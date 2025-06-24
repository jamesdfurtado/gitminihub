import json
from tests.test_helpers import AppTestCase

class RepoTests(AppTestCase):

    def test_view_repo_page(self):
        """ Test that visiting a valid repo page loads correctly. """
        resp = self.client.get("/alice/myrepo")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<h1>alice / myrepo</h1>", resp.text)

    def test_repo_does_not_exist_message(self):
        """ Visiting a nonexistent repo returns error """
        resp = self.client.get("/someuser/fakerepo")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Repository does not exist", resp.text)
