import logging
import os
import sys

import flask
from flask import g
from structlog import configure
from structlog.stdlib import add_log_level, filter_by_level
from structlog.processors import JSONRenderer, TimeStamper


def logger_initial_config(log_level=None):
    """Configures the logger"""
    service_name = 'ras-rm-auth-service'
    logger_date_format = os.getenv('LOGGING_DATE_FORMAT', "%Y-%m-%dT%H:%M%s")
    logger_format = "%(message)s"

    if not log_level:
        log_level = os.getenv('SMS_LOG_LEVEL', 'INFO')

    try:
        indent = int(os.getenv('JSON_INDENT_LOGGING'))
    except (TypeError, ValueError):
        indent = None

    def add_service(logger, method_name, event_dict):  # pylint: disable=unused-argument
        """
        Add the service name to the event dict.
        """
        event_dict['service'] = service_name
        return event_dict

    def zipkin_ids(logger, method_name, event_dict):  # pylint: disable=unused-argument
        event_dict['trace'] = ''
        event_dict['span'] = ''
        event_dict['parent'] = ''
        if not flask.has_app_context():
            return event_dict
        if '_zipkin_span' not in g:
            return event_dict
        event_dict['span'] = g._zipkin_span.zipkin_attrs.span_id
        event_dict['trace'] = g._zipkin_span.zipkin_attrs.trace_id
        event_dict['parent'] = g._zipkin_span.zipkin_attrs.parent_span_id
        return event_dict

    logging.basicConfig(stream=sys.stdout, level=log_level, format=logger_format)
    configure(processors=[zipkin_ids, add_log_level, filter_by_level, add_service,
                          TimeStamper(fmt=logger_date_format, utc=True, key="created_at"), JSONRenderer(indent=indent)])
    oauth_log = logging.getLogger("requests_oauthlib")
    oauth_log.addHandler(logging.NullHandler())
    oauth_log.propagate = False
