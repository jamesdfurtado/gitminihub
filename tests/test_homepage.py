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
        """ Test that only filling 'User' bar redirects to user profile page """
        self.create_user("johndoe")
        resp = self.client.get("/search?user=johndoe", follow_redirects=False)
        self.assertIn(resp.status_code, (302, 307))
        self.assertEqual(resp.headers["location"], "/johndoe")

    def test_search_with_user_and_repo_redirect(self):
        """ Test that 'User' and 'Repository' bar redirects to a repository """
        repo = self.create_repo("repo1", created_at="2025-06-24T00:00:00+00:00")
        self.create_user("jane", repos=[repo])
        resp = self.client.get("/search?user=jane&repo=repo1", follow_redirects=False)
        self.assertIn(resp.status_code, (302, 307))
        self.assertEqual(resp.headers["location"], "/jane/repo1")

    def test_search_invalid_user(self):
        """ Search with nonexistent user returns error """
        self.clear_users()
        resp = self.client.get("/search?user=ghost", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("User does not exist", resp.text)

    def test_search_invalid_repo(self):
        """ Valid user but nonexistent repo returns error """
        valid_repo = self.create_repo("goodrepo", created_at="2025-06-24T00:00:00+00:00")
        self.create_user("validuser", repos=[valid_repo])
        resp = self.client.get("/search?user=validuser&repo=badrepo", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Repository does not exist", resp.text)

    def test_search_repo_only_fails(self):
        """ Only filling repo bar returns error """
        resp = self.client.get("/search?repo=somerepo", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Please specify a user", resp.text)

    def test_homepage_repo_creation_success(self):
        self.create_user("john", password="pw", repos=[])
        self.login_as("john")
        resp = self.client.post("/api/create_remote_repo", data={"repo_name": "newhomepage"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/john/newhomepage", resp.headers["location"])

    def test_homepage_create_repo_without_login_redirects(self):
        resp = self.client.post("/api/create_remote_repo", data={"repo_name": "x"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/login")

    def test_search_does_not_clear_recent_repos(self):
        """ Searching should not erase recent repo history from homepage """
        repo = self.create_repo("alpha", created_at="2025-06-24T00:00:00+00:00")
        self.create_user("bob", repos=[repo])
        self.login_as("bob")
        self.client.get("/bob/alpha")
        resp = self.client.get("/search?user=ghost", follow_redirects=True)
        self.assertIn("Recent Repositories", resp.text)
        self.assertIn("bob/alpha", resp.text)


    def test_homepage_recent_repos_reverse_chronological(self):
        """ Recent repos on homepage are ordered newest to oldest """
        repo1 = self.create_repo("a", created_at="2025-06-01T00:00:00+00:00")
        repo2 = self.create_repo("b", created_at="2025-06-15T00:00:00+00:00")
        repo3 = self.create_repo("c", created_at="2025-06-24T00:00:00+00:00")
        self.create_user("zoe", repos=[repo1, repo2, repo3])

        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

        # Find index positions to verify order
        idx_c = resp.text.find("zoe/c")
        idx_b = resp.text.find("zoe/b")
        idx_a = resp.text.find("zoe/a")

        self.assertTrue(idx_c < idx_b < idx_a)
