import logging
from distutils.util import strtobool

import structlog
from passlib.hash import bcrypt
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
logger = structlog.wrap_logger(logging.getLogger(__name__))


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True)
    hash = Column(Text, nullable=False)
    is_verified = Column(Boolean, default=False)

    def update_user(self, update_params):
        self.username = update_params.get('new_username', self.username)

        if 'account_verified' in update_params:
            self.is_verified = strtobool(update_params['account_verified'])

        if 'password' in update_params:
            self.hash = bcrypt.using(rounds=12).hash(update_params['password'])
