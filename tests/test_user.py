from tests.test_helpers import AppTestCase
from app.utils import create_repo_entry
import json

class UserTests(AppTestCase):

    def test_user_profile(self):
        """ Test that a user’s profile page shows their repos correctly. """
        repos = [
            self.create_repo("my-repo", created_at="2025-06-24T00:00:00+00:00"),
            self.create_repo("weatherapp", created_at="2025-06-23T00:00:00+00:00"),
            self.create_repo("cool-stuff", created_at="2025-06-22T00:00:00+00:00")
        ]
        self.create_user("charlie", repos=repos)

        resp = self.client.get("/charlie")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("charlie's Repositories", resp.text)
        for repo in ["my-repo", "weatherapp", "cool-stuff"]:
            self.assertIn(f'<a href="/charlie/{repo}">{repo}</a>', resp.text)

    def test_user_with_no_repos(self):
        """ User profile with no repos loads correctly """
        self.create_user("norepos", repos=[])
        resp = self.client.get("/norepos")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("norepos currently has no repositories", resp.text)

    def test_nonexistent_user_profile(self):
        """ Nonexistent user profile returns error """
        self.clear_users()
        resp = self.client.get("/ghostuser")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("User does not exist", resp.text)

    def test_create_repo_authenticated_success(self):
        """ Logged in users can create repos on profile page. """
        self.create_user("alex", password="secret", repos=[])
        self.login_as("alex")
        resp = self.client.post("/api/create_remote_repo", data={"repo_name": "testrepo"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/alex/testrepo", resp.headers["location"])

        with open(self.users_path) as f:
            data = json.load(f)
        self.assertTrue(any(r["name"] == "testrepo" for r in data["alex"]["repos"]))

    def test_create_repo_duplicate_name_rejected(self):
        """ Duplicate repo names are rejected """
        dupe_repo = create_repo_entry("dupe")  # uses the same util used by production code
        self.create_user("sam", repos=[dupe_repo])
        self.login_as("sam")
        resp = self.client.post("/api/create_remote_repo", data={"repo_name": "dupe"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/?error=Repository%20already%20exists", resp.headers["location"])

    def test_create_repo_requires_login_redirects(self):
        """ Not logged in users cannot create repo """
        resp = self.client.post("/api/create_remote_repo", data={"repo_name": ...}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/login")
