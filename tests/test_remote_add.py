import os
import json
import shutil
import tempfile
import unittest
from fastapi.testclient import TestClient
from app.main import app
from tests.test_helpers import AppTestCase

class RemoteAddTests(AppTestCase):
    def make_branches(self, username, repo_name, branches):
        """Create refs/heads/ files for the given repo and branch mapping."""
        base = os.path.join(self.repo_root, username, repo_name, ".gitmini", "refs", "heads")
        os.makedirs(base, exist_ok=True)
        for branch, commit in branches.items():
            with open(os.path.join(base, branch), "w") as f:
                f.write(commit)

    def test_success(self):
        self.create_user("alice", repos=[])
        os.makedirs(os.path.join(self.repo_root, "alice", "myrepo", ".gitmini"))
        self.make_branches("alice", "myrepo", {"main": "abc123", "dev": "def456"})
        resp = self.client.post("/api/remote_add", json={"user": "alice", "api_key": "", "repo": "myrepo"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["branches"], {"main": "abc123", "dev": "def456"})

    def test_auth_failure(self):
        self.create_user("bob", repos=[])
        os.makedirs(os.path.join(self.repo_root, "bob", "repo1", ".gitmini"))
        self.make_branches("bob", "repo1", {"main": "c"})
        # Wrong API key
        resp = self.client.post("/api/remote_add", json={"user": "bob", "api_key": "wrong", "repo": "repo1"})
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()["message"], "Authentication failed")

    def test_repo_not_found(self):
        self.create_user("carol", repos=[])
        resp = self.client.post("/api/remote_add", json={"user": "carol", "api_key": "", "repo": "missing"})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["message"], "Repository not found")

    def test_access_denied(self):
        self.create_user("dave", repos=[])
        self.create_user("eve", repos=[])
        os.makedirs(os.path.join(self.repo_root, "eve", "sharedrepo", ".gitmini"))
        self.make_branches("eve", "sharedrepo", {"main": "h"})
        resp = self.client.post("/api/remote_add", json={"user": "dave", "api_key": "", "repo": "sharedrepo"})
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()["message"], "Access denied to repository")

    def test_malformed_payload(self):
        self.create_user("frank", repos=[])
        # Missing fields
        resp = self.client.post("/api/remote_add", json={"user": "frank"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["message"], "Invalid request payload")
        # Not JSON
        resp = self.client.post("/api/remote_add", content=b"notjson", headers={"content-type": "application/json"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["message"], "Invalid request payload")