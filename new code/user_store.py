from typing import Optional, Dict, List
from crypto_manager import load_users_encrypted, save_users_encrypted


def get_all_users() -> Dict[str, dict]:
    return load_users_encrypted()


def get_user(username: str) -> Optional[dict]:
    return get_all_users().get(username)


def upsert_user(user: dict) -> None:
    db = get_all_users()
    db[user["username"]] = user
    save_users_encrypted(db)


def list_usernames() -> List[str]:
    return list(get_all_users().keys())
