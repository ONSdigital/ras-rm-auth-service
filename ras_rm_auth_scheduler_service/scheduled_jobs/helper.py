import logging
import os
import sys

from structlog import configure, wrap_logger
from structlog.processors import format_exc_info, JSONRenderer, TimeStamper
from structlog.stdlib import add_log_level, filter_by_level

logger_date_format = os.getenv('LOGGING_DATE_FORMAT', "%Y-%m-%dT%H:%M%s")
log_level = os.getenv('LOGGING_LEVEL', 20)


def add_severity_level(self, method_name, event_dict):
    if method_name == "warn":
        # The stdlib has an alias
        method_name = "warning"
    event_dict["severity"] = method_name
    return event_dict


logging.basicConfig(stream=sys.stdout, level=log_level, format="%(message)s")
configure(processors=[add_severity_level, add_log_level, filter_by_level, format_exc_info,
                      TimeStamper(fmt="%Y-%m-%dT%H:%M%s",
                                  utc=True, key="created_at"),
                      JSONRenderer(indent=None)])

logger = wrap_logger(logging.getLogger(__name__))


def get_query(date_one, date_two, template_date_column):
    return "SELECT auth.user.username FROM auth.user where (auth.user.last_login_date is null AND " \
           f"auth.user.account_creation_date between '{date_one}' AND '{date_two}' AND " \
           f"auth.user.{template_date_column} is null) OR (auth.user.last_login_date is not null AND " \
           f"auth.user.last_login_date between '{date_one}' AND '{date_two}' AND " \
           f"auth.user.{template_date_column} is null) "


class AuthDueDeletionSchedulerError(Exception):
    def __init__(self, description=None, error=None, **kwargs):
        self.description = description
        self.error = error
        for k, v in kwargs.items():
            self.__dict__[k] = v
