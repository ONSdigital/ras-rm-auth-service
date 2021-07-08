import unittest

from ras_rm_auth_service.basic_auth import get_pw
from run import create_app


class TestBasicAuth(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")

    def test_get_pw(self):
        with self.app.app_context():
            password = get_pw(self.app.config.get("SECURITY_USER_NAME"))
            self.assertEqual(password, self.app.config.get("SECURITY_USER_PASSWORD"))
