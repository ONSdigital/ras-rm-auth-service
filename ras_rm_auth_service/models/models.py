import logging
from distutils.util import strtobool

from structlog import wrap_logger
from passlib.hash import bcrypt
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

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
            logger.info("Maximum failed logins reached, locking account")
            self.account_locked = True

    def reset_failed_logins(self):
        self.failed_logins = 0

    def unlock_account(self):
        logger.info("Unlocking account")
        self.reset_failed_logins()
        self.account_locked = False
        self.account_verified = True

    def set_hashed_password(self, string_password):
        self.hashed_password = bcrypt.using(rounds=12).hash(string_password)

    def is_correct_password(self, string_password):
        return bcrypt.verify(string_password, self.hashed_password)

    def authorise(self, password):
        if not self.is_correct_password(password):
            self.failed_login()

            if self.account_locked:
                logger.debug(USER_ACCOUNT_LOCKED)
                return False, USER_ACCOUNT_LOCKED

            logger.debug(UNAUTHORIZED_USER_CREDENTIALS)
            return False, UNAUTHORIZED_USER_CREDENTIALS

        if self.account_locked:
            logger.debug(USER_ACCOUNT_LOCKED)
            return False, USER_ACCOUNT_LOCKED

        if not self.account_verified:
            logger.debug(ACCOUNT_NOT_VERIFIED)
            return False, ACCOUNT_NOT_VERIFIED

        self.reset_failed_logins()

        return True, None
