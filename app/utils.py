import os, json, re, shutil
from passlib.hash import bcrypt
from itsdangerous import URLSafeSerializer
from fastapi import Request
from datetime import datetime, UTC

# user content "database"
users_path = os.getenv("GITMINIHUB_USERS_PATH", "app/data/users.json")
RESERVED_USERNAMES = {
    "login", "logout", "signup", "search", "static", "admin", "user", "api", "create_repo",
    "auth", "cli-login"
}

# Dynamic repo root (so tests can override it)
def get_repo_root():
    return os.getenv("GITMINIHUB_REPO_ROOT", "app/data/repos")

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
        "created_at": datetime.now(UTC).isoformat()
    }

def add_repo_to_user(users: dict, username: str, repo_name: str) -> str | None:
    normalized = normalize_username(repo_name)
    user_data = users.get(username)
    if not user_data:
        return "User not found"
    if any(r["name"] == normalized for r in user_data["repos"]):
        return "Repository already exists"
    user_data["repos"].append(create_repo_entry(normalized))
    return None

def get_user_repo_entry(users: dict, username: str, repo_name: str) -> dict | None:
    return next((r for r in users.get(username, {}).get("repos", []) if r["name"] == repo_name), None)

def delete_repo_from_filesystem(username: str, repo_name: str):
    path = os.path.join(get_repo_root(), username, repo_name)
    if os.path.exists(path):
        shutil.rmtree(path)

def remove_repo_from_user(users: dict, username: str, repo_name: str):
    users[username]["repos"] = [
        r for r in users.get(username, {}).get("repos", [])
        if r["name"] != repo_name
    ]

def is_repo_owner(current_user: str | None, username: str) -> bool:
    return current_user == username

def get_all_repos(users: dict) -> list[dict]:
    all_repos = []
    for username, data in users.items():
        for repo in data["repos"]:
            all_repos.append({
                "username": username,
                "name": repo["name"],
                "created_at": repo["created_at"]
            })
    return sorted(all_repos, key=lambda r: r["created_at"], reverse=True)

def initialize_repo_structure(username: str, repo_name: str):
    base_path = os.path.join(get_repo_root(), username, repo_name, ".gitmini")
    if os.path.exists(base_path):
        return False

    os.makedirs(os.path.join(base_path, "objects"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "refs", "heads"), exist_ok=True)
    open(os.path.join(base_path, "refs", "heads", "main"), "w").close()

    return True
