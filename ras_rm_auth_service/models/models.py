import logging
import structlog
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
