import hashlib
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="logs/security.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def hash_password(password: str) -> str:
    """Returns SHA-256 hash of a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def delay(seconds: int):
    """Simple delay with logging."""
    logging.info(f"System frozen for {seconds} seconds due to failed attempts.")
    print(f"\n⚠️ System locked for {seconds} seconds. Please wait...")
    time.sleep(seconds)
    print("\nSystem unlocked. You may try again.")

def log_event(message: str, level="info"):
    """Central logging for security events."""
    if level == "warning":
        logging.warning(message)
    else:
        logging.info(message)
