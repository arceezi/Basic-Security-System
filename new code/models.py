from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    username: str
    password_hash: str
    is_admin: bool = False
    failed_attempts: int = 0
    last_login_at: Optional[str] = None
    locked_until: Optional[str] = None
    created_at: Optional[str] = None
    password_changed_at: Optional[str] = None

@dataclass
class Session:
    current_user: Optional[str] = None
    is_frozen_until: Optional[str] = None
