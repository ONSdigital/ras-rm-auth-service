
from ras_rm_auth_scheduler_service.logger import logger
from ras_rm_auth_scheduler_service.process_due_deletion_notification_job import ProcessNotificationJob

if __name__ == '__main__':
    logger.info("Scheduler processing Accounts not accessed in the last 35 months ")
    ProcessNotificationJob().process_third_notification()
    logger.info("Scheduler finished processing Accounts not accessed in last 35 months")
    logger.info("Scheduler processing Accounts not accessed in the last 30 months ")
    ProcessNotificationJob().process_second_notification()
    logger.info("Scheduler finished processing Accounts not accessed in last 30 months")
    logger.info("Scheduler processing Accounts not accessed in the last 24 months ")
    ProcessNotificationJob().process_first_notification()
    logger.info("Scheduler finished processing Accounts not accessed in last 24 months")
