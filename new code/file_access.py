import os
from typing import List
from config import PROTECTED_DIR
from session import session

os.makedirs(PROTECTED_DIR, exist_ok=True)


def require_auth() -> None:
    if session.is_frozen():
        raise PermissionError("System is frozen")
    if not session.is_authenticated():
        raise PermissionError("Not logged in")


def list_protected_files() -> List[str]:
    require_auth()
    return [f for f in os.listdir(PROTECTED_DIR) if os.path.isfile(os.path.join(PROTECTED_DIR, f))]


def open_protected_file(filename: str) -> str:
    require_auth()
    full = os.path.abspath(os.path.join(PROTECTED_DIR, filename))
    if not full.startswith(os.path.abspath(PROTECTED_DIR) + os.sep):
        raise PermissionError("Invalid path")
    with open(full, "r", encoding="utf-8") as f:
        return f.read()
