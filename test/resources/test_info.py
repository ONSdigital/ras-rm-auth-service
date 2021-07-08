import json
import os
import unittest
from pathlib import Path

from run import create_app


class TestInfo(unittest.TestCase):
    @staticmethod
    def delete_git_info():
        if Path("git_info").exists():
            os.remove("git_info")

    def setUp(self):
        app = create_app("TestingConfig")
        self.client = app.test_client()
        self.delete_git_info()

    def tearDown(self):
        self.delete_git_info()

    def test_info_no_git_info(self):
        if Path("git_info").exists():
            os.remove("git_info")

        response = self.client.get("/info")
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["name"], "ras-rm-auth-service")
        self.assertIsNone(response_data.get("test"))

    def test_info_with_git_info(self):
        with open("git_info", "w") as outfile:
            json.dump({"test": "test"}, outfile)

        response = self.client.get("/info")
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["name"], "ras-rm-auth-service")
        self.assertEqual(response_data["test"], "test")
