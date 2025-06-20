import json
import os
from tests.test_helpers import UserJsonTestCase
from app.pages import utils

class UtilsTests(UserJsonTestCase):
    def test_load_users_no_file(self):
        # delete file to simulate non-existence
        if self.users_path and os.path.exists(self.users_path):
            os.remove(self.users_path)
        self.assertEqual(utils.load_users(), {})

    def test_load_users_with_file(self):
        with open(self.users_path, "w") as f:
            json.dump({"x": 1}, f)
        self.assertEqual(utils.load_users(), {"x": 1})

    def test_save_users(self):
        data = {"y": 2}
        utils.save_users(data)
        with open(self.users_path) as f:
            result = json.load(f)
        self.assertEqual(result, data)
