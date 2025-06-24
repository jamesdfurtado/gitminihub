import os, json, re
from passlib.hash import bcrypt
from itsdangerous import URLSafeSerializer
from fastapi import Request
from datetime import datetime, UTC

# user content "database"
users_path = "app/data/users.json"
RESERVED_USERNAMES = {
    "login", "logout", "signup", "search", "static", "admin", "user", "api", "create_repo"
}

# For validating cookies
SECRET_KEY = os.environ["GITMINIHUB_SECRET"]
serializer = URLSafeSerializer(SECRET_KEY)

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

def is_invalid_password(password: str) -> bool:
    return " " in password

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(input_password: str, stored_hash: str) -> bool:
    return bcrypt.verify(input_password, stored_hash)

# sign a cookie with username
def create_session_cookie(username: str) -> str:
    return serializer.dumps(username)

# return the current user if session is valid
def get_current_user(request: Request) -> str | None:
    cookie = request.cookies.get("session")
    if not cookie:
        return None
    try:
        username = serializer.loads(cookie)
        return username
    except Exception:
        return None


def create_repo_entry(name: str) -> dict:
    return {
        "name": name,
        "created_at": datetime.now(UTC).isoformat(),
        "path": ""  # empty for now, logic will be coded when remote file storage is added.
    }

# Creates a new repo (just like clicking "Create repo" button on GitHub)
def add_repo_to_user(users: dict, username: str, repo_name: str) -> str | None:
    """
    Adds a new repo to the given user if it doesn't already exist.
    Returns an error message string if there's a problem, or None if success.
    """
    normalized = normalize_username(repo_name)
    user_data = users.get(username)

    if not user_data:
        return "User not found"

    if any(r["name"] == normalized for r in user_data["repos"]):
        return "Repository already exists"

    user_data["repos"].append(create_repo_entry(normalized))
    return None

