import json
from config import LOG_PATH


def read_events() -> list[dict]:
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return []


def summarize_events(events: list[dict]) -> dict:
    summary = {
        "logins": 0,
        "failed_attempts": 0,
        "freeze_events": 0,
        "last_login_per_user": {}
    }
    for e in events:
        event = e.get("event")
        if event == "LOGIN_SUCCESS":
            summary["logins"] += 1
            u = e.get("username")
            if u:
                summary["last_login_per_user"][u] = e.get("ts")
        elif event == "LOGIN_FAIL":
            summary["failed_attempts"] += 1
        elif event in ("FREEZE_ON", "FREEZE_OFF"):
            summary["freeze_events"] += 1
    return summary


def print_console_dashboard(summary: dict) -> None:
    print("\n=== Activity Summary ===")
    print(f"Logins: {summary['logins']}")
    print(f"Failed Attempts: {summary['failed_attempts']}")
    print(f"Freeze Events: {summary['freeze_events']}")
    print("Last Login Per User:")
    for u, ts in summary["last_login_per_user"].items():
        print(f" - {u}: {ts}")
