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


def add_protected_file(filename: str, content: str) -> None:
    """Create or overwrite a file inside the protected dir. Filename must be a simple name."""
    require_auth()
    # basic validation: no path separators and simple basename only
    if os.path.sep in filename or (os.path.altsep and os.path.altsep in filename):
        raise PermissionError("Invalid filename")
    if filename != os.path.basename(filename):
        raise PermissionError("Invalid filename")
    full = os.path.abspath(os.path.join(PROTECTED_DIR, filename))
    if not full.startswith(os.path.abspath(PROTECTED_DIR) + os.sep):
        raise PermissionError("Invalid path")
    # write content
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def delete_protected_file(filename: str) -> None:
    """Delete a file inside the protected dir."""
    require_auth()
    if os.path.sep in filename or (os.path.altsep and os.path.altsep in filename):
        raise PermissionError("Invalid filename")
    full = os.path.abspath(os.path.join(PROTECTED_DIR, filename))
    if not full.startswith(os.path.abspath(PROTECTED_DIR) + os.sep):
        raise PermissionError("Invalid path")
    if not os.path.exists(full):
        raise FileNotFoundError(filename)
    os.remove(full)
