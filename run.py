import logging
import os

from alembic import command
from alembic.config import Config
from flask import Flask, _app_ctx_stack
from retrying import retry, RetryError
from sqlalchemy import create_engine, column, text
from sqlalchemy.exc import DatabaseError, ProgrammingError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import exists, select
from structlog import wrap_logger

from ras_rm_auth_service.logger_config import logger_initial_config

logger = wrap_logger(logging.getLogger(__name__))


def create_app(config=None):
    app = Flask(__name__)

    app_config = f"config.{config or os.environ.get('APP_SETTINGS', 'Config')}"
    app.config.from_object(app_config)
    app.name = 'ras-rm-auth-service'
    logger_initial_config(log_level=app.config['LOGGING_LEVEL'])

    app.url_map.strict_slashes = False

    from ras_rm_auth_service.resources.info import info_view  # NOQA # pylint: disable=wrong-import-position
    from ras_rm_auth_service.resources.account import account  # NOQA # pylint: disable=wrong-import-position
    from ras_rm_auth_service.resources.tokens import tokens  # NOQA # pylint: disable=wrong-import-position
    from ras_rm_auth_service.batch_process_endpoints import batch
    app.register_blueprint(info_view)
    app.register_blueprint(account)
    app.register_blueprint(tokens)
    app.register_blueprint(batch)

    try:
        initialise_db(app)
    except RetryError:
        logger.exception('Failed to initialise database')
        exit(1)

    logger.info('App and database successfully initialised', app_name=app.name, version=app.config['VERSION'])

    return app


def create_database(db_connection, db_schema):
    from ras_rm_auth_service.models import models

    def current_request():
        return _app_ctx_stack.__ident_func__()

    engine = create_engine(db_connection)
    session = scoped_session(sessionmaker(), scopefunc=current_request)
    session.configure(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    engine.session = session

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.attributes['configure_logger'] = False

    if db_connection.startswith('postgres'):
        # fix-up the postgres schema:
        for t in models.Base.metadata.sorted_tables:
            t.schema = db_schema

        q = exists(select([column('schema_name')]).select_from(text("information_schema.schemata"))
                   .where(text(f"schema_name = '{db_schema}'")))

        if not session().query(q).scalar():
            logger.info("Creating schema", schema=db_schema)
            engine.execute(f"CREATE SCHEMA {db_schema}")

            logger.info("Creating database tables.")
            models.Base.metadata.create_all(engine)

            logger.info("Alembic table stamped")
            command.stamp(alembic_cfg, "head")
        else:
            logger.info("Schema exists.", schema=db_schema)

            logger.info("Running Alembic database upgrade")
            command.upgrade(alembic_cfg, "head")
    else:
        logger.info("Creating database tables.")
        models.Base.metadata.create_all(engine)

    return engine


def retry_if_database_error(exception):
    logger.error('Database error has occurred', error=exception)
    return isinstance(exception, DatabaseError) and not isinstance(exception, ProgrammingError)


@retry(retry_on_exception=retry_if_database_error, wait_fixed=2000, stop_max_delay=30000, wrap_exception=True)
def initialise_db(app):
    app.db = create_database(app.config['DATABASE_URI'], app.config['DATABASE_SCHEMA'])


app = create_app()
