import json
from tests.test_helpers import AppTestCase

class UserTests(AppTestCase):

    def test_user_profile(self):
        """ Test that a user’s profile page shows their repos correctly. """
        with open(self.users_path, "w") as f:
            json.dump({
                "charlie": {
                    "password_hash": "fake",
                    "repos": ["my-repo", "weatherapp", "cool-stuff"]
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
