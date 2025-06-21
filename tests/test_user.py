from tests.test_helpers import UserJsonTestCase

class UserTests(UserJsonTestCase):

    def test_user_profile(self):
        """ Test that a user’s profile page shows their repos correctly. """
        resp = self.client.get("/charlie")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("charlie's Repositories", resp.text)
        for repo in ["my-repo", "weatherapp", "cool-stuff"]:
            self.assertIn(f'<a href="/charlie/{repo}">{repo}</a>', resp.text)
