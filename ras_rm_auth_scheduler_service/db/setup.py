from sqlalchemy import create_engine

import config as cfg
from ras_rm_auth_scheduler_service.helper import AuthDueDeletionSchedulerError
from ras_rm_auth_scheduler_service.logger import logger


def _get_database():
    try:
        engine = _get_engine()
        logger.info("Connected to database!")
    except IOError:
        logger.exception("Failed to get database connection!")
        raise IOError

    return engine


def _get_engine():
    """
    Get SQLalchemy engine using URL.
    """

    url = cfg.Config.DATABASE_URI
    engine = create_engine(url, pool_size=50)
    return engine


def get_connection():
    """
    Get DB connection
    """
    try:
        con = _get_database().raw_connection()
        con.cursor().execute("SET SCHEMA '{}'".format(cfg.Config.DATABASE_SCHEMA))
    except Exception as e:
        logger.exception(e)
        raise AuthDueDeletionSchedulerError("Unable to establish database connection.")

    return con
