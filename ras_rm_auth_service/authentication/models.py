from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(models.Manager):
    def create_user(self, username):
        user = self.create(username=username)
        return user

class User(models.Model):
    username_validator = UnicodeUsernameValidator()

    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_(
            'Designates whether this user has verified their email address. '
        ),
    )
    alternative_hash = models.TextField(
        _('alternative_hash'),
        null=True,
        help_text=_(
            'Passlib based hash. '
        ),
    )
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    objects = UserManager()
