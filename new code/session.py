from datetime import datetime, timezone
from typing import Optional
import atexit
from active_sessions import add_active_session, remove_active_session, update_active_session, is_user_active

class SessionManager:
    def __init__(self):
        self.current_user: Optional[str] = None
        self.is_frozen_until: Optional[str] = None
        atexit.register(self.cleanup)

    def get_current_user(self) -> Optional[str]:
        if self.current_user:
            update_active_session(self.current_user)
        return self.current_user
    
    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def can_login(self, username: str) -> bool:
        """Check if a user can log in (not already logged in elsewhere)"""
        return not is_user_active(username)

    def login(self, username: str) -> None:
        if not self.can_login(username):
            raise PermissionError("User already logged in")
        self.current_user = username
        add_active_session(username)

    def logout(self) -> None:
        if self.current_user:
            remove_active_session(self.current_user)
        self.current_user = None
    
    def cleanup(self):
        """Ensure we remove our session on exit"""
        if self.current_user:
            remove_active_session(self.current_user)

    def freeze_until(self, iso_ts: str) -> None:
        self.is_frozen_until = iso_ts

    def is_frozen(self) -> bool:
        if not self.is_frozen_until:
            return False
        try:
            return datetime.now(timezone.utc) < datetime.fromisoformat(self.is_frozen_until)
        except Exception:
            return False

    def clear_freeze(self) -> None:
        self.is_frozen_until = None

# global session (simple singleton for the skeleton)
session = SessionManager()
