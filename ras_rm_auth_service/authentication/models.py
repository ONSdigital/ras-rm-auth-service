from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
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
