import rich_click as click
import rich
from rich import print
from percheron.utils import git, trac, github, nlp, config, results

def header(str): 
    """Print a formatted header"""
    print(rich.rule.Rule())
    print(f"[bold]{str}[/bold]")


@click.group()
@click.version_option()
def cli():
    pass


@cli.command(name="get")
@click.argument(
    "version"
)
@click.option(
    "-o",
    "--option",
    help="An example option",
)
def get(version, option):
    """Get contributors for a release of Django"""

    issue = config.validate_configuration()
    if issue:
        print(f"[red]An issue has occured:\n  [bold]{issue}[/bold]\nCannot continue.[/red]")
        click.Context.exit(1)

    print(rich.markdown.Markdown(f"# percheron processing Django {version}"))

    header(":down_arrow: Download django codebase")
    git.get_github_repo()

    header(":thought_balloon: Determine range of calculations")
    prev_version = git.get_previous_version(version)
    if not git.tag_valid(prev_version):
        print(f"❌ Previous version [bold]{prev_version}[/bold] isn't a valid tag. Exiting.")
        click.Context.exit(1)
    
    print(f"Searching for Django contributors between {prev_version} and {version}")
    commits = git.get_commits_in_range(start_tag=prev_version, end_tag=version)

    header(f":flashlight: Getting data from local Git clone")
    git_commits, git_trac_links, tickets = git.get_git_commits(commits)
    print("Git Commits:", len(git_commits))
    print("Git Trac Links:", len(git_trac_links))
    print("Tickets:", len(tickets))


    header(f":railway_track: Getting data from Trac")
    trac_tickets, trac_ticket_comments = trac.get_trac_tickets(tickets)
    print("Trac Tickets:", len(trac_tickets))
    print("Trac Ticket Comments:", len(trac_ticket_comments))


    header(f":octopus: Getting data from github")
    pull_requests, pr_comments = github.get_github_data(tickets)
    print("Pull requests:", len(pull_requests))
    print("Pull Request Comments:", len(pr_comments))

    header(f":detective: Parsing commit messages for 'Thanks'")
    nlp.install_nltk_data()
    thanks = nlp.get_thanks(commits)
    print(f"People thanked: {len(thanks)}")

    data = {"git_commits": git_commits, "git_trac_links": git_trac_links, "tickets": tickets, 
        "trac_tickets": trac_tickets, "trac_ticket_comments": trac_ticket_comments,  "pull_requests": pull_requests, "pr_comments": pr_comments, "thanks": thanks  }

    results.save_to_json(data)

    print(rich.markdown.Markdown(f"# Data collected.\nYou can now start analysing the data."))

