import logging
from datetime import datetime, timezone
from distutils.util import strtobool

import bcrypt
from marshmallow import Schema, fields, validate
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base
from structlog import wrap_logger
from werkzeug.exceptions import Unauthorized

ACCOUNT_NOT_VERIFIED = "User account not verified"
UNAUTHORIZED_USER_CREDENTIALS = "Unauthorized user credentials"
USER_ACCOUNT_LOCKED = "User account locked"
USER_ACCOUNT_DELETED = "User account deleted"
MAX_FAILED_LOGINS = 10

Base = declarative_base()
logger = wrap_logger(logging.getLogger(__name__))


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True)
    hashed_password = Column(Text, nullable=False)
    account_verified = Column(Boolean, default=False, nullable=False)
    account_locked = Column(Boolean, default=False, nullable=False)
    failed_logins = Column(Integer, default=0, nullable=False)
    last_login_date = Column(DateTime, default=None, nullable=True)
    account_creation_date = Column(DateTime, default=datetime.utcnow)
    first_notification = Column(DateTime, default=None, nullable=True)
    second_notification = Column(DateTime, default=None, nullable=True)
    third_notification = Column(DateTime, default=None, nullable=True)
    mark_for_deletion = Column(Boolean, default=False)
    force_delete = Column(Boolean, default=False)

    def update_user(self, update_params):
        self.username = update_params.get("new_username", self.username)

        if "account_verified" in update_params:
            self.account_verified = strtobool(update_params["account_verified"])
            if self.mark_for_deletion and not self.force_delete:
                self.mark_for_deletion = False

        if "password" in update_params:
            self.set_hashed_password(update_params["password"])

        if "account_locked" in update_params and not strtobool(update_params["account_locked"]):
            self.unlock_account()

    def failed_login(self):
        self.failed_logins += 1

        if self.failed_logins >= MAX_FAILED_LOGINS:
            logger.info("Maximum failed logins reached, locking account", user_id=id)
            self.account_locked = True

    def reset_failed_logins(self):
        self.failed_logins = 0

    def unlock_account(self):
        logger.info("Unlocking account", user_id=id)
        self.reset_failed_logins()
        self.account_locked = False
        self.account_verified = True
        if not self.force_delete:
            self.mark_for_deletion = False

    def set_hashed_password(self, string_password):
        logger.info("Changing password for account", user_id=id)
        self.hashed_password = bcrypt.hashpw(string_password.encode("utf-8"), bcrypt.gensalt(12))

    def is_correct_password(self, string_password):
        check_password = self.hashed_password
        if isinstance(check_password, str):
            check_password = check_password.encode("utf8")
        logger.error(type(check_password))

        return bcrypt.checkpw(string_password.encode("utf8"), check_password)

    def authorise(self, password):
        if not self.is_correct_password(password):
            self.failed_login()

            if self.account_locked:
                raise Unauthorized(description=USER_ACCOUNT_LOCKED)

            raise Unauthorized(description=UNAUTHORIZED_USER_CREDENTIALS)

        if self.account_locked:
            raise Unauthorized(description=USER_ACCOUNT_LOCKED)

        if not self.account_verified:
            raise Unauthorized(description=ACCOUNT_NOT_VERIFIED)

        if self.force_delete:
            raise Unauthorized(description=USER_ACCOUNT_DELETED)

        self.reset_failed_logins()
        self.update_last_login_date()
        self.reset_due_deletion()

        return True

    def update_last_login_date(self):
        self.last_login_date = datetime.now(timezone.utc)

    def reset_due_deletion(self):
        if not self.force_delete:
            self.mark_for_deletion = False
        self.first_notification = None
        self.second_notification = None
        self.third_notification = None

    def to_user_dict(self):
        d = {
            "first_notification": self.first_notification,
            "second_notification": self.second_notification,
            "third_notification": self.third_notification,
            "mark_for_deletion": self.mark_for_deletion,
        }
        return d

    def patch_user(self, patch_params):
        self.mark_for_deletion = patch_params.get("mark_for_deletion", self.mark_for_deletion)
        self.first_notification = patch_params.get("first_notification", self.first_notification)
        self.second_notification = patch_params.get("second_notification", self.second_notification)
        self.third_notification = patch_params.get("third_notification", self.third_notification)
        self.force_delete = patch_params.get("force_delete", self.force_delete)


class AccountSchema(Schema):
    """Account data which is required for the operation of runner itself"""

    username = fields.String(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True, validate=validate.Length(min=1))


class PatchAccountSchema(Schema):
    """Account data which is required for the operation patch"""

    mark_for_deletion = fields.Boolean(required=False)
    first_notification = fields.DateTime(required=False)
    second_notification = fields.DateTime(required=False)
    third_notification = fields.DateTime(required=False)
    force_delete = fields.Boolean(required=False)
