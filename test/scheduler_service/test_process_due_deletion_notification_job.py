import unittest
from unittest.mock import patch, Mock
from datetime import timedelta, datetime

from ras_rm_auth_scheduler_service.helper import AuthDueDeletionSchedulerError
from ras_rm_auth_scheduler_service.notify_service import NotifyError
from ras_rm_auth_scheduler_service.process_due_deletion_notification_job import process_notification_job


def process_due_deletion_notification_job():
    pass


class TestNotificationJob(unittest.TestCase):
    _datetime_24_months_ago = datetime.utcnow() - timedelta(days=730)
    _datetime_30_months_ago = datetime.utcnow() - timedelta(days=913)
    _datetime_35_months_ago = datetime.utcnow() - timedelta(days=1065)
    _datetime_36_months_ago = datetime.utcnow() - timedelta(days=1095)

    def test_successful_first_notification(self):
        with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService'
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
                process_notification_job(self._datetime_30_months_ago,
                                         self._datetime_24_months_ago,
                                         'first_notification')
                self.assertEqual(mock_notify.call_count, 3)
                self.assertEqual(mock_con.commit.call_count, 3)

    def test_no_notification_required_for_first_notification(self):
        with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService'
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
                process_notification_job(self._datetime_30_months_ago,
                                         self._datetime_24_months_ago,
                                         'first_notification')
                self.assertEqual(mock_notify.call_count, 0)
                self.assertEqual(mock_con.commit.call_count, 0)

    def test_no_connection_for_first_notification(self):
        with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService'
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
                setup.get_connection.side_effect = AuthDueDeletionSchedulerError('Unable to establish database '
                                                                                 'connection.')
                with self.assertRaises(AuthDueDeletionSchedulerError):
                    process_notification_job(self._datetime_30_months_ago,
                                             self._datetime_24_months_ago,
                                             'first_notification')

    def test_notification_error_for_first_notification(self):
        with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService'
                       '.request_to_notify'
                       )as mock_notify:
                mock_notify.side_effect = NotifyError()
                to_test = [('test@test.com',), ('test1test.com',), ('test2@test.com',)]
                mock_cursor = Mock()
                cursor_attrs = {'fetchall.return_value': to_test}
                mock_cursor.configure_mock(**cursor_attrs)
                mock_con = Mock()
                engine_attrs = {'cursor.return_value': mock_cursor}
                mock_con.configure_mock(**engine_attrs)
                setup.get_connection.return_value = mock_con
                with self.assertRaises(NotifyError):
                    process_notification_job(self._datetime_30_months_ago,
                                             self._datetime_24_months_ago,
                                             'first_notification')
                    self.assertEqual(mock_con.commit.call_count, 0)

    def test_successful_second_notification(self):
        with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService'
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
                process_notification_job(self._datetime_30_months_ago,
                                         self._datetime_24_months_ago,
                                         'second_notification')
                self.assertEqual(mock_notify.call_count, 3)
                self.assertEqual(mock_con.commit.call_count, 3)

    def test_no_notification_required_for_second_notification(self):
        with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService'
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
                process_notification_job(self._datetime_30_months_ago,
                                         self._datetime_24_months_ago,
                                         'second_notification')
                self.assertEqual(mock_notify.call_count, 0)
                self.assertEqual(mock_con.commit.call_count, 0)

    def test_no_connection_for_second_notification(self):
        with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService'
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
                setup.get_connection.side_effect = AuthDueDeletionSchedulerError('Unable to establish database '
                                                                                 'connection.')
                with self.assertRaises(AuthDueDeletionSchedulerError):
                    process_notification_job(self._datetime_30_months_ago,
                                             self._datetime_24_months_ago,
                                             'second_notification')

    def test_notification_error_for_second_notification(self):
        with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService'
                       '.request_to_notify'
                       )as mock_notify:
                mock_notify.side_effect = NotifyError()
                to_test = [('test@test.com',), ('test1test.com',), ('test2@test.com',)]
                mock_cursor = Mock()
                cursor_attrs = {'fetchall.return_value': to_test}
                mock_cursor.configure_mock(**cursor_attrs)
                mock_con = Mock()
                engine_attrs = {'cursor.return_value': mock_cursor}
                mock_con.configure_mock(**engine_attrs)
                setup.get_connection.return_value = mock_con
                with self.assertRaises(NotifyError):
                    process_notification_job(self._datetime_30_months_ago,
                                             self._datetime_24_months_ago,
                                             'second_notification')
                    self.assertEqual(mock_con.commit.call_count, 0)

    def test_successful_third_notification(self):
        with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService'
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
                process_notification_job(self._datetime_30_months_ago,
                                         self._datetime_24_months_ago,
                                         'third_notification')
                self.assertEqual(mock_notify.call_count, 3)
                self.assertEqual(mock_con.commit.call_count, 3)

    def test_no_notification_required_for_third_notification(self):
        with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService'
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
                process_notification_job(self._datetime_30_months_ago,
                                         self._datetime_24_months_ago,
                                         'third_notification')
                self.assertEqual(mock_notify.call_count, 0)
                self.assertEqual(mock_con.commit.call_count, 0)

    def test_no_connection_for_third_notification(self):
        with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService'
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
                setup.get_connection.side_effect = AuthDueDeletionSchedulerError('Unable to establish database '
                                                                                 'connection.')
                with self.assertRaises(AuthDueDeletionSchedulerError):
                    process_notification_job(self._datetime_30_months_ago,
                                             self._datetime_24_months_ago,
                                             'third_notification')

    def test_notification_error_for_third_notification(self):
        with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.setup')as setup:
            with patch('ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService'
                       '.request_to_notify'
                       )as mock_notify:
                mock_notify.side_effect = NotifyError()
                to_test = [('test@test.com',), ('test1test.com',), ('test2@test.com',)]
                mock_cursor = Mock()
                cursor_attrs = {'fetchall.return_value': to_test}
                mock_cursor.configure_mock(**cursor_attrs)
                mock_con = Mock()
                engine_attrs = {'cursor.return_value': mock_cursor}
                mock_con.configure_mock(**engine_attrs)
                setup.get_connection.return_value = mock_con
                with self.assertRaises(NotifyError):
                    process_notification_job(self._datetime_30_months_ago,
                                             self._datetime_24_months_ago,
                                             'third_notification')
                    self.assertEqual(mock_con.commit.call_count, 0)
