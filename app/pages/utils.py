import os, json, re
from passlib.hash import bcrypt

# user content "database"
users_path = "app/data/users.json"

# These usernames cannot be used for signups
RESERVED_USERNAMES = {
    "login", "signup", "search", "static", "admin", "user", "api"
}

def load_users():
    if os.path.exists(users_path):
        with open(users_path, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(users_path, "w") as f:
        json.dump(users, f, indent=2)

# Normalize usernames to lowercase and remove spaces
def normalize_username(username: str) -> str:
    return username.replace(" ", "").lower()

# Reject usernames with invalid characters or reserved keywords
def is_invalid_username(username: str) -> bool:
    if not username:
        return True
    if normalize_username(username) in RESERVED_USERNAMES:
        return True
    if any(c.isupper() for c in username):
        return True
    if " " in username:
        return True
    if not re.fullmatch(r"[a-z0-9\-]+", username):
        return True
    return False

# Reject passwords with spaces
def is_invalid_password(password: str) -> bool:
    return " " in password

# Hash passwords
def hash_password(password: str) -> str:
    return bcrypt.hash(password)

# Verify incoming passwords
def verify_password(input_password: str, stored_hash: str) -> bool:
    return bcrypt.verify(input_password, stored_hash)
