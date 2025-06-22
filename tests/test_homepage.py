from tests.test_helpers import AppTestCase

class HomepageTests(AppTestCase):
    
    def test_homepage(self):
        """ Test for successful homepage load """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Welcome to GitMiniHub", resp.text)

    def test_search_no_user(self):
        """ Test that empty search bar does nothing and returns to homepage """
        resp = self.client.get("/search")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Welcome to GitMiniHub", resp.text)

    def test_search_with_user_redirect(self):
        """ Test that only filling "User" bar redirects to user profile page """
        resp = self.client.get("/search?user=johndoe", follow_redirects=False)
        self.assertIn(resp.status_code, (302, 307))
        self.assertEqual(resp.headers["location"], "/johndoe")

    def test_search_with_user_and_repo_redirect(self):
        """ Test that "User" and "Repository" bar redirects to a repository """
        resp = self.client.get("/search?user=jane&repo=repo1", follow_redirects=False)
        self.assertIn(resp.status_code, (302, 307))
        self.assertEqual(resp.headers["location"], "/jane/repo1")
