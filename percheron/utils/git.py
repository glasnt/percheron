import re
import subprocess
import sys
from rich import print
from datetime import datetime
from pathlib import Path

import git

CODEBASE_FOLDER = "codebase"


def get_repo():
    """Get a pythonic represenatation of the repo"""
    return git.Repo(CODEBASE_FOLDER)


def run_command(cmd):
    cmds = cmd.split()
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
    for c in iter(lambda: process.stdout.read(1), b""):
        sys.stdout.buffer.write(c)


def get_github_repo():
    """Pull a copy of the git repo to local disk, if it doesn't already exist."""
    if Path(CODEBASE_FOLDER).exists():
        print(
            f"Codebase already cloned. To re-clone, delete the folder '{CODEBASE_FOLDER}'."
        )
    else:
        run_command(f"git clone https://github.com/django/django {CODEBASE_FOLDER}")


def get_previous_version(version):
    """For a version of Django, get the previous version"""
    tags = [str(t) for t in get_repo().tags]

    # Scope: most comparisons will be Django releases, which use MAJOR.MINOR, which strictly isn't semver
    # So, we make our own logic.
    major, minor = [int(i) for i in version.split(".")]

    if minor == 0:
        # get the last minor release of the previous major version
        pmajor = major - 1
        pmajor_tags = [
            t
            for t in tags
            if t.startswith(str(pmajor))  # prev major version
            and len(t.split(".")) == 2  # only MAJOR.MINOR
            and t.split(".")[-1].isdigit()  # ignore release candidates
        ]
        prev_version = pmajor_tags[-1]
    else:
        # just decrement the minor version
        prev_version = f"{major}.{minor - 1}"
    return prev_version


def tag_valid(tag):
    """Return true if the tag is a valid tag in the codebase"""
    return tag in get_repo().tags


def get_commits_in_range(start_tag, end_tag):
    """For two tags, get the commits in the range.
    Uses logic from https://noumenal.es/posts/what-is-django-4/zj2/"""
    repo = get_repo()

    start_commit = repo.commit(start_tag)
    end_commit = repo.commit(end_tag)
    merge_base = repo.merge_base(start_commit, end_commit)[0]

    commits = list(repo.iter_commits(str(merge_base) + ".." + str(end_commit)))

    def pretty_commit(commit):
        print(
            "  Author:",
            commit.author,
            "\n  Date:  ",
            datetime.fromtimestamp(commit.authored_date),
            "\n      " + commit.message,
        )

    print("First commit: ")
    pretty_commit(start_commit)
    print("Last commit:")
    pretty_commit(end_commit)
    print(f"Number of commits: {len(commits)}")
    commit_delta = datetime.fromtimestamp(end_commit.authored_date) - datetime.fromtimestamp(start_commit.authored_date)
    print(
        f"Time between commits: {commit_delta.days} days ({str(round(commit_delta.days / 7 / 52 * 12))} months)"
    )
    return commits


def get_git_commits(commits):
    def get_commit(commit):
        git_commits.append(
            {
                "commit_sha": commit.hexsha,
                "datetime": commit.authored_date,
                "author": commit.author.name,
                "author_email": commit.author.email,
                "committer": commit.committer.name,
                "committer_email": commit.committer.email,
                "message": commit.message,
            }
        )

        # Get all ticket references in message
        # NOTE(glasnt): this will include "Fixed", but also "Refs" (which may include older tickets)
        tickets = [x.replace("#", "") for x in re.findall("\#[0-9]*", commit.message)]

        for ticket in tickets:
            if ticket:
                git_trac_links.append(
                    {"commit_sha": commit.hexsha, "trac_ticket_id": ticket}
                )

    git_commits = []
    git_trac_links = []
    tickets = []

    for commit in commits:
        get_commit(commit)

    # Get unique list
    tickets = list(set([k["trac_ticket_id"] for k in git_trac_links]))

    return git_commits, git_trac_links, tickets
