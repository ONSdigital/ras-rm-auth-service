import logging
from contextlib import contextmanager

import structlog
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from retrying import RetryError
logger = structlog.wrap_logger(logging.getLogger(__name__))


def retry_if_sql_error(exception):
    return isinstance(exception, OperationalError)


@contextmanager
def transactional_session():
    """Provide a transactional scope around a series of operations."""
    session = current_app.db.session()
    try:
        logger.info("before session yield")
        yield session
        logger.info("after session yield")
        session.commit()
        logger.info("after commit")
    except SQLAlchemyError as e:
        # not logging exception as it may have sensitive data
        logger.error(
            "Error committing to database",
            error_class=e.__class__.__name__,
            pool_size=current_app.db.engine.pool.size(),
            connections_in_pool=current_app.db.engine.pool.checkedin(),
            connections_checked_out=current_app.db.engine.pool.checkedout(),
            current_overflow=current_app.db.engine.pool.overflow(),
        )
        session.rollback()
        logger.info("before raise 1")
        raise
    except RetryError as e:
        logger.error("Too many retries", error_class=e.__class__.__name__)
        session.rollback()
        logger.info("before raise 2")
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
        logger.error(
            "Error reading from database",
            error_class=e.__class__.__name__,
            pool_size=current_app.db.engine.pool.size(),
            connections_in_pool=current_app.db.engine.pool.checkedin(),
            connections_checked_out=current_app.db.engine.pool.checkedout(),
            current_overflow=current_app.db.engine.pool.overflow(),
        )
        raise
    except RetryError as e:
        logger.error("Too many retries", error_class=e.__class__.__name__)
        raise
    finally:
        session.close()
