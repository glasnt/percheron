import rich_click as click
import rich
from rich import print
from percheron.utils import git

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

    print(f"Getting information for [pink1]Django {version}[/pink1]")
    print("⬇️  Download Django codebase")
    git.get_github_repo()

    print("💭 Determine range of calculations")
    prev_version = git.get_previous_version(version)
    if not git.tag_valid(prev_version):
        print(f"❌ Previous version [bold]{prev_version}[/bold] isn't a valid tag. Exiting.")
        click.Context.exit(1)
    
    print(f"🔎 Searching for Django contributors between {prev_version} and {version}")
    commits = git.get_commits_in_range(start_tag=prev_version, end_tag=version)
    
