import json
from tests.test_helpers import AppTestCase

class HomepageTests(AppTestCase):
    
    def test_homepage(self):
        """ Test for successful homepage load """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Welcome to GitMiniHub", resp.text)

    def test_search_no_user(self):
        """ Test that empty search bar reports error and reloads page """
        resp = self.client.get("/search")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Please specify a user", resp.text)

    def test_search_with_user_redirect(self):
        """ Test that only filling "User" bar redirects to user profile page """
        with open(self.users_path, "w") as f:
            json.dump({"johndoe": {"password_hash": "hash", "repos": []}}, f)

        resp = self.client.get("/search?user=johndoe", follow_redirects=False)
        self.assertIn(resp.status_code, (302, 307))
        self.assertEqual(resp.headers["location"], "/johndoe")

    def test_search_with_user_and_repo_redirect(self):
        """ Test that "User" and "Repository" bar redirects to a repository """
        with open(self.users_path, "w") as f:
            json.dump({
                "jane": {
                    "password_hash": "hash",
                    "repos": [{
                        "name": "repo1",
                        "created_at": "2025-06-24T00:00:00+00:00",
                        "path": ""
                    }]
                }
            }, f)

        resp = self.client.get("/search?user=jane&repo=repo1", follow_redirects=False)
        self.assertIn(resp.status_code, (302, 307))
        self.assertEqual(resp.headers["location"], "/jane/repo1")

    def test_search_invalid_user(self):
        """ Search with nonexistent user returns error """
        with open(self.users_path, "w") as f:
            json.dump({}, f)

        resp = self.client.get("/search?user=ghost", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("User does not exist", resp.text)

    def test_search_invalid_repo(self):
        """ Valid user but nonexistent repo returns error """
        with open(self.users_path, "w") as f:
            json.dump({
                "validuser": {
                    "password_hash": "x",
                    "repos": [{
                        "name": "goodrepo",
                        "created_at": "2025-06-24T00:00:00+00:00",
                        "path": ""
                    }]
                }
            }, f)

        resp = self.client.get("/search?user=validuser&repo=badrepo", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Repository does not exist", resp.text)

    def test_search_repo_only_fails(self):
        """ Only filling repo bar returns error """
        resp = self.client.get("/search?repo=somerepo", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Please specify a user", resp.text)
