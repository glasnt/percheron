from dotenv import load_dotenv
import os

load_dotenv()


def validate_configuration():
    """Confirm settings before things start."""
    if "GITHUB_TOKEN" not in os.environ.keys():
        return "GITHUB_TOKEN is not defined. You will have problems later."
