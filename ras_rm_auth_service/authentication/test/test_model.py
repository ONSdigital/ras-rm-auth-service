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
