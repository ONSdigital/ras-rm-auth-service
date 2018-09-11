import unittest

from passlib.hash import bcrypt

from ras_rm_auth_service.models.models import User


class TestModel(unittest.TestCase):

    def test_use_has_verified_field_returns_set_value_if_set(self):
        user = User(username="test", is_verified=True)
        self.assertEqual(True, user.is_verified)

    def test_user_hash_field_returns_value_if_set(self):
        h = '$pbkdf2-sha256$29000$N2YMIWQsBWBMae09x1jrPQ$1t8iyB2A.WF/Z5JZv.lfCIhXXN33N23OSgQYThBYRfk'
        user = User(username="test", hash=h)
        self.assertEqual(h, user.hash)

    def test_user_username_field_returns_set_value_if_set(self):
        user = User(username="test")
        user.username = "another"
        self.assertEqual("another", user.username)

    def test_user_defaults_username_to_username_from_create(self):
        user = User(username="test")
        self.assertEqual("test", user.username)

    def test_update_user_email(self):
        user = User(username="test")
        update_params = {"new_username": "another-username"}
        user.update_user(update_params)
        self.assertEqual("another-username", user.username)

    def test_update_user_is_verified(self):
        user = User(username="test", is_verified=False)
        update_params = {"account_verified": "true"}
        user.update_user(update_params)
        self.assertEqual(True, user.is_verified)

    def test_update_user_password(self):
        user = User(username="test", is_verified=False, hash="h4$HedPassword")
        update_params = {"password": "newpassword"}
        user.update_user(update_params)
        self.assertTrue(bcrypt.verify("newpassword", user.hash))
