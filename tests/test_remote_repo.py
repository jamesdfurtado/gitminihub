from tests.test_helpers import AppTestCase
import json
import os

class RemoteRepoTests(AppTestCase):

    def test_repo_delete_flow(self):
        """ User can delete their own repo after confirmation """
        repo = self.create_repo("project")
        self.create_user("james", repos=[repo])
        self.login_as("james")

        base = os.path.join(self.repo_root, "james", "project", ".gitmini")
        os.makedirs(base, exist_ok=True)

        resp = self.client.post("/james/project/delete", data={"confirm_name": "project"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/james")

        # Confirm it's gone
        with open(self.users_path) as f:
            users = json.load(f)
        self.assertEqual(users["james"]["repos"], [])

        # Visit page should now show error
        resp = self.client.get("/james/project")
        self.assertIn("Repository does not exist", resp.text)

    def test_repo_delete_wrong_confirmation(self):
        """ Delete fails if confirmation name is incorrect """
        repo = self.create_repo("project")
        self.create_user("james", repos=[repo])
        self.login_as("james")

        base = os.path.join(self.repo_root, "james", "project", ".gitmini")
        os.makedirs(base, exist_ok=True)

        resp = self.client.post("/james/project/delete", data={"confirm_name": "wrong"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers["location"], "/james/project?error=confirmation_mismatch")

    def test_repo_delete_blocked_if_not_owner(self):
        """ Non-owners can't delete repos """
        repo = self.create_repo("project")
        self.create_user("james", repos=[repo])
        self.create_user("intruder")
        self.login_as("intruder")

        base = os.path.join(self.repo_root, "james", "project", ".gitmini")
        os.makedirs(base, exist_ok=True)

        # Make sure the repo exists
        get_resp = self.client.get("/james/project")
        self.assertIn("james / project", get_resp.text)

        # Try to delete it
        post_resp = self.client.post("/james/project/delete", data={"confirm_name": "project"}, follow_redirects=False)
        self.assertEqual(post_resp.status_code, 302)
        self.assertEqual(post_resp.headers["location"], "/james/project?error=unauthorized")

