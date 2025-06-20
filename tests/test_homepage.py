import os
import json
import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.pages import utils

class HomepageTests(unittest.TestCase):
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

    def test_homepage(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Welcome to GitMiniHub", resp.text)

    def test_search_no_user(self):
        resp = self.client.get("/search")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Welcome to GitMiniHub", resp.text)  # fallback since error isn't rendered

    def test_search_with_user_redirect(self):
        resp = self.client.get("/search?user=johndoe", follow_redirects=False)
        self.assertIn(resp.status_code, (302, 307))
        self.assertEqual(resp.headers["location"], "/johndoe")

    def test_search_with_user_and_repo_redirect(self):
        resp = self.client.get("/search?user=jane&repo=repo1", follow_redirects=False)
        self.assertIn(resp.status_code, (302, 307))
        self.assertEqual(resp.headers["location"], "/jane/repo1")
