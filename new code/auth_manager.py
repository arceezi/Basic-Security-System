from __future__ import annotations
from typing import Tuple, Optional
from datetime import datetime, timezone, timedelta

import bcrypt

from config import (
    LOCKOUT_MAX_ATTEMPTS,
    SYSTEM_FREEZE_SECONDS,
    AUTO_UNLOCK_SECONDS,  # used as the per-user lock duration too (can separate if you want)
)
from user_store import get_user, upsert_user, get_all_users
from session import session
from logger import log_event


# -------- time helpers --------
def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().isoformat()


def _parse_iso(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


# -------- public API --------
def register_user(username: str, password: str, is_admin: bool = False) -> Tuple[bool, str]:
    """
    Create a new user with bcrypt-hashed password.
    Returns (ok, message).
    """
    if not username or not password:
        return False, "Username and password required"

    db = get_all_users()
    if username in db:
        return False, "User already exists"

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = {
        "username": username,
        "password_hash": pw_hash,
        "is_admin": is_admin,
        "failed_attempts": 0,
        "last_login_at": None,
        "locked_until": None,
        "created_at": _now_iso(),
        "password_changed_at": _now_iso(),
    }
    upsert_user(user)
    log_event("REGISTER_SUCCESS", username)
    return True, "User created"


def authenticate(username: str, password: str) -> Tuple[bool, str]:
    """
    Attempt login with full lock/freeze handling.
    Returns (ok, message-for-UI).
    """
    # 1) Clear any expired locks/freezes first
    _auto_unlock_system_if_due()
    _auto_unlock_user_if_due(username)

    # 2) Block if system is frozen
    if is_system_frozen():
        return False, _freeze_message()

    # 3) Get user and block if specifically locked
    user = get_user(username)
    if not user:
        log_event("LOGIN_FAIL", username, reason="no_such_user")
        # we do NOT increment failed_attempts for non-existent users
        return False, "Invalid credentials"

    # Per-user lock check
    if _is_user_locked(user):
        remain = user_lock_remaining_seconds(user)
        return False, f"Account temporarily locked. Try again in {remain}s."

    # 4) Verify password
    ok = bcrypt.checkpw(password.encode(), user["password_hash"].encode())
    if ok:
        user["failed_attempts"] = 0
        user["last_login_at"] = _now_iso()
        upsert_user(user)
        session.login(username)
        log_event("LOGIN_SUCCESS", username)
        return True, "Login successful"

    # 5) Handle failure: bump attempts, warn/lock/freeze
    attempts = int(user.get("failed_attempts", 0)) + 1
    user["failed_attempts"] = attempts
    upsert_user(user)

    log_event("LOGIN_FAIL", username, attempt=attempts)

    # Warning if about to hit lockout
    if attempts == LOCKOUT_MAX_ATTEMPTS - 1:
        left = attempts_left(username)
        log_event("LOCK_WARN", username, attempts=attempts, attempts_left=left)
        return False, f"Invalid credentials. Final attempt remaining (1 of {LOCKOUT_MAX_ATTEMPTS})."

    # Lock + system freeze on reaching threshold
    if attempts >= LOCKOUT_MAX_ATTEMPTS:
        _lock_user(user, seconds=AUTO_UNLOCK_SECONDS)
        freeze_secs = maybe_trigger_freeze()  # system-wide
        msg = "Too many attempts. "
        if freeze_secs:
            msg += f"System frozen for {freeze_secs}s. "
        msg += f"Your account is locked for {AUTO_UNLOCK_SECONDS}s."
        return False, msg

    # Generic failure message with attempts left
    left = attempts_left(username)
    return False, f"Invalid credentials. Attempt {attempts} of {LOCKOUT_MAX_ATTEMPTS} ({left} left)."


def logout() -> None:
    u = session.get_current_user()
    session.logout()
    if u:
        log_event("LOGOUT", u)


def is_system_frozen() -> bool:
    return session.is_frozen()


def maybe_trigger_freeze() -> Optional[int]:
    """
    Start a system-wide freeze window and log it.
    Returns the number of seconds frozen (for UI), or None if already frozen.
    """
    # If already frozen, do nothing but report remaining
    if session.is_frozen():
        return freeze_remaining_seconds()

    seconds = SYSTEM_FREEZE_SECONDS
    until = _now() + timedelta(seconds=seconds)
    session.freeze_until(until.isoformat())
    log_event("FREEZE_ON", None, seconds=seconds)
    return seconds


def attempts_left(username: str) -> int:
    user = get_user(username)
    if not user:
        return LOCKOUT_MAX_ATTEMPTS
    return max(0, LOCKOUT_MAX_ATTEMPTS - int(user.get("failed_attempts", 0)))


def freeze_remaining_seconds() -> Optional[int]:
    """
    Returns remaining frozen seconds for the system, or None if not frozen.
    """
    if not session.is_frozen_until:
        return None
    target = _parse_iso(session.is_frozen_until)
    if not target:
        return None
    delta = (target - _now()).total_seconds()
    return int(delta) if delta > 0 else None


def user_lock_remaining_seconds(user_or_username) -> Optional[int]:
    """
    Returns remaining seconds for the user's own lock, or None if not locked.
    Accepts user dict or username.
    """
    user = user_or_username if isinstance(user_or_username, dict) else get_user(user_or_username)
    if not user:
        return None
    target = _parse_iso(user.get("locked_until"))
    if not target:
        return None
    delta = (target - _now()).total_seconds()
    return int(delta) if delta > 0 else None


# -------- internal helpers --------
def _freeze_message() -> str:
    remain = freeze_remaining_seconds()
    if remain is None:
        # If time parsing failed, still block with generic text
        return "System is frozen. Try again later or contact admin."
    return f"System is frozen. Try again in {remain}s or contact admin."


def _is_user_locked(user: dict) -> bool:
    target = _parse_iso(user.get("locked_until"))
    return bool(target and _now() < target)


def _lock_user(user: dict, seconds: int) -> None:
    until = _now() + timedelta(seconds=seconds)
    user["locked_until"] = until.isoformat()
    upsert_user(user)
    log_event("USER_LOCK_ON", user["username"], seconds=seconds)


def _unlock_user(user: dict) -> None:
    if user.get("locked_until"):
        user["locked_until"] = None
        upsert_user(user)
        log_event("USER_LOCK_OFF", user["username"])


def _auto_unlock_user_if_due(username: str) -> None:
    """
    If this user exists and has an expired lock, clear it and log.
    """
    user = get_user(username)
    if not user:
        return
    if not user.get("locked_until"):
        return
    target = _parse_iso(user["locked_until"])
    if not target:
        # Invalid timestamp; best effort: clear lock
        user["locked_until"] = None
        upsert_user(user)
        log_event("USER_LOCK_OFF", username, reason="invalid_timestamp")
        return
    if _now() >= target:
        _unlock_user(user)


def _auto_unlock_system_if_due() -> None:
    """
    If the system-wide freeze has expired, clear and log.
    """
    if not session.is_frozen():
        return
    target = _parse_iso(session.is_frozen_until)
    if not target:
        session.clear_freeze()
        log_event("FREEZE_OFF", None, reason="invalid_timestamp")
        return
    if _now() >= target:
        session.clear_freeze()
        log_event("FREEZE_OFF")


def bootstrap_admin(default_password: str = "admin123") -> None:
    """
    Ensure an 'admin' account exists. Idempotent: does nothing if admin already exists.
    """
    db = get_all_users()
    if "admin" in db:
        return

    pw_hash = bcrypt.hashpw(default_password.encode(), bcrypt.gensalt()).decode()
    user = {
        "username": "admin",
        "password_hash": pw_hash,
        "is_admin": True,
        "failed_attempts": 0,
        "last_login_at": None,
        "locked_until": None,
        "created_at": _now_iso(),
        "password_changed_at": _now_iso(),
    }
    upsert_user(user)
    log_event("REGISTER_SUCCESS", "admin", bootstrap=True)
