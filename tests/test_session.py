import json
from passlib.hash import bcrypt
from tests.test_helpers import AppTestCase

class SessionTests(AppTestCase):

    def test_valid_session_cookie_recognized(self):
        """ Validate login session reflects in UI header. """
        with open(self.users_path, "w") as f:
            json.dump({"testuser": {"password_hash": bcrypt.hash("pw"), "repos": []}}, f)

        cookie = self.serializer.dumps("testuser")
        self.client.cookies.set("session", cookie)
        resp = self.client.get("/")
        self.assertIn('<a href="/testuser"', resp.text)
        self.assertIn("Log Out", resp.text)

    def test_invalid_session_cookie_fails_silently(self):
        """ Failed login does not crash system. """
        self.client.cookies.set("session", "fake_or_tampered")
        resp = self.client.get("/")
        self.assertIn("Sign Up", resp.text)
        self.assertIn("Log In", resp.text)

    def test_missing_session_cookie_means_guest(self):
        """ Test that no cookie = not signed in """
        resp = self.client.get("/")
        self.assertIn("Log In", resp.text)
        self.assertIn("Sign Up", resp.text)

    def test_logout_clears_session_cookie(self):
        """ /logout route clears the cookie and redirects to homepage. """
        self.client.cookies.set("session", "placeholder")
        resp = self.client.get("/logout", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/")

        cookie_header = resp.headers.get("set-cookie", "")
        self.assertIn("session=", cookie_header)
        self.assertIn("Max-Age=0", cookie_header)

    def test_session_persists_across_pages(self):
        """ Session remains active across multiple routes """
        with open(self.users_path, "w") as f:
            json.dump({"testuser": {"password_hash": bcrypt.hash("pw"), "repos": ["repo1"]}}, f)

        cookie = self.serializer.dumps("testuser")
        self.client.cookies.set("session", cookie)

        # Visit homepage
        resp_home = self.client.get("/")
        self.assertIn("Log Out", resp_home.text)

        # Visit profile page
        resp_profile = self.client.get("/testuser")
        self.assertIn("Log Out", resp_profile.text)

        # Visit repo page
        resp_repo = self.client.get("/testuser/repo1")
        self.assertIn("Log Out", resp_repo.text)

