import os
import json
import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.pages import utils

class SignupTests(unittest.TestCase):
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

    def test_signup_invalid_username_space(self):
        resp = self.client.post("/signup", data={"username": "user name", "password": "pass"})
        self.assertIn("Username must be lowercase and contain no spaces.", resp.text)

    def test_signup_duplicate_username(self):
        with open(self.users_path, "w") as f:
            json.dump({"existing": {"password_hash": "hash", "repos": []}}, f)

        resp = self.client.post("/signup", data={"username": "existing", "password": "pwd"})
        self.assertIn("Username already exists.", resp.text)

    def test_signup_success_creates_user_and_redirects(self):
        resp = self.client.post("/signup", data={"username": "TestUser", "password": "Secret1"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/login")

        with open(self.users_path) as f:
            saved = json.load(f)
        self.assertIn("testuser", saved)
        self.assertIn("password_hash", saved["testuser"])
        self.assertIsInstance(saved["testuser"]["repos"], list)
