import json
from pathlib import Path

from sqlite_utils import Database

from percheron import config
from percheron.utils.helpers import retrieve_name

OUTPUT_DB = Path(config.DATA_FOLDER) / "percheron_data.db"


def datasette_init():
    """Initialise the datasette database"""
    Path(config.DATA_FOLDER).mkdir(parents=True, exist_ok=True)
    Database(OUTPUT_DB, recreate=True)


def save_to_disk(data):
    """For a list of dictionaries, save the results to a JSON file, and append to datasette"""

    fn = retrieve_name(data)  # Sorry

    json_fn = f"{config.DATA_FOLDER}/{fn}.json"
    with open(json_fn, "w") as f:
        f.write(json.dumps(data, indent=2))
        print(f"Wrote data to {json_fn}")

    Database(OUTPUT_DB)[fn].insert_all(data)
