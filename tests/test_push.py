import os
import json
import shutil
import tempfile
import unittest
from fastapi.testclient import TestClient
from app.main import app
from tests.test_helpers import AppTestCase

class PushTests(AppTestCase):
    def make_branch(self, username, repo_name, branch):
        base = os.path.join(self.repo_root, username, repo_name, ".gitmini", "refs", "heads")
        os.makedirs(base, exist_ok=True)
        with open(os.path.join(base, branch), "w") as f:
            f.write("commit123")

    def add_api_key(self, username, api_key):
        with open(self.users_path, "r") as f:
            users = json.load(f) 
        if "api_keys" not in users[username]:
            users[username]["api_keys"] = []
        users[username]["api_keys"].append(api_key)
        with open(self.users_path, "w") as f:
            json.dump(users, f)

    def test_success(self):
        api_key = "validkey"
        self.create_user("alice", repos=[])
        self.add_api_key("alice", api_key)
        os.makedirs(os.path.join(self.repo_root, "alice", "myrepo", ".gitmini"))
        self.make_branch("alice", "myrepo", "main")
        resp = self.client.post("/api/remote/push", json={"user": "alice", "api_key": api_key, "repo": "myrepo", "branch": "main"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["message"], "Push successful")

    def test_auth_failure(self):
        api_key = "realkey"
        self.create_user("bob", repos=[])
        self.add_api_key("bob", api_key)
        os.makedirs(os.path.join(self.repo_root, "bob", "repo1", ".gitmini"))
        self.make_branch("bob", "repo1", "main")
        # Wrong API key
        resp = self.client.post("/api/remote/push", json={"user": "bob", "api_key": "wrong", "repo": "repo1", "branch": "main"})
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()["message"], "Authentication failed")

    def test_repo_not_found(self):
        api_key = "key"
        self.create_user("carol", repos=[])
        self.add_api_key("carol", api_key)
        resp = self.client.post("/api/remote/push", json={"user": "carol", "api_key": api_key, "repo": "missing", "branch": "main"})
        self.assertIn(resp.status_code, (403, 404))
        self.assertEqual(resp.json()["status"], "error")
        self.assertIn("Repository not found", resp.json()["message"])

    def test_access_denied(self):
        api_key = "k1"
        self.create_user("dave", repos=[])
        self.create_user("eve", repos=[])
        self.add_api_key("dave", api_key)
        self.add_api_key("eve", "k2")
        os.makedirs(os.path.join(self.repo_root, "eve", "sharedrepo", ".gitmini"))
        self.make_branch("eve", "sharedrepo", "main")
        # Dave tries to access Eve's repo
        resp = self.client.post("/api/remote/push", json={"user": "dave", "api_key": api_key, "repo": "sharedrepo", "branch": "main"})
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()["status"], "error")
        self.assertIn("Repository not found or access denied", resp.json()["message"])

    def test_branch_not_found(self):
        api_key = "k3"
        self.create_user("frank", repos=[])
        self.add_api_key("frank", api_key)
        os.makedirs(os.path.join(self.repo_root, "frank", "repoz", ".gitmini"))
        # No branch created
        resp = self.client.post("/api/remote/push", json={"user": "frank", "api_key": api_key, "repo": "repoz", "branch": "dev"})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["status"], "error")
        self.assertEqual(resp.json()["message"], "Remote branch not found.")

    def test_malformed_payload(self):
        api_key = "k4"
        self.create_user("gina", repos=[])
        self.add_api_key("gina", api_key)
        # Missing fields
        resp = self.client.post("/api/remote/push", json={"user": "gina"})
        self.assertEqual(resp.status_code, 422)
        # Not JSON
        resp = self.client.post("/api/remote/push", content=b"notjson", headers={"content-type": "application/json"})
        self.assertEqual(resp.status_code, 422) 