import unittest
from fastapi.testclient import TestClient
from app.main import app

class UserTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_user_profile(self):
        resp = self.client.get("/charlie")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("charlie's Repositories", resp.text)
        for repo in ["my-repo", "weatherapp", "cool-stuff"]:
            self.assertIn(f'<a href="/charlie/{repo}">{repo}</a>', resp.text)
