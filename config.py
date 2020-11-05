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
    PARTY_URL = os.getenv('PARTY_URL')
    AUTH_URL = os.getenv('AUTH_URL', 'http://localhost:8041')
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)
    DUE_DELETION_FIRST_NOTIFICATION_TEMPLATE = os.getenv('DUE_DELETION_FIRST_NOTIFICATION_TEMPLATE',
                                                         'due_deletion_first_notification_templates')
    DUE_DELETION_SECOND_NOTIFICATION_TEMPLATE = os.getenv('DUE_DELETION_SECOND_NOTIFICATION_TEMPLATE',
                                                          'due_deletion_second_notification_templates')
    DUE_DELETION_THIRD_NOTIFICATION_TEMPLATE = os.getenv('DUE_DELETION_THIRD_NOTIFICATION_TEMPLATE',
                                                         'due_deletion_third_notification_templates')
    SEND_EMAIL_TO_GOV_NOTIFY = os.getenv('SEND_EMAIL_TO_GOV_NOTIFY', True)
    PUBSUB_TOPIC = os.getenv('PUBSUB_TOPIC', 'ras-rm-notify-test')
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'test-project-id')


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
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)
    AUTH_URL = os.getenv('AUTH_URL', 'http://localhost:8041')
