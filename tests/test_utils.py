import os
import json
import unittest
from app.pages import utils

class UtilsTests(unittest.TestCase):
    def setUp(self):
        self.test_file = "tests/temp_users.json"
        utils.users_path = self.test_file

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_load_users_no_file(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.assertEqual(utils.load_users(), {})

    def test_load_users_with_file(self):
        with open(self.test_file, "w") as f:
            json.dump({"x": 1}, f)
        self.assertEqual(utils.load_users(), {"x": 1})

    def test_save_users(self):
        data = {"y": 2}
        utils.save_users(data)
        with open(self.test_file) as f:
            result = json.load(f)
        self.assertEqual(result, data)
