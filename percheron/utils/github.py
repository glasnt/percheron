import time

from datetime import datetime
from tqdm import tqdm
from percheron.utils import cache, results
from percheron.utils.helpers import unique
from percheron import config


def github_api(uri):
    """For a GitHub API path, return the JSON data"""

    session = cache.session()
    resp = session.get(
        "https://api.github.com" + uri,
        headers={
            "Authorization": f"Bearer {config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
    )

    if resp.status_code == 404:
        raise ValueError(resp.json()["message"])

    if resp.status_code != 200:
        message = resp.json()["message"]
        rate_limit_context()
        cache.request_limit_reached(message, uri=uri)

    return resp.json()


def search_for_pull_requests(ticket_id):
    """For a ticket ID, search for related pull requests,
    based on the system trac uses"""
    data = github_api(
        "/search/issues?q=repo:django/django+in:title+type:pr+"
        + "%23"
        + ticket_id
        + "%20"
        + "+%23"
        + ticket_id
        + "%2C"
        + "+%23"
        + ticket_id
        + "%3A"
        + "+%23"
        + ticket_id
        + "%29"
    )["items"]

    return [x["number"] for x in data]


def get_pull_request(pr_id):
    """For a given pull request ID, get the minimum data from the github API"""
    data = github_api(f"/repos/django/django/pulls/{pr_id}")

    pr = {
        "id": data["number"],
        "state": data["state"],
        "user": data["user"]["login"],
    }

    return pr


def get_comments_from_pull_request(pull_request_id):
    """For a pull request ID, get the comments"""
    comments = []

    # Comments
    data = github_api(f"/repos/django/django/pulls/{pull_request_id}/comments")

    for record in data:
        comments.append(
            {
                "user": record["user"]["login"],
                "commit_id": record["commit_id"],
                "message": record["body"],
                "pull_request": pull_request_id,
            }
        )

    # Review Comments
    data = github_api(f"/repos/django/django/issues/{pull_request_id}/comments")

    for record in data:
        comments.append(
            {
                "user": record["user"]["login"],
                "commit_id": None,
                "message": record["body"],
                "pull_request": pull_request_id,
            }
        )

    return comments


def get_github_data(tickets):

    pull_request_ids = []
    pull_requests = []
    trac_pr_links = []

    print("Getting Pull Requests that are mentioned in tickets...")
    for ticket_no in tqdm(tickets):
        prs_for_ticket = search_for_pull_requests(ticket_no)

        for pr in prs_for_ticket:
            trac_pr_links.append({"ticket_id": ticket_no, "pull_request": str(pr)})
        
        pull_request_ids += prs_for_ticket

    pull_request_ids = list(set(pull_request_ids))

    print("Getting information about those Pull Requests...")
    for pr_id in tqdm(pull_request_ids):
        pull_requests.append(get_pull_request(pr_id))

    pr_comments = []

    print("Getting comments from those Pull Requests...")
    for request in tqdm(pull_requests):
        pr_comments += get_comments_from_pull_request(request["id"])

    results.save_to_disk(pull_requests)
    results.save_to_disk(pr_comments)
    results.save_to_disk(trac_pr_links)

    return pull_requests, pr_comments


def rate_limit_context():
    """For a GitHub API path, return the JSON data"""

    session = cache.session()

    with session.cache_disabled():
        resp = session.get(
            "https://api.github.com/rate_limit",
            headers={
                "Authorization": f"Bearer {config.GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3.raw",
            },
        )
    if "message" in resp.json().keys():
        print(resp.json())
    else:
        data = resp.json()["resources"]

        if (
            "X-RateLimit-Remaining" in resp.headers
            and resp.headers["X-RateLimit-Remaining"] == 0
        ):
            wait_seconds = int(resp.headers.get("x-ratelimit-reset")) - int(time.time())
            wait_minutes = int(wait_seconds / 60)
            message += f"\nRate limit expired. Wait {wait_minutes} minutes (or {wait_seconds} seconds)."

        for limit_type in ["core", "search"]:
            d = data[limit_type]
            reset = datetime.fromtimestamp(d["reset"])
            print(
                f"GitHub {limit_type} API limit: {d['used']}/{d['limit']} resets at {reset} ({reset.second} seconds)"
            )


def get_github_user(user):
    """For a GitHub username, get their name.
    NOTE(glasnt): debugging details have been added here to work out source of
    missing data, rather than trying to use None or N/A, etc.
    """
    try:
        data = github_api(f"/users/{user}")
    except ValueError:
        # this is okay
        return user
    if data["name"] == None:
        # This is ok
        return user
    return data["name"].strip()


def get_github_users(users):
    """For a list of users, get their GitHub name"""
    github_name = {}
    github_userdata = []
    for user in tqdm(unique(users)):
        name = get_github_user(user)

        github_name[user] = name
        github_userdata.append({"name": name, "username": user })

    results.save_to_disk(github_userdata)

    return github_name
