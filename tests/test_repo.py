from tests.test_helpers import UserJsonTestCase

class RepoTests(UserJsonTestCase):

    def test_view_repo_page(self):
        """ Test that visiting a repo page loads correctly. """
        resp = self.client.get("/alice/myrepo")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<h1>alice / myrepo</h1>", resp.text)
