import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from rich import print
from rich.console import Console
from rich.table import Table

from percheron import config
from percheron.utils.helpers import unique

OUTPUT_REPORT = Path(config.REPORT_FOLDER) / "percheron_report.txt"
OUTPUT_LIST = Path(config.REPORT_FOLDER) / "percheron_list.txt"
OUTPUT_CSV = Path(config.REPORT_FOLDER) / "percheron_report.csv"


def print_table(
    table_name="Table", columns=["a", "b"], data=[[1, 2], [3, 4]], limit=None
):
    table = Table(title=table_name)
    for col in columns:
        table.add_column(col)
    if limit:
        data = data[:limit]
        table.title += f" (limit {limit})"
    for x in data:
        table.add_row(*list([str(y) for y in x]))
    print(table)


def load_from_json(data_fn):
    """Load data from file"""
    json_fn = f"{config.DATA_FOLDER}/{data_fn}.json"
    with open(json_fn) as f:
        data = json.load(f)
    return data


def table_data(data_source):
    data = load_from_json(data_source)
    breakpoint()
    gc_authors = Counter([g["author"] for g in data])
    print_table(
        "Git Committers", ["Name", "Commits"], gc_authors.most_common(), limit=10
    )


def generate_report(
    version,
    git_commits,
    pull_requests,
    pr_comments,
    trac_tickets,
    trac_ticket_comments,
    thanks,
    translators,
    github_user,
    github_name,
):
    Path(config.REPORT_FOLDER).mkdir(parents=True, exist_ok=True)

    contrib_array = {"g": 0, "pr": 0, "prc": 0, "ttr": 0, "ttc": 0, "st": 0, "tt": 0}

    contributors = {}

    def merge_contrib(records, key):
        for g in records:
            user, num = g
            if not user in contributors.keys():
                contributors[user] = contrib_array.copy()
            contributors[user][key] = num

    gc = Counter(
        [github_user.get(g["author"], g["author"]) for g in git_commits]
    ).most_common()
    merge_contrib(gc, "g")

    prc = Counter([g["user"] for g in pull_requests]).most_common()
    merge_contrib(prc, "pr")

    prcsc = Counter([g["user"] for g in pr_comments]).most_common()
    merge_contrib(prcsc, "prc")

    ttrc = Counter([g["reporter"] for g in trac_tickets]).most_common()
    merge_contrib(ttrc, "ttr")

    ttcc = Counter(
        [github_user.get(g["name"], g["name"]) for g in trac_ticket_comments]
    ).most_common()
    merge_contrib(ttcc, "ttc")

    stc = Counter([github_user.get(g, g) for g in thanks]).most_common()
    merge_contrib(stc, "st")

    ttc = Counter([github_user.get(g, g) for g in translators]).most_common()
    merge_contrib(ttc, "tt")

    contributors

    table = Table(title=f"Contributions to Django {version}")

    with open(OUTPUT_CSV, "w") as f:
        writer = csv.writer(f)

        columns = [
            "Name",
            "User",
            "Commits",
            "PRs",
            "PR Comments",
            "Trac Tickets",
            "Trac Comments",
            "Security",
            "Translations",
        ]
        for col in columns:
            table.add_column(col)

        writer.writerow(columns)

        for c in contributors:
            name = github_name.get(c, c)
            data = [str(s[1]) for s in contributors[c].items()]
            table.add_row(c, name, *data)
            writer.writerow([c, name, *data])

    with open(OUTPUT_REPORT, "w") as f:
        console = Console(file=f)
        console.print(table)
        console.rule(f"Report Generated {datetime.now().ctime()}")

    # Generate a displayable name for the list report
    django_contributors = []
    for c in unique(contributors.keys()):
        name = github_name.get(c, None)
        if name is not None and name != c:
            display_name = f"{name} ({c})"
        else:
            display_name = c
        django_contributors.append(display_name)

    django_contributors = unique(django_contributors)

    with open(OUTPUT_LIST, "w") as f:
        f.write(f"Contributors to Django {version}: {len(django_contributors)}")
        f.write("\n".join(django_contributors))
