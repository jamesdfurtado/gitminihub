import os
import json
import shutil
import unittest

test_data_dir = "tests/data"
users_json_path = os.path.join(test_data_dir, "users.json")
repos_root_path = os.path.join(test_data_dir, "repos")

os.environ["GITMINIHUB_REPO_ROOT"] = repos_root_path
os.environ["GITMINIHUB_USERS_PATH"] = users_json_path
os.environ["GITMINIHUB_SECRET"] = "testsecret"

from fastapi.testclient import TestClient
from app.main import app
from app import utils
from itsdangerous import URLSafeSerializer
from passlib.hash import bcrypt
from datetime import datetime, timezone

class AppTestCase(unittest.TestCase):

    def setUp(self):
        """ Setting up the test environment (fresh every time). """
        self.client = TestClient(app)
        self.users_path = users_json_path
        self.repo_root = repos_root_path

        utils.users_path = self.users_path

        # Ensure tests/data/ exists
        os.makedirs(test_data_dir, exist_ok=True)

        # Start fresh users.json
        with open(self.users_path, "w") as f:
            json.dump({}, f)

        # Start fresh repos dir
        if os.path.exists(self.repo_root):
            shutil.rmtree(self.repo_root)
        os.makedirs(self.repo_root)

        secret = os.environ["GITMINIHUB_SECRET"]
        self.serializer = URLSafeSerializer(secret)

    def tearDown(self):
        """Clean up after each test run."""
        if os.path.exists(self.repo_root):
            shutil.rmtree(self.repo_root)
        if os.path.exists(self.users_path):
            os.remove(self.users_path)

    def create_user(self, username, password="pw", repos=None):
        """Creates a user in users.json with optional repos."""
        if repos is None:
            repos = []
        # Load existing users
        if os.path.exists(self.users_path):
            with open(self.users_path, "r") as f:
                users = json.load(f)
        else:
            users = {}
        users[username] = {
            "password_hash": bcrypt.hash(password),
            "repos": repos
        }
        self.save_users_file(users)

    def login_as(self, username):
        """Simulates a logged-in session by setting the session cookie."""
        self.set_session_cookie(username)

    def set_session_cookie(self, username):
        """Sets a signed session cookie for the user."""
        cookie = self.serializer.dumps(username)
        self.client.cookies.set("session", cookie)

    def create_repo(self, name, created_at=None):
        """Returns a repo dictionary for a given name."""
        if not created_at:
            created_at = datetime.now(timezone.utc).isoformat()
        return {"name": name, "created_at": created_at}

    def save_users_file(self, users_dict):
        """Overwrites users.json with the given user dict."""
        with open(self.users_path, "w") as f:
            json.dump(users_dict, f)

    def clear_users(self):
        """Wipes all users from users.json."""
        with open(self.users_path, "w") as f:
            json.dump({}, f)

    def create_repo_structure(self, username, repo_name):
        """Creates a basic .gitmini structure on disk for testing."""
        base = os.path.join(self.repo_root, username, repo_name, ".gitmini")
        os.makedirs(os.path.join(base, "objects"), exist_ok=True)
        os.makedirs(os.path.join(base, "refs", "heads"), exist_ok=True)
        open(os.path.join(base, "refs", "heads", "main"), "w").close()
