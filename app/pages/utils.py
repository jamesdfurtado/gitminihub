import os, json
from passlib.hash import bcrypt

# user content "database"
users_path = "app/data/users.json"

# These usernames cannot be used
RESERVED_USERNAMES = {"login", "signup"}

def load_users():
    if os.path.exists(users_path):
        with open(users_path, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(users_path, "w") as f:
        json.dump(users, f, indent=2)

def normalize_username(username: str) -> str:
    return username.replace(" ", "").lower()

def is_invalid_username(username: str) -> bool:
    return (
        not username
        or " " in username
        or any(c.isupper() for c in username)
        or normalize_username(username) in RESERVED_USERNAMES
    )

# Reject passwords with invalid characters
def is_invalid_password(password: str) -> bool:
    return " " in password

# Hash passwords
def hash_password(password: str) -> str:
    return bcrypt.hash(password)

# Verify incoming passwords
def verify_password(input_password: str, stored_hash: str) -> bool:
    return bcrypt.verify(input_password, stored_hash)
