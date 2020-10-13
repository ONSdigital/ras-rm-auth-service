from datetime import datetime
from itertools import chain

from ras_rm_auth_scheduler_service.db import setup
from ras_rm_auth_scheduler_service.helper import get_query
from ras_rm_auth_scheduler_service.logger import logger
from ras_rm_auth_scheduler_service.notify_service import NotifyService
from ras_rm_auth_service.resources.tokens import obfuscate_email


def _get_notification_column(template_name):
    templates = {'first_notification': "first_notification",
                 'second_notification': "second_notification",
                 'third_notification': "third_notification"}
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
        logger.info(f"Sending due deletion {scheduler} to {obfuscate_email(username)}")
        NotifyService().request_to_notify(template_name=scheduler,
                                          email=username)
        logger.info(f"Due deletion {scheduler} sent to {obfuscate_email(username)}")
        logger.info(f"updating {column_name} for {obfuscate_email(username)}")
        csr.execute(
            f"Update auth.user set {column_name} = '{datetime.utcnow()}' where auth.user.username = '{obfuscate_email(username)}'")
        con.commit()
        logger.info(f"updated {column_name} for {obfuscate_email(username)}")
    csr.close()
    con.close()
