import os
import json
import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.pages import utils
from passlib.hash import bcrypt

class LoginTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.users_path = utils.users_path
        self._backup = {}
        if os.path.exists(self.users_path):
            with open(self.users_path, "r") as f:
                self._backup = json.load(f)
        with open(self.users_path, "w") as f:
            json.dump({}, f)

    def tearDown(self):
        with open(self.users_path, "w") as f:
            json.dump(self._backup, f)

    def test_login_empty_or_invalid_username(self):
        resp = self.client.post("/login", data={"username": "", "password": "pwd"})
        self.assertIn("Invalid username or password.", resp.text)

        resp2 = self.client.post("/login", data={"username": "bad user", "password": "pwd"})
        self.assertIn("Invalid username or password.", resp2.text)

    def test_login_nonexistent_user(self):
        resp = self.client.post("/login", data={"username": "nouser", "password": "pwd"})
        self.assertIn("Invalid username or password.", resp.text)

    def test_login_wrong_password(self):
        valid_hash = bcrypt.hash("mypwd")
        with open(self.users_path, "w") as f:
            json.dump({"bob": {"password_hash": valid_hash, "repos": []}}, f)

        resp = self.client.post("/login", data={"username": "bob", "password": "wrong"})
        self.assertIn("Invalid username or password.", resp.text)

    def test_login_success_redirects_home(self):
        valid_hash = bcrypt.hash("mypwd")
        with open(self.users_path, "w") as f:
            json.dump({"alice": {"password_hash": valid_hash, "repos": []}}, f)

        resp = self.client.post("/login", data={"username": "ALICE", "password": "mypwd"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/")
