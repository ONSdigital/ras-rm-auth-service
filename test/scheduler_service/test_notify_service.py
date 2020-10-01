import unittest
from unittest.mock import MagicMock, patch

from ras_rm_auth_scheduler_service.scheduled_jobs.notify_service import NotifyService, NotifyError


class TestNotifyService(unittest.TestCase):
    """
        Tests that the notify service is working as expected
    """

    def test_an_invalid_template_id(self):
        with self.assertRaises(KeyError):
            notify = NotifyService()
            notify._get_template_id(template_name='invalid_template')

    def test_a_valid_template_id(self):
        notify = NotifyService()
        template_id = notify._get_template_id(template_name='due_deletion_first_notification_templates')
        self.assertEqual(template_id, 'due_deletion_first_notification_templates')

    def test_a_successful_send_to_pub_sub(self):
        with patch(
            'ras_rm_auth_scheduler_service.scheduled_jobs.notify_service.NotifyService._get_user_first_name'
        )as mock_request:
            mock_request.return_value = "test"
            publisher = MagicMock()
            publisher.topic_path.return_value = 'projects/test-project-id/topics/ras-rm-notify-test'
            notify = NotifyService()
            notify.publisher = publisher
            result = notify.request_to_notify(email='test@test.test',
                                              template_name='due_deletion_first_notification_templates')
            data = b'{"notify": {"email_address": "test@test.test", ' \
                   b'"template_id": "due_deletion_first_notification_templates", "personalisation": {"first_name": ' \
                   b'"test"}}}'

            publisher.publish.assert_called()
            publisher.publish.assert_called_with('projects/test-project-id/topics/ras-rm-notify-test', data=data)
            self.assertIsNone(result)

    def test_a_unsuccessful_send_to_pub_sub(self):
        with patch(
            'ras_rm_auth_scheduler_service.scheduled_jobs.notify_service.NotifyService._get_user_first_name'
        )as mock_request:
            mock_request.return_value = "test"
            future = MagicMock()
            future.result.side_effect = TimeoutError("bad")
            publisher = MagicMock()
            publisher.publish.return_value = future
            notify = NotifyService()
            notify.publisher = publisher
            with self.assertRaises(NotifyError):
                notify.request_to_notify(email='test@test.test',
                                         template_name='due_deletion_first_notification_templates')

    def test_a_unsuccessful_send_to_pub_sub_with_exception(self):
        with patch(
            'ras_rm_auth_scheduler_service.scheduled_jobs.notify_service.NotifyService._get_user_first_name'
        )as mock_request:
            mock_request.return_value = "test"
            future = MagicMock()
            future.result.side_effect = Exception("bad")
            publisher = MagicMock()
            publisher.publish.return_value = future
            notify = NotifyService()
            notify.publisher = publisher
            with self.assertRaises(NotifyError):
                notify.request_to_notify(email='test@test.test',
                                         template_name='due_deletion_first_notification_templates')
