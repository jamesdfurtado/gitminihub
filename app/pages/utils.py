import os, json

users_path = "app/data/users.json"

def load_users():
    if os.path.exists(users_path):
        with open(users_path, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(users_path, "w") as f:
        json.dump(users, f, indent=2)
