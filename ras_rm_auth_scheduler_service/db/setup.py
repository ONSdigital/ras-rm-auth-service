from sqlalchemy import create_engine
import config as cfg

from ras_rm_auth_scheduler_service.scheduled_jobs.helper import logger as log, AuthDueDeletionSchedulerError


def get_database():
    try:
        engine = get_engine()
        log.info("Connected to database!")
    except IOError:
        log.exception("Failed to get database connection!")
        raise IOError

    return engine


def get_engine():
    """
    Get SQLalchemy engine using credentials.
    Input:
    db: database name
    user: Username
    host: Hostname of the database server
    port: Port number
    passwd: Password for the database
    """

    url = cfg.Config.DATABASE_URI
    engine = create_engine(url, pool_size=50)
    return engine


def get_connection():
    try:
        con = get_database().raw_connection()
        con.cursor().execute("SET SCHEMA '{}'".format(cfg.Config.DATABASE_SCHEMA))
    except Exception:
        raise AuthDueDeletionSchedulerError('Unable to establish database connection.')

    return con
