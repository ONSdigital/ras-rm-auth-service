import logging
import os
import sys

from structlog import configure, wrap_logger
from structlog.processors import JSONRenderer, TimeStamper, format_exc_info
from structlog.stdlib import add_log_level, filter_by_level

logger_date_format = os.getenv("LOGGING_DATE_FORMAT", "%Y-%m-%dT%H:%M%s")
log_level = os.getenv("LOGGING_LEVEL", 20)


def add_severity_level(process_name, method_name, event_dict):
    # as we are extending structlog processor, it passes three attributes by default
    # although I am only using two attributes. Please ignore process_name
    if method_name == "warn":
        # The stdlib has an alias warn for warning
        # this method name is not understood by logging api
        # hence changing to warning
        method_name = "warning"
    event_dict["severity"] = method_name
    return event_dict


logging.basicConfig(stream=sys.stdout, level=log_level, format="%(message)s")
configure(
    processors=[
        add_severity_level,
        add_log_level,
        filter_by_level,
        format_exc_info,
        TimeStamper(fmt="%Y-%m-%dT%H:%M%s", utc=True, key="created_at"),
        JSONRenderer(indent=None),
    ]
)

logger = wrap_logger(logging.getLogger(__name__))
