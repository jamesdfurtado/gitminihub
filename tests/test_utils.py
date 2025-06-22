# Just to clarify, this is a test for utils.py, it's not helper functions.

import json
import os
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
