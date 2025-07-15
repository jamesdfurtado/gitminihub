import json
import os
import re
from tests.test_helpers import AppTestCase
from app import utils

class UtilsTests(AppTestCase):

    def test_load_users_no_file(self):
        """ Test that loading users with empty users.json doesn't crash. """
        if self.users_path and os.path.exists(self.users_path):
            os.remove(self.users_path)
        self.assertEqual(utils.load_users(), {})

    def test_load_users_with_file(self):
        """ Test that loading users returns file contents. """
        self.save_users_file({"x": 1})
        self.assertEqual(utils.load_users(), {"x": 1})

    def test_save_users(self):
        """ Test that saving users saves to users.json correctly. """
        data = {"y": 2}
        utils.save_users(data)
        with open(self.users_path) as f:
            result = json.load(f)
        self.assertEqual(result, data)

    def test_create_repo_entry_structure(self):
        entry = utils.create_repo_entry("myrepo")
        self.assertEqual(entry["name"], "myrepo")
        self.assertIn("created_at", entry)
        self.assertTrue(re.fullmatch(r"\d{4}-\d{2}-\d{2}T.*\+00:00", entry["created_at"]))


    def test_user_profile_sorts_repos_by_created_at_desc(self):
        """ User profile shows newest repo first """
        repo_first = self.create_repo("first", created_at="2024-01-01T00:00:00+00:00")
        repo_latest = self.create_repo("latest", created_at="2025-06-24T00:00:00+00:00")
        self.create_user("alex", repos=[repo_first, repo_latest])

        resp = self.client.get("/alex")
        self.assertTrue(resp.text.find("latest") < resp.text.find("first"))