from typing import Tuple, List, Dict
from user_store import get_all_users, get_user, upsert_user
from session import session
from logger import log_event
import bcrypt
from typing import Optional
from datetime import datetime, timezone, timedelta
from auth_manager import maybe_trigger_freeze


def require_admin() -> None:
    u = session.get_current_user()
    if not u:
        raise PermissionError("Not logged in")
    user = get_user(u)
    if not user or not user.get("is_admin"):
        raise PermissionError("Admin required")


def reset_password(target_username: str, new_password: str) -> Tuple[bool, str]:
    require_admin()
    user = get_user(target_username)
    if not user:
        return False, "User not found"
    user["password_hash"] = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    upsert_user(user)
    log_event("ADMIN_RESET_PASSWORD", session.get_current_user(), target=target_username)
    return True, "Password reset"


def list_users() -> List[Dict]:
    require_admin()
    db = get_all_users()
    result = []
    for u, rec in db.items():
        result.append({
            "username": u,
            "is_admin": rec.get("is_admin", False),
            "failed_attempts": rec.get("failed_attempts", 0),
            "last_login_at": rec.get("last_login_at")
        })
    log_event("ADMIN_LIST_USERS", session.get_current_user(), count=len(result))
    return result


def unlock_system() -> None:
    require_admin()
    from session import session as sess
    sess.clear_freeze()
    log_event("UNLOCK_MANUAL", session.get_current_user())


def lock_system(seconds: Optional[int] = None) -> Optional[int]:
    """Manually lock the system (freeze). If seconds is None use default freeze seconds via maybe_trigger_freeze()."""
    require_admin()
    if seconds is None:
        return maybe_trigger_freeze()
    until = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    from session import session as sess
    sess.freeze_until(until.isoformat())
    log_event("LOCK_MANUAL", session.get_current_user(), seconds=seconds)
    return seconds


def set_user_locked_until(username: str, iso_ts: str | None) -> None:
    require_admin()
    user = get_user(username)
    if not user:
        raise ValueError("User not found")
    user["locked_until"] = iso_ts
    upsert_user(user)
