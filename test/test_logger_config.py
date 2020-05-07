import logging
import os
import unittest

import pytest
from structlog import wrap_logger
from testfixtures import log_capture

from ras_rm_auth_service.logger_config import logger_initial_config

# Supresses the warnings that won't be fixed by the project maintainer until Python 2 is deprecated.
# More information about this can be found https://github.com/Simplistix/testfixtures/pull/54
# Remove this and the filterwarnings if this problem ever gets fixed.
testfixtures_warning = "inspect.getargspec()"


class TestLoggerConfig(unittest.TestCase):

    @pytest.mark.filterwarnings(f"ignore:{testfixtures_warning}")
    @log_capture()
    def test_success(self, l):
        os.environ['JSON_INDENT_LOGGING'] = '1'
        logger_initial_config()
        logger = wrap_logger(logging.getLogger())
        logger.error('Test')
        message = l.records[0].msg

        self.assertIn('"event": "Test",\n ', message)
        self.assertIn('"severity": "error",\n ', message)
        self.assertIn('"level": "error",\n ', message)
        self.assertIn('"service": "ras-rm-auth-service",\n ', message)

    @pytest.mark.filterwarnings(f"ignore:{testfixtures_warning}")
    @log_capture()
    def test_indent_type_error(self, l):
        os.environ['JSON_INDENT_LOGGING'] = 'abc'
        logger_initial_config()
        logger = wrap_logger(logging.getLogger())
        logger.error('Test')
        message = l.records[0].msg
        self.assertIn('"event": "Test", ', message)
        self.assertIn('"severity": "error", ', message)
        self.assertIn('"level": "error", ', message)
        self.assertIn('"service": "ras-rm-auth-service", ', message)

    @pytest.mark.filterwarnings(f"ignore:{testfixtures_warning}")
    @log_capture()
    def test_indent_value_error(self, l):
        logger_initial_config()
        logger = wrap_logger(logging.getLogger())
        logger.error('Test')
        message = l.records[0].msg
        self.assertIn('"event": "Test", ', message)
        self.assertIn('"severity": "error", ', message)
        self.assertIn('"level": "error", ', message)
        self.assertIn('"service": "ras-rm-auth-service", ', message)
