import json
import os
import re
from datetime import datetime
from tests.test_helpers import AppTestCase
from app.pages import utils

class UtilsTests(AppTestCase):

    def test_load_users_no_file(self):
        """ Test that loading users with empty users.json doesn't crash. """
        if self.users_path and os.path.exists(self.users_path):
            os.remove(self.users_path)
        self.assertEqual(utils.load_users(), {})

    def test_load_users_with_file(self):
        """ Test that loading users returns file contents. """
        with open(self.users_path, "w") as f:
            json.dump({"x": 1}, f)
        self.assertEqual(utils.load_users(), {"x": 1})

    def test_save_users(self):
        """ Test that saving users saves to users.json correctly. """
        data = {"y": 2}
        utils.save_users(data)
        with open(self.users_path) as f:
            result = json.load(f)
        self.assertEqual(result, data)

    def test_create_repo_entry_structure(self):
        """ Repos in users.json have correct fields/types. """
        entry = utils.create_repo_entry("myrepo")
        self.assertEqual(entry["name"], "myrepo")
        self.assertIn("created_at", entry)
        self.assertIn("path", entry)
        self.assertEqual(entry["path"], "")
        self.assertTrue(re.fullmatch(r"\d{4}-\d{2}-\d{2}T.*\+00:00", entry["created_at"]))

    def test_homepage_lists_all_repos_reverse_chronologically(self):
        """ Homepage lists all repos in reverse chronological order. """
        users = {
            "a": {
                "password_hash": "x",
                "repos": [
                    {"name": "old", "created_at": "2023-01-01T00:00:00+00:00", "path": ""}
                ]
            },
            "b": {
                "password_hash": "y",
                "repos": [
                    {"name": "new", "created_at": "2025-01-01T00:00:00+00:00", "path": ""}
                ]
            }
        }
        with open(self.users_path, "w") as f:
            json.dump(users, f)

        resp = self.client.get("/")
        first_index = resp.text.find("b/new")
        second_index = resp.text.find("a/old")
        self.assertTrue(first_index < second_index)

    def test_user_profile_sorts_repos_by_created_at_desc(self):
        """ User profile shows newest repo first """
        user_data = {
            "alex": {
                "password_hash": "z",
                "repos": [
                    {"name": "first", "created_at": "2024-01-01T00:00:00+00:00", "path": ""},
                    {"name": "latest", "created_at": "2025-06-24T00:00:00+00:00", "path": ""}
                ]
            }
        }
        with open(self.users_path, "w") as f:
            json.dump(user_data, f)

        resp = self.client.get("/alex")
        self.assertTrue(resp.text.find("latest") < resp.text.find("first"))
