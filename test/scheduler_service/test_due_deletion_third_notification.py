import unittest
from unittest.mock import patch, Mock

from ras_rm_auth_scheduler_service.scheduled_jobs.due_deletion_third_notification import \
    process_accounts_for_third_notification


class TestDueDeletionThirdNotification(unittest.TestCase):

    def test_successful_notification(self):
        with patch('ras_rm_auth_scheduler_service.scheduled_jobs.due_deletion_third_notification.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.scheduled_jobs.due_deletion_third_notification.NotifyService'
                       '.request_to_notify'
                       )as mock_notify:
                mock_notify.return_value = Mock()
                to_test = [('test@test.com',), ('test1test.com',), ('test2@test.com',)]
                mock_cursor = Mock()
                cursor_attrs = {'fetchall.return_value': to_test}
                mock_cursor.configure_mock(**cursor_attrs)
                mock_con = Mock()
                engine_attrs = {'cursor.return_value': mock_cursor}
                mock_con.configure_mock(**engine_attrs)
                setup.get_connection.return_value = mock_con
                process_accounts_for_third_notification()
                self.assertEqual(mock_notify.call_count, 3)

    def test_no_notification_required(self):
        with patch('ras_rm_auth_scheduler_service.scheduled_jobs.due_deletion_third_notification.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.scheduled_jobs.due_deletion_third_notification.NotifyService'
                       '.request_to_notify'
                       )as mock_notify:
                mock_notify.return_value = Mock()
                to_test = []
                mock_cursor = Mock()
                cursor_attrs = {'fetchall.return_value': to_test}
                mock_cursor.configure_mock(**cursor_attrs)
                mock_con = Mock()
                engine_attrs = {'cursor.return_value': mock_cursor}
                mock_con.configure_mock(**engine_attrs)
                setup.get_connection.return_value = mock_con
                process_accounts_for_third_notification()
                self.assertEqual(mock_notify.call_count, 0)
