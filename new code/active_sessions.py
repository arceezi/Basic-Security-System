import json
import os
import msvcrt
from typing import Optional, Dict
from datetime import datetime, timezone
from config import ACTIVE_SESSIONS_PATH

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _cleanup_stale_sessions(sessions: Dict) -> Dict:
    """Remove sessions older than 5 minutes (suggesting crashed instances)"""
    now = datetime.now(timezone.utc)
    cutoff = 300  # 5 minutes in seconds
    return {
        username: data for username, data in sessions.items()
        if data and datetime.fromisoformat(data["last_active"]).timestamp() + cutoff > now.timestamp()
    }

def _acquire_lock(file_handle) -> None:
    """Lock the file for exclusive access"""
    while True:
        try:
            # Try to lock the entire file
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
            break
        except IOError:
            # Another process has the lock, wait a bit and retry
            import time
            time.sleep(0.1)

def _release_lock(file_handle) -> None:
    """Release the lock on the file"""
    try:
        # Unlock the file
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
    except IOError:
        pass  # Ignore errors during unlock

def get_active_sessions() -> Dict:
    """Get dictionary of active user sessions with locking"""
    if not os.path.exists(ACTIVE_SESSIONS_PATH):
        return {}
        
    try:
        with open(ACTIVE_SESSIONS_PATH, "r+b") as f:
            _acquire_lock(f)
            try:
                f.seek(0)
                content = f.read().decode("utf-8")
                sessions = json.loads(content or "{}")
                sessions = _cleanup_stale_sessions(sessions)
                # Write back cleaned sessions
                f.seek(0)
                f.truncate()
                f.write(json.dumps(sessions).encode("utf-8"))
                return sessions
            finally:
                _release_lock(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        return {}

def is_user_active(username: str) -> bool:
    """Check if a user has an active session"""
    return bool(get_active_sessions().get(username))

def add_active_session(username: str) -> None:
    """Add/update a user's active session with locking"""
    os.makedirs(os.path.dirname(ACTIVE_SESSIONS_PATH), exist_ok=True)
    
    # Ensure file exists
    if not os.path.exists(ACTIVE_SESSIONS_PATH):
        with open(ACTIVE_SESSIONS_PATH, "wb") as f:
            f.write(b"{}")
    
    with open(ACTIVE_SESSIONS_PATH, "r+b") as f:
        _acquire_lock(f)
        try:
            f.seek(0)
            content = f.read().decode("utf-8")
            sessions = json.loads(content or "{}")
            sessions = _cleanup_stale_sessions(sessions)
            sessions[username] = {
                "pid": os.getpid(),
                "last_active": _now_iso()
            }
            f.seek(0)
            f.truncate()
            f.write(json.dumps(sessions).encode("utf-8"))
        finally:
            _release_lock(f)

def remove_active_session(username: str) -> None:
    """Remove a user's active session with locking"""
    if not os.path.exists(ACTIVE_SESSIONS_PATH):
        return
        
    with open(ACTIVE_SESSIONS_PATH, "r+b") as f:
        _acquire_lock(f)
        try:
            f.seek(0)
            content = f.read().decode("utf-8")
            sessions = json.loads(content or "{}")
            if username in sessions:
                del sessions[username]
            f.seek(0)
            f.truncate()
            f.write(json.dumps(sessions).encode("utf-8"))
        finally:
            _release_lock(f)

def update_active_session(username: str) -> None:
    """Update last_active timestamp for a session"""
    if is_user_active(username):
        add_active_session(username)  # This will update the timestamp