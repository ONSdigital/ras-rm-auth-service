import os
from distutils.util import strtobool

from ras_rm_auth_service.cloud.cloudfoundry import ONSCloudFoundry

cf = ONSCloudFoundry()


class Config(object):
    DEBUG = False
    TESTING = False
    VERSION = '0.1.0'
    NAME = 'ras-rm-auth-service'
    DATABASE_SCHEMA = 'auth'
    PORT = os.getenv('PORT', 8041)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD')

    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 5))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 10))
    DB_POOL_RECYCLE = -1

    if cf.detected:
        DATABASE_URI = cf.db.credentials['uri']
    else:
        DATABASE_URI = os.getenv('DATABASE_URI', "postgresql://postgres:postgres@localhost:6432/postgres")

    # Zipkin
    ZIPKIN_DISABLE = bool(strtobool(os.getenv("ZIPKIN_DISABLE", "False")))
    ZIPKIN_DSN = os.getenv("ZIPKIN_DSN", None)
    ZIPKIN_SAMPLE_RATE = int(os.getenv("ZIPKIN_SAMPLE_RATE", 0))


class DevelopmentConfig(Config):
    DEBUG = True
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME', 'admin')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD', 'secret')


class TestingConfig(Config):
    DEBUG = True
    Testing = True
    SECURITY_USER_NAME = 'admin'
    SECURITY_USER_PASSWORD = 'secret'
    DATABASE_URI = os.getenv("TEST_DATABASE_URI", "postgresql://postgres:postgres@localhost:6432/postgres")
