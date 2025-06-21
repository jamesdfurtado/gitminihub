# Just to clarify, these are helper functions for the test cases

import os
import json
import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.pages import utils

class UserJsonTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.users_path = "tests/users.json"
        self._backup = None

        if os.path.exists(self.users_path):
            with open(self.users_path, "r") as f:
                self._backup = json.load(f)
        else:
            os.makedirs(os.path.dirname(self.users_path), exist_ok=True)
            with open(self.users_path, "w") as f:
                json.dump({}, f)

        utils.users_path = self.users_path

    def tearDown(self):
        if self._backup is not None:
            with open(self.users_path, "w") as f:
                json.dump(self._backup, f)
