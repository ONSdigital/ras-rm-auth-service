from datetime import datetime
from itertools import chain

from ras_rm_auth_scheduler_service.db import setup
from ras_rm_auth_scheduler_service.helper import get_query
from ras_rm_auth_scheduler_service.logger import logger
from ras_rm_auth_scheduler_service.notify_service import NotifyService


def _get_notification_column(template_name):
    templates = {'first_notification': "due_deletion_first_notification_date",
                 'second_notification': "due_deletion_second_notification_date",
                 'third_notification': "due_deletion_third_notification_date"}
    if template_name in templates:
        return templates[template_name]
    else:
        raise KeyError('Notification column does not exist')


def process_notification_job(date_one, date_two, scheduler):
    con = setup.get_connection()
    csr = con.cursor()
    column_name = _get_notification_column(scheduler)
    query = get_query(date_one, date_two, column_name)
    csr.execute(query)
    users = [x for x in chain.from_iterable(csr.fetchall()) if isinstance(x, str)]
    for username in users:
        logger.info(f"Sending due deletion {scheduler} to {username}")
        NotifyService().request_to_notify(template_name=scheduler,
                                          email=username)
        logger.info(f"Due deletion {scheduler} sent to {username}")
        logger.info(f"updating {column_name} for {username}")
        csr.execute(f"Update auth.user set {column_name} = '{datetime.utcnow()}'")
        con.commit()
        logger.info(f"updated {column_name} for {username}")
    csr.close()
    con.close()
