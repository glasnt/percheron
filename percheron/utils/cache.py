
from requests_cache import CachedSession
import click

from rich import print

def session(): 
    # Note: POST may be ignored by default! So ensure we cache that. 
    return CachedSession('cache/api_cache', backend='sqlite', allowable_methods=('GET', 'POST'))


def request_limit_reached(message, uri=None): 
    print(f"An issue has occured: [bold]{message}[/bold].")
    if "search" in uri:
        print("This issue occured using the GitHub Search API. This API has a notoriously slow API limit. Try again soon.")
    
    raise SystemExit()
