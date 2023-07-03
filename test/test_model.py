import unittest

import bcrypt
from werkzeug.exceptions import Unauthorized

from ras_rm_auth_service.models.models import MAX_FAILED_LOGINS, User


class TestModel(unittest.TestCase):
    def test_use_has_verified_field_returns_set_value_if_set(self):
        user = User(username="test", account_verified=True)
        self.assertEqual(True, user.account_verified)

    def test_user_hashed_password_field_returns_value_if_set(self):
        h = "$pbkdf2-sha256$29000$N2YMIWQsBWBMae09x1jrPQ$1t8iyB2A.WF/Z5JZv.lfCIhXXN33N23OSgQYThBYRfk"
        user = User(username="test", hashed_password=h)
        self.assertEqual(h, user.hashed_password)

    def test_user_username_field_returns_set_value_if_set(self):
        user = User(username="test")
        self.assertEqual("test", user.username)

    def test_user_failed_logins_returns_set_value_if_set(self):
        user = User(failed_logins=1)
        self.assertEqual(1, user.failed_logins)

    def test_user_account_locked_returns_set_value_if_set(self):
        user = User(account_locked=True)
        self.assertEqual(True, user.account_locked)

    def test_user_defaults_username_to_username_from_create(self):
        user = User(username="test")
        self.assertEqual("test", user.username)

    def test_update_user_email(self):
        user = User(username="test")
        update_params = {"new_username": "another-username"}
        user.update_user(update_params)
        self.assertEqual("another-username", user.username)

    def test_update_user_account_verified(self):
        user = User(username="test", account_verified=False)
        update_params = {"account_verified": "true"}
        user.update_user(update_params)
        self.assertEqual(True, user.account_verified)

    def test_update_user_password(self):
        user = User(username="test", account_verified=False, hashed_password="h4$HedPassword")
        update_params = {"password": "newpassword"}
        user.update_user(update_params)
        string_password = "newpassword"
        self.assertTrue(bcrypt.checkpw(string_password.encode("utf8"), user.hashed_password))

    def test_update_user_account_locked_and_account_verified(self):
        user = User(username="test", account_verified=False, account_locked=True)
        update_params = {"account_locked": "false"}
        user.update_user(update_params)
        self.assertEqual(False, user.account_locked)
        self.assertEqual(True, user.account_verified)

    def test_failed_login_increments_failed_logins_count(self):
        user = User(failed_logins=0)
        user.failed_login()
        self.assertEqual(1, user.failed_logins)

    def test_failed_login_locks_account_after_max_failed_attempts(self):
        user = User(failed_logins=MAX_FAILED_LOGINS - 1, account_locked=False)
        user.failed_login()
        self.assertEqual(True, user.account_locked)

    def test_unlock_account_resets_failed_logins(self):
        user = User(failed_logins=13, account_locked=True)
        user.unlock_account()
        self.assertEqual(0, user.failed_logins)

    def test_unlock_account_unlocks_account(self):
        user = User(failed_logins=13, account_locked=True)
        user.unlock_account()
        self.assertEqual(False, user.account_locked)

    def test_unlock_account_verifies_account(self):
        user = User(failed_logins=13, account_verified=False, account_locked=True)
        user.unlock_account()
        self.assertEqual(True, user.account_verified)

    def test_set_hashed_password(self):
        user = User()
        user.set_hashed_password("password")
        string_password = "password"
        self.assertTrue(bcrypt.checkpw(string_password.encode("utf8"), user.hashed_password))

    def test_is_correct_password_true(self):
        user = User()
        user.set_hashed_password("password")
        self.assertTrue(user.is_correct_password("password"))

    def test_is_correct_password_false(self):
        user = User()
        user.set_hashed_password("password")
        self.assertFalse(user.is_correct_password("wrongpassword"))

    def test_authorise_successfully_authorised(self):
        user = User(
            account_locked=False,
            account_verified=True,
            hashed_password=bcrypt.hashpw(b"password", bcrypt.gensalt(12)),
            failed_logins=0,
        )

        authorised = user.authorise("password")

        self.assertEqual(True, authorised)

    def test_authorise_successfully_authorised_resets_failed_logins(self):
        user = User(
            account_locked=False,
            account_verified=True,
            hashed_password=bcrypt.hashpw(b"password", bcrypt.gensalt(12)),
            failed_logins=5,
        )

        authorised = user.authorise("password")

        self.assertEqual(True, authorised)
        self.assertEqual(0, user.failed_logins)

    def test_authorise_wrong_password(self):
        user = User(
            account_locked=False,
            account_verified=True,
            hashed_password=bcrypt.hashpw(b"password", bcrypt.gensalt(12)),
            failed_logins=0,
        )

        with self.assertRaises(Unauthorized) as err:
            authorised = user.authorise("wrongpassword")
            self.assertEqual(False, authorised)

        self.assertEqual("Unauthorized user credentials", err.exception.description)
        self.assertEqual(1, user.failed_logins)

    def test_authorise_wrong_password_user_becomes_locked(self):
        user = User(
            account_locked=False,
            account_verified=True,
            hashed_password=bcrypt.hashpw(b"password", bcrypt.gensalt(12)),
            failed_logins=MAX_FAILED_LOGINS - 1,
        )

        with self.assertRaises(Unauthorized) as err:
            authorised = user.authorise("wrongpassword")
            self.assertEqual(False, authorised)

        self.assertEqual("User account locked", err.exception.description)
        self.assertEqual(MAX_FAILED_LOGINS, user.failed_logins)

    def test_authorise_correct_password_but_user_is_locked(self):
        user = User(
            account_locked=True,
            account_verified=True,
            hashed_password=bcrypt.hashpw(b"password", bcrypt.gensalt(12)),
            failed_logins=0,
        )

        with self.assertRaises(Unauthorized) as err:
            authorised = user.authorise("password")
            self.assertEqual(False, authorised)

        self.assertEqual("User account locked", err.exception.description)

    def test_authorise_correct_password_but_user_is_not_verified(self):
        user = User(
            account_locked=False,
            account_verified=False,
            hashed_password=bcrypt.hashpw(b"password", bcrypt.gensalt(12)),
            failed_logins=0,
        )

        with self.assertRaises(Unauthorized) as err:
            authorised = user.authorise("password")
            self.assertEqual(False, authorised)

        self.assertEqual("User account not verified", err.exception.description)

    def test_last_login_date_field_exists_and_defaults_to_none(self):
        user = User(username="test")
        self.assertEqual(None, user.last_login_date)

    def test_last_login_date_gets_filled_in_when_authorising(self):
        user = User(
            account_locked=False,
            account_verified=True,
            hashed_password=bcrypt.hashpw(b"password", bcrypt.gensalt(12)),
            failed_logins=0,
        )

        user.authorise("password")

        self.assertIsNotNone(user.last_login_date)
