import json
import os
from core.utils import log_event

DATA_FILE = "data/users.json"

def initialize_storage():
    """Ensures data folder and user file exist."""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
        log_event("Initialized user storage.")

def load_users() -> dict:
    """Loads user database."""
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users: dict):
    """Saves user database."""
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)
