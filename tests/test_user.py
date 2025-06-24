import json
from tests.test_helpers import AppTestCase
from app.pages.utils import create_repo_entry
from passlib.hash import bcrypt

class UserTests(AppTestCase):

    def test_user_profile(self):
        """ Test that a user’s profile page shows their repos correctly. """
        with open(self.users_path, "w") as f:
            json.dump({
                "charlie": {
                    "password_hash": "fake",
                    "repos": [
                        {"name": "my-repo", "created_at": "2025-06-24T00:00:00+00:00", "path": ""},
                        {"name": "weatherapp", "created_at": "2025-06-23T00:00:00+00:00", "path": ""},
                        {"name": "cool-stuff", "created_at": "2025-06-22T00:00:00+00:00", "path": ""}
                    ]
                }
            }, f)

        resp = self.client.get("/charlie")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("charlie's Repositories", resp.text)
        for repo in ["my-repo", "weatherapp", "cool-stuff"]:
            self.assertIn(f'<a href="/charlie/{repo}">{repo}</a>', resp.text)

    def test_user_with_no_repos(self):
        """ User profile with no repos loads correctly """
        with open(self.users_path, "w") as f:
            json.dump({
                "norepos": {
                    "password_hash": "fake",
                    "repos": []
                }
            }, f)

        resp = self.client.get("/norepos")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("norepos currently has no repositories", resp.text)

    def test_nonexistent_user_profile(self):
        """ Nonexistent user profile returns error """
        with open(self.users_path, "w") as f:
            json.dump({}, f)

        resp = self.client.get("/ghostuser")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("User does not exist", resp.text)

    def test_create_repo_authenticated_success(self):
        """ Logged in users can create repos on profile page. """
        users = {
            "alex": {
                "password_hash": bcrypt.hash("secret"),
                "repos": []
            }
        }
        with open(self.users_path, "w") as f:
            json.dump(users, f)

        self.client.cookies.set("session", self.serializer.dumps("alex"))
        resp = self.client.post("/create_repo", data={"repo_name": "testrepo"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/alex/testrepo", resp.headers["location"])

        with open(self.users_path) as f:
            data = json.load(f)
        self.assertTrue(any(r["name"] == "testrepo" for r in data["alex"]["repos"]))

    def test_create_repo_duplicate_name_rejected(self):
        """ Duplicate repo names are rejected """
        users = {
            "sam": {
                "password_hash": bcrypt.hash("pw"),
                "repos": [create_repo_entry("dupe")]
            }
        }
        with open(self.users_path, "w") as f:
            json.dump(users, f)

        self.client.cookies.set("session", self.serializer.dumps("sam"))
        resp = self.client.post("/create_repo", data={"repo_name": "dupe"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/?error=Repository%20already%20exists", resp.headers["location"])

    def test_create_repo_requires_login_redirects(self):
        """ Not logged in users cannot create repo """
        resp = self.client.post("/create_repo", data={"repo_name": "shouldfail"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/login")
