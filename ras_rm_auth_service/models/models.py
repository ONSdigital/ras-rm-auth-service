import logging
from datetime import datetime, timezone
from distutils.util import strtobool

from marshmallow import Schema, fields, validate
from structlog import wrap_logger
from passlib.hash import bcrypt
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.exceptions import Unauthorized

ACCOUNT_NOT_VERIFIED = "User account not verified"
UNAUTHORIZED_USER_CREDENTIALS = "Unauthorized user credentials"
USER_ACCOUNT_LOCKED = "User account locked"
MAX_FAILED_LOGINS = 10

Base = declarative_base()
logger = wrap_logger(logging.getLogger(__name__))


class User(Base):
    __tablename__ = 'user'

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

    def update_user(self, update_params):
        self.username = update_params.get('new_username', self.username)

        if 'account_verified' in update_params:
            self.account_verified = strtobool(update_params['account_verified'])

        if 'password' in update_params:
            self.set_hashed_password(update_params['password'])

        if 'account_locked' in update_params and not strtobool(update_params['account_locked']):
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

    def set_hashed_password(self, string_password):
        logger.info("Changing password for account", user_id=id)
        self.hashed_password = bcrypt.using(rounds=12).hash(string_password)

    def is_correct_password(self, string_password):
        return bcrypt.verify(string_password, self.hashed_password)

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

        self.reset_failed_logins()
        self.update_last_login_date()
        self.reset_due_deletion_dates()

        return True

    def update_last_login_date(self):
        self.last_login_date = datetime.now(timezone.utc)

    def reset_due_deletion_dates(self):
        self.first_notification = None
        self.second_notification = None
        self.third_notification = None


class AccountSchema(Schema):
    """ Account data which is required for the operation of runner itself
    """
    username = fields.String(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True, validate=validate.Length(min=1))
