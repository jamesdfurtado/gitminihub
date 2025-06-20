import json
from tests.test_helpers import UserJsonTestCase

class SignupTests(UserJsonTestCase):
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
