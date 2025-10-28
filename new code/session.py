from datetime import datetime, timezone
from typing import Optional

class SessionManager:
    def __init__(self):
        self.current_user: Optional[str] = None
        self.is_frozen_until: Optional[str] = None

    def get_current_user(self) -> Optional[str]:
        return self.current_user

    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def login(self, username: str) -> None:
        self.current_user = username

    def logout(self) -> None:
        self.current_user = None

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
