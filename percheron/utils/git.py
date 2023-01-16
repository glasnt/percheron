import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import git
from rich import print

from percheron import config
from percheron.utils import results
from percheron.utils.helpers import unique


def run_command(cmd):
    cmds = cmd.split()
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
    for c in iter(lambda: process.stdout.read(1), b""):
        sys.stdout.buffer.write(c)


def get_django_repo():
    get_github_repo(codebase=config.DJANGO_PROJECT, clone_fn=config.DJANGO_REPO)


def get_translations_repo(version):
    get_github_repo(
        codebase=config.TRANSLATIONS_PROJECT,
        clone_fn=config.TRANSLATIONS_REPO,
        branch=f"stable/{version}.x",
    )


def get_github_repo(codebase, clone_fn, branch=None):
    """Pull a copy of the git repo to local disk, if it doesn't already exist.
    Optionally only clone a specific branch in question (saves time/diskspace)"""

    if Path(clone_fn).exists():
        print(f"Codebase already cloned. To re-clone, delete the folder '{clone_fn}'.")
    else:
        branch_filter = f"-b {branch}" if branch else ""
        run_command(
            f"git clone {branch_filter} https://github.com/django/{codebase} {str(clone_fn)}"
        )


def get_previous_version(version):
    """For a version of Django, get the previous version"""
    tags = [str(t) for t in git.Repo(config.DJANGO_REPO).tags]

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
    return tag in git.Repo(config.DJANGO_REPO).tags


def get_commits_in_range(start_tag, end_tag):
    """For two tags, get the commits in the range.
    Uses logic from https://noumenal.es/posts/what-is-django-4/zj2/"""
    repo = git.Repo(config.DJANGO_REPO)

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
    commit_delta = datetime.fromtimestamp(
        end_commit.authored_date
    ) - datetime.fromtimestamp(start_commit.authored_date)
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
        tickets = [x.replace("#", "") for x in re.findall("#[0-9]*", commit.message)]

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

    results.save_to_disk(git_commits)
    results.save_to_disk(git_trac_links)
    

    return git_commits, git_trac_links, tickets


def get_translators(version):
    """Get translators for version of Django

    NOTE: the logic within here is based on the limitation that we
    parse the translation file headers for committers for the current year

    If functionality within Transifex is found, this can be used instead.
    """
    translations = config.TRANSLATIONS_REPO

    # Using the version as a tag, get the current year for the Django (not translations) repo
    last_commit = git.Repo(config.DJANGO_REPO).commit(version)
    year = datetime.fromtimestamp(last_commit.committed_date).year

    # Check all the translations headers for people from the year
    people = []

    for file in translations.glob("**/*.po"):
        with open(file) as f:
            for line in f.readlines():
                if re.search(f"^#(.*), (.*){year}(.*)", line):
                    people.append(line.split(",")[0])

    # cleanup data
    for i, author in enumerate(people):
        people[i] = author.replace("#", "").strip().split("<")[0]

    people = unique(people)

    # save translators to file
    translators = [{"name": name} for name in people]
    results.save_to_disk(translators)

    return people
