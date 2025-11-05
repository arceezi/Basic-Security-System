import os

# Compute project base dir (parent of this file) so paths work independent of cwd.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

LOCKOUT_MAX_ATTEMPTS = 5
SYSTEM_FREEZE_SECONDS = 60
AUTO_UNLOCK_SECONDS = 180
# Data and key paths - absolute, based on repository layout
USERS_DB_ENC_PATH = os.path.join(BASE_DIR, "data", "users.json.enc")
FERNET_KEY_PATH = os.path.join(BASE_DIR, "data", "key.key")
LOG_PATH = os.path.join(BASE_DIR, "logs", "security.log")
PROTECTED_DIR = os.path.join(BASE_DIR, "protected_files")
ACTIVE_SESSIONS_PATH = os.path.join(BASE_DIR, "data", "active_sessions.json")

PASSWORD_HASH_ROUNDS = 12
GUI_TITLE = "Basic Security System"
USER_LOCK_SECONDS = 180          # per-user lock duration
SYSTEM_FREEZE_SECONDS = 60       # system-wide freeze
ACTIVE_SESSIONS_PATH = "data/active_sessions.json"  # track logged-in users
