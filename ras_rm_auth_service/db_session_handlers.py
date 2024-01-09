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
        logger.error(
            f"Rolling back database session due to {e.__class__.__name__}",
            error_class=e.__class__.__name__,
            pool_size=current_app.db.engine.pool.size(),
            connections_in_pool=current_app.db.engine.pool.checkedin(),
            connections_checked_out=current_app.db.engine.pool.checkedout(),
            current_overflow=current_app.db.engine.pool.overflow(),
        )
        session.rollback()
        raise
    except Exception as e:
        logger.error("Unknown error raised when committing to database", error_class=e.__class__.__name__)
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
        logger.error(
            "Error reading from database",
            error_class=e.__class__.__name__,
            pool_size=current_app.db.engine.pool.size(),
            connections_in_pool=current_app.db.engine.pool.checkedin(),
            connections_checked_out=current_app.db.engine.pool.checkedout(),
            current_overflow=current_app.db.engine.pool.overflow(),
        )
        raise
    except Exception as e:
        logger.error("Unknown error raised when accessing database", error_class=e.__class__.__name__)
        raise
    finally:
        session.close()
