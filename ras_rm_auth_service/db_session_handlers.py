import logging
from contextlib import contextmanager

import structlog
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

logger = structlog.wrap_logger(logging.getLogger(__name__))


@contextmanager
def transactional_session():
    """Provide a transactional scope around a series of operations."""
    session = current_app.db.session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        # not logging exception as it may have sensitive data
        logger.info(
            "Error committing to database, rolling back",
            error_class=e.__class__.__name__,
        )
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def non_transactional_session():
    """Provide a non transactional scope db session."""
    session = current_app.db.session()
    try:
        yield session
    except SQLAlchemyError as e:
        # not logging exception as it may have sensitive data
        logger.info(
            "Error reading from database",
            error_class=e.__class__.__name__,
        )
        raise
    finally:
        session.close()
