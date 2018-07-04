from django.test import TestCase
from ..models import User


class UserTestCase(TestCase):
    def test_has_verified_field_defaults_to_false(self):
        user = User.objects.create_user(username="test")
        self.assertEqual(False, user.is_verified)

    def test_has_verified_field_returns_set_value_if_set(self):
        user = User.objects.create_user(username="test")
        user.is_verified = True
        self.assertEqual(True, user.is_verified)

    def test_hash_field_defaults_to_none(self):
        user = User.objects.create_user(username="test")
        self.assertEqual(None, user.alternative_hash)

    def test_hash_field_returns_value_if_set(self):
        user = User.objects.create_user(username="test")
        user.alternative_hash = '$pbkdf2-sha256$29000$N2YMIWQsBWBMae09x1jrPQ$1t8iyB2A.WF/Z5JZv.lfCIhXXN33N23OSgQYThBYRfk'
        self.assertEqual('$pbkdf2-sha256$29000$N2YMIWQsBWBMae09x1jrPQ$1t8iyB2A.WF/Z5JZv.lfCIhXXN33N23OSgQYThBYRfk',
                         user.alternative_hash)
