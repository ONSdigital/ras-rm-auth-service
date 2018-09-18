import logging
import os
import unittest

from structlog import wrap_logger
from testfixtures import log_capture

from ras_rm_auth_service.logger_config import logger_initial_config


class TestLoggerConfig(unittest.TestCase):

    @log_capture()
    def test_success(self, l):
        os.environ['JSON_INDENT_LOGGING'] = '1'
        logger_initial_config(service_name='ras-rm-auth-service')
        logger = wrap_logger(logging.getLogger())
        logger.error('Test')
        message = l.records[0].msg

        self.assertIn('"event": "Test",\n ', message)
        self.assertIn('"level": "error",\n ', message)
        self.assertIn('"service": "ras-rm-auth-service",\n ', message)
        self.assertIn('"trace": "",\n ', message)
        self.assertIn('"span": "",\n ', message)
        self.assertIn('"parent": "",\n', message)

    @log_capture()
    def test_indent_type_error(self, l):
        os.environ['JSON_INDENT_LOGGING'] = 'abc'
        logger_initial_config(service_name='ras-rm-auth-service')
        logger = wrap_logger(logging.getLogger())
        logger.error('Test')
        message = l.records[0].msg
        self.assertIn('"event": "Test", ', message)
        self.assertIn('"level": "error", ', message)
        self.assertIn('"service": "ras-rm-auth-service", ', message)
        self.assertIn('"trace": "", ', message)
        self.assertIn('"span": "", ', message)
        self.assertIn('"parent": "", ', message)

    @log_capture()
    def test_indent_value_error(self, l):
        logger_initial_config(service_name='ras-rm-auth-service')
        logger = wrap_logger(logging.getLogger())
        logger.error('Test')
        message = l.records[0].msg
        self.assertIn('"event": "Test", ', message)
        self.assertIn('"level": "error", ', message)
        self.assertIn('"service": "ras-rm-auth-service", ', message)
        self.assertIn('"trace": "", ', message)
        self.assertIn('"span": "", ', message)
        self.assertIn('"parent": "", ', message)
