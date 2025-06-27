from tests.test_helpers import AppTestCase
from app.utils import RESERVED_USERNAMES
import json

class SignupTests(AppTestCase):

    def test_signup_username_invalid_is_rejected(self):
        """ Usernames with spaces and uppercase chars are rejected. """
        resp1 = self.client.post("/signup", data={"username": "UsE rName", "password": "pass"})
        self.assertIn("Invalid username.", resp1.text)

        resp2 = self.client.post("/signup", data={"username": "user name", "password": "pass"})
        self.assertIn("Invalid username.", resp2.text)

        resp3 = self.client.post("/signup", data={"username": "UpperCase", "password": "pass"})
        self.assertIn("Invalid username.", resp3.text)

    def test_signup_username_with_symbols_rejected(self):
        """ Reject usernames with non-alphanumeric chars. """
        for bad in ["abc.def", "user@", "weird$name", "with/slash", "brackets()", "semi;colon"]:
            resp = self.client.post("/signup", data={"username": bad, "password": "pass"})
            self.assertIn("Invalid username.", resp.text)

    def test_signup_username_with_dash_and_numbers_accepted(self):
        """ Alphanumeric and dashes are allowed for username signups. """
        resp = self.client.post("/signup", data={"username": "valid-user123", "password": "okpass"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/login")

    def test_signup_duplicate_username(self):
        """ Cannot create user with duplicate name. """
        self.create_user("existing")
        resp = self.client.post("/signup", data={"username": "existing", "password": "pwd"})
        self.assertIn("Username already exists.", resp.text)

    def test_signup_success_creates_user_and_redirects(self):
        """ Valid signups succeed and redirect to login page. """
        resp = self.client.post("/signup", data={"username": "testuser", "password": "Secret1"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/login")

        with open(self.users_path) as f:
            saved = json.load(f)
        self.assertIn("testuser", saved)
        self.assertIn("password_hash", saved["testuser"])
        self.assertIsInstance(saved["testuser"]["repos"], list)

    def test_signup_reserved_username_rejected(self):
        """ User cannot signup with blocked usernames. """
        for reserved in RESERVED_USERNAMES:
            resp = self.client.post("/signup", data={"username": reserved, "password": "somepass"})
            self.assertIn("Invalid username.", resp.text)

    def test_signup_password_with_space_rejected(self):
        """ Passwords with spaces not allowed. """
        resp = self.client.post("/signup", data={"username": "newuser", "password": "bad pass"})
        self.assertIn("Password cannot contain spaces.", resp.text)
