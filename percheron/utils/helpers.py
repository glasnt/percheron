"""
Generic helpers for various things. 
"""

import inspect


def flatten(l):
    """For a nested list, flatten it to be one dimention."""
    return [item for sublist in l for item in sublist]


def unique(l):
    """For a list of items, return only the unique values."""

    l = list(filter(lambda i: i is not None, l))
    l = [a.strip() for a in l]
    return sorted(list(set(l)), key=str.casefold)


def retrieve_name(var):
    """
    This is awful https://stackoverflow.com/a/40536047
    """
    for fi in reversed(inspect.stack()):
        names = [
            var_name
            for var_name, var_val in fi.frame.f_locals.items()
            if var_val is var
        ]
        if len(names) > 0:
            return names[0]


def convert_lookup_to_data(github_name):
    # original format: github_name[user] = get_github_user(user)

    # flip it
    github_user = {v: k for k, v in github_name.items()}

    # list it
    github_user_data = [{"user": k, "name": v} for k, v in github_name.items()]
    return github_user, github_user_data
