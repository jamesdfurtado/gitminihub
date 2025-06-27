from tests.test_helpers import AppTestCase
import json
import os

class RepoTests(AppTestCase):

    def test_guest_can_view_existing_repo(self):
        """ Guests can view existing repos """
        repo = self.create_repo("project")
        self.create_user("james", repos=[repo])
        resp = self.client.get("/james/project")
        self.assertIn("james / project", resp.text)
        self.assertIn("placeholder repo view", resp.text)

    def test_guest_cannot_see_delete_button(self):
        """ Guests cannot see delete repo button """
        repo = self.create_repo("project")
        self.create_user("james", repos=[repo])
        resp = self.client.get("/james/project")
        self.assertNotIn("Delete Repository", resp.text)

    def test_guest_visiting_nonexistent_repo(self):
        """ Guests get error for nonexistent repo """
        self.create_user("james", repos=[])
        resp = self.client.get("/james/fake")
        self.assertIn("Repository does not exist", resp.text)

    def test_guest_visiting_repo_of_nonexistent_user(self):
        """ Guests visiting a nonexistent user's repo get error """
        resp = self.client.get("/ghost/project")
        self.assertIn("Repository does not exist", resp.text)

    def test_user_can_view_own_repo(self):
        """ Signed-in user can view their own repo and see delete button """
        repo = self.create_repo("project")
        self.create_user("james", repos=[repo])
        self.login_as("james")
        resp = self.client.get("/james/project")
        self.assertIn("Delete Repository", resp.text)

    def test_user_cannot_see_delete_button_on_others_repo(self):
        """ Signed-in user cannot delete someone else's repo """
        repo = self.create_repo("project")
        self.create_user("james", repos=[repo])
        self.create_user("other")
        self.login_as("other")
        resp = self.client.get("/james/project")
        self.assertNotIn("Delete Repository", resp.text)

    def test_user_visiting_own_nonexistent_repo(self):
        """ Own nonexistent repo shows error """
        self.create_user("james", repos=[])
        self.login_as("james")
        resp = self.client.get("/james/project")
        self.assertIn("Repository does not exist", resp.text)

    def test_user_visiting_others_nonexistent_repo(self):
        """ Viewing someone else's nonexistent repo shows error """
        self.create_user("james", repos=[])
        self.create_user("sam")
        self.login_as("sam")
        resp = self.client.get("/james/fake")
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

