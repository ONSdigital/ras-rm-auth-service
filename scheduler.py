
from ras_rm_auth_scheduler_service.logger import logger
from ras_rm_auth_scheduler_service.process_due_deletion_notification_job import process_notification_job
from datetime import timedelta, datetime


if __name__ == '__main__':
    _datetime_24_months_ago = datetime.utcnow() - timedelta(days=730)
    _datetime_30_months_ago = datetime.utcnow() - timedelta(days=913)
    _datetime_35_months_ago = datetime.utcnow() - timedelta(days=1065)
    _datetime_36_months_ago = datetime.utcnow() - timedelta(days=1095)
    logger.info("Scheduler processing Accounts not accessed in the last 35 months ")
    process_notification_job(_datetime_36_months_ago, _datetime_35_months_ago, 'third_notification')
    logger.info("Scheduler finished processing Accounts not accessed in last 35 months")
    logger.info("Scheduler processing Accounts not accessed in the last 30 months ")
    process_notification_job(_datetime_35_months_ago, _datetime_30_months_ago, 'second_notification')
    logger.info("Scheduler finished processing Accounts not accessed in last 30 months")
    logger.info("Scheduler processing Accounts not accessed in the last 24 months ")
    process_notification_job(_datetime_30_months_ago, _datetime_24_months_ago, 'first_notification')
    logger.info("Scheduler finished processing Accounts not accessed in last 24 months")
