from core.utils import hash_password, delay, log_event
from core.data_manager import load_users, save_users

MAX_ATTEMPTS = 5
FREEZE_TIME = 10  # seconds

class AuthManager:
    def __init__(self):
        self.failed_attempts = 0

    def register_user(self, username: str, password: str):
        users = load_users()
        if username in users:
            print("⚠️ Username already exists.")
            return
        users[username] = hash_password(password)
        save_users(users)
        log_event(f"User '{username}' registered successfully.")
        print("✅ Registration successful!")

    def login(self, username: str, password: str) -> bool:
        users = load_users()
        hashed_input = hash_password(password)

        if username in users and users[username] == hashed_input:
            print("✅ Login successful!")
            log_event(f"User '{username}' logged in.")
            self.failed_attempts = 0
            return True

        self.failed_attempts += 1
        log_event(f"Failed login attempt for '{username}'. ({self.failed_attempts}/{MAX_ATTEMPTS})", "warning")

        if self.failed_attempts >= MAX_ATTEMPTS:
            delay(FREEZE_TIME)
            self.failed_attempts = 0
        else:
            print("❌ Incorrect username or password.")
        return False
