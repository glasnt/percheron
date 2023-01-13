import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from rich import print
from rich.console import Console
from rich.table import Table
from sqlite_utils import Database

from percheron.utils.helpers import retrieve_name, unique

RESULTS_FOLDER = "data"
OUTPUT_DB = "percheron_data.db"
OUTPUT_REPORT = "percheron_report.txt"
OUTPUT_LIST = "percheron_list.txt"

def print_table(table_name="Table", columns=["a", "b"], data=[[1,2],[3,4]], limit=None):
    table = Table(title=table_name)
    for col in columns:
        table.add_column(col)
    if limit:
        data = data[:limit]
        table.title += f" (limit {limit})"
    for x in data:
        table.add_row(*list([str(y) for y in x]))
    print(table)


def table_data(data_source): 
    data = load_from_json(data_source)
    breakpoint()
    gc_authors = Counter([g["author"] for g in data])
    print_table("Git Committers", ["Name", "Commits"], gc_authors.most_common(), limit=10)


def load_from_json(data_fn):
    json_fn = f"{RESULTS_FOLDER}/{data_fn}.json"
    with open(json_fn) as f:
        data = json.load(f)
    return data

def save_to_disk(data_sets):
    Path(RESULTS_FOLDER).mkdir(parents=True, exist_ok=True)

    db = Database(OUTPUT_DB, recreate=True)

    for data in data_sets:
        # Sorry
        fn = retrieve_name(data)

        json_fn = f"{RESULTS_FOLDER}/{fn}.json"
        with open(json_fn, "w") as f:
            f.write(json.dumps(data, indent=2))
            print(f"Wrote data to {json_fn}")
            
        # Some data is flat, so make it a bit more beefy
        if type(data) == list and type(data[0]) == str:
            data = [{"name": s} for s in data]

        db[fn].insert_all(data)


def generate_report(version, git_commits, pull_requests, pr_comments, trac_tickets, trac_ticket_comments, thanks, translators, github_user, github_name):
    contrib_array = {"g": 0, "pr": 0, "prc": 0, "ttr": 0, "ttc": 0, "st": 0, "tt": 0}

    contributors = {}

    def merge_contrib(records, key):
        for g in records:
            user, num = g
            if not user in contributors.keys():
                contributors[user] = contrib_array.copy()
            contributors[user][key] = num
        

    gc = Counter([github_user.get(g["author"], g["author"]) for g in git_commits]).most_common()
    merge_contrib(gc, "g")
        
    prc = Counter([g["user"] for g in pull_requests]).most_common()
    merge_contrib(prc, "pr")

    prcsc = Counter([g["user"] for g in pr_comments]).most_common()
    merge_contrib(prcsc, "prc")

    ttrc = Counter([g["reporter"] for g in trac_tickets]).most_common()
    merge_contrib(ttrc, "ttr")

    ttcc = Counter([github_user.get(g["name"], g["name"]) for g in trac_ticket_comments]).most_common()
    merge_contrib(ttcc, "ttc")

    stc = Counter([github_user.get(g, g) for g in thanks]).most_common()
    merge_contrib(stc, "st")

    ttc = Counter([github_user.get(g, g) for g in translators]).most_common()
    merge_contrib(ttc, "tt")
        
    contributors

    table = Table(title=f"Contributions to Django {version}")
    for col in ["Name", "User", "Commits", "PRs", "PR Comments", "Trac Tickets", "Trac Comments", "Security", "Translations"]:
        table.add_column(col)

    for c in contributors:
        table.add_row(c, github_name.get(c, c), *[str(s[1]) for s in contributors[c].items()] )

    with open(OUTPUT_REPORT, "w") as f:
        console = Console(file=f)
        console.print(table)
        console.rule(f"Report Generated {datetime.now().ctime()}")

    django_contributors = unique([github_name.get(g, g) for g in unique(contributors.keys())])
    with open(OUTPUT_LIST, "w") as f:
        f.write(f"Contributors to Django {version}: {len(django_contributors)}")
        f.write("\n".join(django_contributors))