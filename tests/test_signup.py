import json
from tests.test_helpers import UserJsonTestCase

class SignupTests(UserJsonTestCase):

    def test_signup_username_invalid_is_rejected(self):
        """ Test that usernames with spaces are rejected. """
        resp = self.client.post("/signup", data={"username": "UsE rName", "password": "pass"})
        self.assertIn("Invalid username.", resp.text)



    def test_signup_duplicate_username(self):
        """ Test that existing usernames can’t be reused. """
        with open(self.users_path, "w") as f:
            json.dump({"existing": {"password_hash": "hash", "repos": []}}, f)

        resp = self.client.post("/signup", data={"username": "existing", "password": "pwd"})
        self.assertIn("Username already exists.", resp.text)


    def test_signup_success_creates_user_and_redirects(self):
        """ Test that valid signups create a user and redirect to login. """
        resp = self.client.post("/signup", data={"username": "TestUser", "password": "Secret1"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/login")

        with open(self.users_path) as f:
            saved = json.load(f)
        self.assertIn("testuser", saved)
        self.assertIn("password_hash", saved["testuser"])
        self.assertIsInstance(saved["testuser"]["repos"], list)


    def test_signup_reserved_username_rejected(self):
        """ Test that usernames 'login' and 'signup' are blocked. """
        for reserved in ["login", "signup"]:
            resp = self.client.post("/signup", data={"username": reserved, "password": "somepass"})
            self.assertIn("Invalid username.", resp.text)


    def test_signup_password_with_space_rejected(self):
        """ Test that signup rejects passwords with spaces. """
        resp = self.client.post("/signup", data={"username": "newuser", "password": "bad pass"})
        self.assertIn("Password cannot contain spaces.", resp.text)
