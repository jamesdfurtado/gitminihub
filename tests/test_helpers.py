# Just to clarify, these are helper functions for the test cases

import os
import json
import shutil
import unittest
from fastapi.testclient import TestClient
from app.main import app
from app import utils
from itsdangerous import URLSafeSerializer
from passlib.hash import bcrypt
from datetime import datetime, timezone

class AppTestCase(unittest.TestCase):

    def setUp(self):
        """ Setting up the test environment """
        self.client = TestClient(app)
        self.users_path = "tests/users.json"
        self.repo_root = "repos"
        self._backup = None

        if os.path.exists(self.users_path):
            with open(self.users_path, "r") as f:
                self._backup = json.load(f)
        else:
            os.makedirs(os.path.dirname(self.users_path), exist_ok=True)
            with open(self.users_path, "w") as f:
                json.dump({}, f)

        utils.users_path = self.users_path

        if not os.path.exists(self.repo_root):
            os.makedirs(self.repo_root)

        secret = os.environ["GITMINIHUB_SECRET"]
        self.serializer = URLSafeSerializer(secret)

    def tearDown(self):
        """ Tearing down test environment. """
        if self._backup is not None:
            with open(self.users_path, "w") as f:
                json.dump(self._backup, f)
        if os.path.exists(self.repo_root):
            shutil.rmtree(self.repo_root)

    def create_user(self, username, password="pw", repos=None):
        """Creates a user in users.json with optional repos."""
        if repos is None:
            repos = []
        users = {username: {
            "password_hash": bcrypt.hash(password),
            "repos": repos
        }}
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
