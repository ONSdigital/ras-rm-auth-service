from datetime import timedelta, datetime
from itertools import chain

from ras_rm_auth_scheduler_service.db import setup
from ras_rm_auth_scheduler_service.scheduled_jobs.helper import logger, get_query
from ras_rm_auth_scheduler_service.scheduled_jobs.notify_service import NotifyService


def process_accounts_for_third_notification():
    logger.info("Scheduler processing Accounts not accessed in the last 35 months ")
    con = setup.get_connection()
    csr = con.cursor()
    _datetime_35_months_ago = datetime.utcnow() - timedelta(days=1065)
    _datetime_36_months_ago = datetime.utcnow() - timedelta(days=1095)
    query = get_query(_datetime_36_months_ago, _datetime_35_months_ago, "due_deletion_third_notification_date")
    csr.execute(query)
    users = [x for x in chain.from_iterable(csr.fetchall()) if isinstance(x, str)]
    for username in users:
        logger.info(f"Sending third due deletion notification {username}")
        NotifyService().request_to_notify(template_name='due_deletion_third_notification_templates',
                                          email=username)
        csr.execute(f"Update auth.user set due_deletion_first_notification_date = '{datetime.utcnow()}'")
        con.commit()
        logger.info(f"Due deletion third notification sent to the {username}")
    csr.close()
    con.close()
    logger.info("Scheduler finished processing Accounts not accessed in last 35 months")
