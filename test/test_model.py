import unittest
from datetime import datetime, timedelta

import bcrypt
from freezegun import freeze_time
from werkzeug.exceptions import Unauthorized

from ras_rm_auth_service.models.models import MAX_FAILED_LOGINS, User

TIME_TO_FREEZE = datetime(2024, 1, 1, 12, 0, 0)


class TestModel(unittest.TestCase):
    def test_user_has_verified_field_returns_set_value_if_set(self):
        user = User(username="test", account_verified=True)
        self.assertTrue(user.account_verified)

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
        self.assertTrue(user.account_locked)

    def test_user_defaults_username_to_username_from_create(self):
        user = User(username="test")
        self.assertEqual("test", user.username)

    def test_update_user_email(self):
        user = User(username="test")
        update_params = {"new_username": "another-username"}
        user.update_user(update_params)
        self.assertEqual("another-username", user.username)

    @freeze_time(TIME_TO_FREEZE)
    def test_update_user_account_verified(self):
        user = User(username="test", account_verified=False)
        update_params = {"account_verified": "true"}
        user.update_user(update_params)
        self.assertTrue(user.account_verified)
        self.assertEqual(datetime.utcnow(), user.account_verification_date)

    def test_update_user_password(self):
        user = User(username="test", account_verified=False, hashed_password="h4$HedPassword")
        update_params = {"password": "newpassword"}
        user.update_user(update_params)
        string_password = "newpassword"
        self.assertTrue(bcrypt.checkpw(string_password.encode("utf8"), user.hashed_password.encode("utf-8")))

    def test_update_user_account_locked_and_account_verified(self):
        user = User(username="test", account_verified=False, account_locked=True)
        update_params = {"account_locked": "false"}
        user.update_user(update_params)
        self.assertFalse(user.account_locked)
        self.assertTrue(user.account_verified)

    def test_failed_login_increments_failed_logins_count(self):
        user = User(failed_logins=0)
        user.failed_login()
        self.assertEqual(1, user.failed_logins)

    def test_failed_login_locks_account_after_max_failed_attempts(self):
        user = User(failed_logins=MAX_FAILED_LOGINS - 1, account_locked=False)
        user.failed_login()
        self.assertTrue(user.account_locked)

    def test_unlock_account_resets_failed_logins(self):
        user = User(failed_logins=13, account_locked=True)
        user.unlock_account()
        self.assertEqual(0, user.failed_logins)

    def test_unlock_account_unlocks_account(self):
        user = User(failed_logins=13, account_locked=True)
        user.unlock_account()
        self.assertFalse(user.account_locked)

    def test_unlock_account_verifies_account(self):
        user = User(failed_logins=13, account_verified=False, account_locked=True)
        user.unlock_account()
        self.assertTrue(user.account_verified)

    def test_set_hashed_password(self):
        user = User()
        user.set_hashed_password("password")
        string_password = "password"
        self.assertTrue(bcrypt.checkpw(string_password.encode("utf8"), user.hashed_password.encode("utf-8")))

    def test_is_correct_password_true(self):
        user = User()
        user.set_hashed_password("password")
        self.assertTrue(user.is_correct_password("password"))

    def test_is_correct_password_false(self):
        user = User()
        user.set_hashed_password("password")
        self.assertFalse(user.is_correct_password("wrongpassword"))

    def test_authorise_successfully_authorised(self):
        password = "password"
        user = User(
            account_locked=False,
            account_verified=True,
            hashed_password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            failed_logins=0,
        )

        authorised = user.authorise("password")

        self.assertTrue(authorised)

    def test_authorise_successfully_authorised_resets_failed_logins(self):
        password = "password"
        user = User(
            account_locked=False,
            account_verified=True,
            hashed_password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            failed_logins=5,
        )

        authorised = user.authorise("password")

        self.assertTrue(authorised)
        self.assertEqual(0, user.failed_logins)

    def test_authorise_wrong_password(self):
        password = "password"
        user = User(
            account_locked=False,
            account_verified=True,
            hashed_password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            failed_logins=0,
        )

        with self.assertRaises(Unauthorized) as err:
            user.authorise("wrongpassword")

        self.assertEqual("Unauthorized user credentials", err.exception.description)
        self.assertEqual(1, user.failed_logins)

    def test_authorise_wrong_password_user_becomes_locked(self):
        password = "password"
        user = User(
            account_locked=False,
            account_verified=True,
            hashed_password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            failed_logins=MAX_FAILED_LOGINS - 1,
        )

        with self.assertRaises(Unauthorized) as err:
            user.authorise("wrongpassword")

        self.assertEqual("User account locked", err.exception.description)
        self.assertEqual(MAX_FAILED_LOGINS, user.failed_logins)

    def test_authorise_correct_password_but_user_is_locked(self):
        password = "password"
        user = User(
            account_locked=True,
            account_verified=True,
            hashed_password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            failed_logins=0,
        )

        with self.assertRaises(Unauthorized) as err:
            user.authorise("password")

        self.assertEqual("User account locked", err.exception.description)

    def test_authorise_correct_password_but_user_is_not_verified(self):
        password = "password"
        user = User(
            account_locked=False,
            account_verified=False,
            hashed_password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            failed_logins=0,
        )

        with self.assertRaises(Unauthorized) as err:
            user.authorise("password")

        self.assertEqual("User account not verified", err.exception.description)

    def test_last_login_date_field_exists_and_defaults_to_none(self):
        user = User(username="test")
        self.assertIsNone(user.last_login_date)

    def test_last_login_date_gets_filled_in_when_authorising(self):
        password = "password"
        user = User(
            account_locked=False,
            account_verified=True,
            hashed_password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            failed_logins=0,
        )

        user.authorise("password")

        self.assertIsNotNone(user.last_login_date)

    @freeze_time(TIME_TO_FREEZE)
    def test_user_verifies_email_update_also_updates_verification_timestamp(self):
        user = User(
            username="test", account_verified=True, account_verification_date=datetime.utcnow() - timedelta(minutes=1)
        )
        update_params = {"new_username": "another-username", "account_verified": "true"}
        user.update_user(update_params)
        self.assertEqual(user.username, update_params["new_username"])
        self.assertTrue(user.account_verified)
        self.assertEqual(datetime.utcnow(), user.account_verification_date)

    @freeze_time(TIME_TO_FREEZE)
    def test_user_updates_password_does_not_update_verification_timestamp(self):
        password = "password"
        verification_date = datetime.utcnow() - timedelta(minutes=1)
        user = User(
            username="test",
            account_verified=True,
            hashed_password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            account_verification_date=verification_date,
        )
        update_params = {"password": "new-password", "account_locked": "false"}
        user.update_user(update_params)
        self.assertTrue(bcrypt.checkpw(update_params["password"].encode("utf8"), user.hashed_password.encode("utf-8")))
        self.assertFalse(user.account_locked)
        self.assertEqual(verification_date, user.account_verification_date)

    def test_user_unlocks_account_does_not_update_verification_timestamp(self):
        verification_date = datetime.utcnow() - timedelta(minutes=1)
        user = User(
            username="test", account_verified=True, account_locked=True, account_verification_date=verification_date
        )
        update_params = {"account_locked": "false"}
        user.update_user(update_params)
        self.assertFalse(user.account_locked)
        self.assertEqual(verification_date, user.account_verification_date)

    def test_user_dict(self):
        expected_user_dict = {
            "first_notification": datetime.utcnow(),
            "second_notification": None,
            "third_notification": None,
            "mark_for_deletion": False,
            "account_verification_date": datetime.utcnow(),
        }
        user = User(
            first_notification=expected_user_dict["first_notification"],
            second_notification=expected_user_dict["second_notification"],
            third_notification=expected_user_dict["third_notification"],
            mark_for_deletion=expected_user_dict["mark_for_deletion"],
            account_verification_date=expected_user_dict["account_verification_date"],
        )

        self.assertEqual(expected_user_dict, user.to_user_dict())
