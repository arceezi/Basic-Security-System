import json
import os
from datetime import datetime, timezone
from config import LOG_PATH

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def log_event(event: str, username: str | None = None, **meta):
    line = {"ts": _now_iso(), "event": event}
    if username:
        line["username"] = username
    if meta:
        line["meta"] = meta
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")
