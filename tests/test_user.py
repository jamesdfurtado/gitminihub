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
