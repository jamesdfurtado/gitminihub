import json
from passlib.hash import bcrypt
from tests.test_helpers import UserJsonTestCase

class LoginTests(UserJsonTestCase):

    def test_login_empty_or_invalid_username(self):
        """ Test that empty or invalid usernames show a login error. """
        resp = self.client.post("/login", data={"username": "", "password": "pwd"})
        self.assertIn("Invalid username or password.", resp.text)

        resp2 = self.client.post("/login", data={"username": "bad user", "password": "pwd"})
        self.assertIn("Invalid username or password.", resp2.text)

    def test_login_nonexistent_user(self):
        """ Test that unknown usernames trigger an error. """
        resp = self.client.post("/login", data={"username": "nouser", "password": "pwd"})
        self.assertIn("Invalid username or password.", resp.text)

    def test_login_wrong_password(self):
        """ Test that wrong passwords reject login. """
        valid_hash = bcrypt.hash("mypwd")
        with open(self.users_path, "w") as f:
            json.dump({"bob": {"password_hash": valid_hash, "repos": []}}, f)

        resp = self.client.post("/login", data={"username": "bob", "password": "wrong"})
        self.assertIn("Invalid username or password.", resp.text)

    def test_login_success_redirects_home(self):
        """ Test that correct login redirects to homepage. """
        valid_hash = bcrypt.hash("mypwd")
        with open(self.users_path, "w") as f:
            json.dump({"alice": {"password_hash": valid_hash, "repos": []}}, f)

        resp = self.client.post("/login", data={"username": "ALICE", "password": "mypwd"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/")

    def test_login_password_with_space_rejected(self):
        """ Test that passwords with spaces are rejected during login. """
        valid_hash = bcrypt.hash("mypassword")
        with open(self.users_path, "w") as f:
            json.dump({"user": {"password_hash": valid_hash, "repos": []}}, f)

        resp = self.client.post("/login", data={"username": "user", "password": "my password"})
        self.assertIn("Password cannot contain spaces.", resp.text)

    def test_login_username_with_spaces_normalized(self):
        """ Test that usernames with spaces are normalized and allowed. """
        valid_hash = bcrypt.hash("goodpwd")
        with open(self.users_path, "w") as f:
            json.dump({"demo": {"password_hash": valid_hash, "repos": []}}, f)

        resp = self.client.post("/login", data={"username": "  d e m o  ", "password": "goodpwd"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/")
