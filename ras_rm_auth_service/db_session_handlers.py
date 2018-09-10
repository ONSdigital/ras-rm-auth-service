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
    except SQLAlchemyError:
        logger.exception("Error committing to database",
                         pool_size=current_app.db.engine.pool.size(),
                         connections_in_pool=current_app.db.engine.pool.checkedin(),
                         connections_checked_out=current_app.db.engine.pool.checkedout(),
                         current_overflow=current_app.db.engine.pool.overflow())
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
    except SQLAlchemyError:
        logger.exception("Error reading from database",
                         pool_size=current_app.db.engine.pool.size(),
                         connections_in_pool=current_app.db.engine.pool.checkedin(),
                         connections_checked_out=current_app.db.engine.pool.checkedout(),
                         current_overflow=current_app.db.engine.pool.overflow())
        raise
    finally:
        session.close()
