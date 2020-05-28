import os


class Config(object):
    DEBUG = False
    TESTING = False
    VERSION = '0.3.0'
    DATABASE_SCHEMA = 'auth'
    PORT = os.getenv('PORT', 8041)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD')
    DATABASE_URI = os.getenv('DATABASE_URI', "postgresql://postgres:postgres@localhost:5432/postgres")


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
    DATABASE_URI = os.getenv("TEST_DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres")
