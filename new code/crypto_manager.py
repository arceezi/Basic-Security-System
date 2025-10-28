import os
import json
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet, InvalidToken
from config import FERNET_KEY_PATH, USERS_DB_ENC_PATH

# === Key Management ===
# Prefer env var SECURITY_FERNET_KEY (base64 urlsafe 32-byte key)
# else load from FERNET_KEY_PATH; create if missing with 0600 perms.

def ensure_key() -> bytes:
    env_key = os.getenv("SECURITY_FERNET_KEY")
    if env_key:
        try:
            # Validate by constructing Fernet
            Fernet(env_key.encode())
            return env_key.encode()
        except Exception:
            raise ValueError("SECURITY_FERNET_KEY is not a valid Fernet key")

    os.makedirs(os.path.dirname(FERNET_KEY_PATH), exist_ok=True)
    if not os.path.exists(FERNET_KEY_PATH):
        key = Fernet.generate_key()
        with open(FERNET_KEY_PATH, "wb") as f:
            f.write(key)
        try:
            os.chmod(FERNET_KEY_PATH, 0o600)
        except Exception:
            pass
        return key
    with open(FERNET_KEY_PATH, "rb") as f:
        return f.read()


def _fernet() -> Fernet:
    return Fernet(ensure_key())

# === Encrypted Load/Save ===

def load_users_encrypted() -> Dict[str, Any]:
    if not os.path.exists(USERS_DB_ENC_PATH):
        return {}
    with open(USERS_DB_ENC_PATH, "rb") as f:
        ciphertext = f.read()
    try:
        plaintext = _fernet().decrypt(ciphertext)
    except InvalidToken:
        # Helpful message if an older plaintext file exists under .enc
        raise RuntimeError(
            "Failed to decrypt users DB. If you previously saved plaintext to "
            f"{USERS_DB_ENC_PATH}, delete it and re-run to bootstrap an encrypted one."
        )
    return json.loads(plaintext.decode("utf-8"))


def save_users_encrypted(users: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(USERS_DB_ENC_PATH), exist_ok=True)
    data = json.dumps(users, indent=2).encode("utf-8")
    token = _fernet().encrypt(data)
    tmp = USERS_DB_ENC_PATH + ".tmp"
    with open(tmp, "wb") as f:
        f.write(token)
    os.replace(tmp, USERS_DB_ENC_PATH)

# === Optional: Key Rotation ===

def rotate_key(optional_new_key: Optional[bytes] = None) -> None:
    """
    Decrypt with current key, write a new key (or use provided), and re-encrypt.
    NOTE: If using SECURITY_FERNET_KEY, rotation should be handled by changing that env
    and re-encrypting; this helper assumes file-based key.
    """
    # Load with current key
    users = load_users_encrypted()

    # Decide new key
    new_key = optional_new_key or Fernet.generate_key()

    # If using file key, overwrite file; otherwise just use in-memory
    os.makedirs(os.path.dirname(FERNET_KEY_PATH), exist_ok=True)
    with open(FERNET_KEY_PATH, "wb") as f:
        f.write(new_key)
    try:
        os.chmod(FERNET_KEY_PATH, 0o600)
    except Exception:
        pass

    # Re-encrypt using new key
    data = json.dumps(users, indent=2).encode("utf-8")
    token = Fernet(new_key).encrypt(data)
    tmp = USERS_DB_ENC_PATH + ".tmp"
    with open(tmp, "wb") as f:
        f.write(token)
    os.replace(tmp, USERS_DB_ENC_PATH)
