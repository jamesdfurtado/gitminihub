import unittest
from fastapi.testclient import TestClient
from app.main import app

class RepoTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_view_repo_page(self):
        resp = self.client.get("/alice/myrepo")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<h1>alice / myrepo</h1>", resp.text)
