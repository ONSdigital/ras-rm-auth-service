from ras_rm_auth_scheduler_service.scheduled_jobs.due_deletion_first_notification import \
    process_accounts_for_first_notification
from ras_rm_auth_scheduler_service.scheduled_jobs.due_deletion_second_notification import \
    process_accounts_for_second_notification
from ras_rm_auth_scheduler_service.scheduled_jobs.due_deletion_third_notification import \
    process_accounts_for_third_notification

if __name__ == '__main__':
    process_accounts_for_third_notification()
    process_accounts_for_second_notification()
    process_accounts_for_first_notification()
