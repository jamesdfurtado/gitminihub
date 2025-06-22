import json
from passlib.hash import bcrypt
from tests.test_helpers import AppTestCase

class SessionTests(AppTestCase):

    def test_valid_session_cookie_recognized(self):
        """ Validate login session. """
        with open(self.users_path, "w") as f:
            json.dump({"testuser": {"password_hash": bcrypt.hash("pw"), "repos": []}}, f)

        cookie = self.serializer.dumps("testuser")
        self.client.cookies.set("session", cookie)
        resp = self.client.get("/")
        self.assertIn("Signed in as", resp.text)
        self.assertIn("testuser", resp.text)

    def test_invalid_session_cookie_fails_silently(self):
        """ Failed login does not crash system. """
        self.client.cookies.set("session", "fake_or_tampered")
        resp = self.client.get("/")
        self.assertNotIn("Signed in as", resp.text)
        self.assertIn("Sign Up", resp.text)

    def test_missing_session_cookie_means_guest(self):
        """ Test that no cookie = not signed in """
        resp = self.client.get("/")
        self.assertNotIn("Signed in as", resp.text)
        self.assertIn("Log In", resp.text)

    def test_logout_clears_session_cookie(self):
        """ /logout route clears the cookie and redirects to homepage. """
        self.client.cookies.set("session", "placeholder")
        resp = self.client.get("/logout", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/")

        cookie_header = resp.headers.get("set-cookie", "")
        self.assertIn("session=", cookie_header)
        self.assertIn("Max-Age=0", cookie_header)
