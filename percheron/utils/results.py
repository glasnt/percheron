from collections import Counter
import json
from rich import print
from rich.table import Table

RESULTS_FOLDER = "data"

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

def save_to_json(data): 
    # TODO make folder if doesn't exist.
    for fn in data.keys():
        json_fn = f"{RESULTS_FOLDER}/{fn}.json"
        with open(json_fn, "w") as f:
            f.write(json.dumps(data[fn]))
            print(f"Wrote data to {json_fn}")
    