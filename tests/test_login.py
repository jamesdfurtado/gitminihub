from tests.test_helpers import AppTestCase

class LoginTests(AppTestCase):

    def test_login_empty_or_invalid_username(self):
        """ Invalid usernames throw an error. """
        resp = self.client.post("/login", data={"username": "", "password": "pwd"})
        self.assertIn("Invalid username or password.", resp.text)

        resp2 = self.client.post("/login", data={"username": "bad user", "password": "pwd"})
        self.assertIn("Invalid username or password.", resp2.text)

    def test_login_nonexistent_user(self):
        """ Test that unknown usernames trigger an error. """
        resp = self.client.post("/login", data={"username": "nouser", "password": "pwd"})
        self.assertIn("Invalid username or password.", resp.text)

    def test_login_wrong_password(self):
        """ Wrong passwords reject login. """
        self.create_user("bob", password="mypwd")
        resp = self.client.post("/login", data={"username": "bob", "password": "wrong"})
        self.assertIn("Invalid username or password.", resp.text)

    def test_login_success_redirects_home(self):
        """ Correct login redirects to homepage. """
        self.create_user("alice", password="mypwd")
        resp = self.client.post("/login", data={"username": "ALICE", "password": "mypwd"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/")

    def test_login_password_with_space_rejected(self):
        """ Passwords with spaces rejected. """
        self.create_user("user", password="mypassword")
        resp = self.client.post("/login", data={"username": "user", "password": "my password"})
        self.assertIn("Password cannot contain spaces.", resp.text)

    def test_login_username_with_spaces_normalized(self):
        """ Login with spaces are normalized. """
        self.create_user("demo", password="goodpwd")
        resp = self.client.post("/login", data={"username": "  d e m o  ", "password": "goodpwd"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/")

    def test_login_sets_session_cookie(self):
        """ Logging in sets a user session cookie. """
        self.create_user("user1", password="secret")
        resp = self.client.post("/login", data={"username": "user1", "password": "secret"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("session=", resp.headers.get("set-cookie", ""))
