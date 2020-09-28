import unittest
from unittest.mock import MagicMock

from ras_rm_auth_service.notify_service import NotifyService, NotifyError
from run import create_app


class TestNotifyService(unittest.TestCase):
    """
        Tests that the notify service is working as expected
    """

    def setUp(self):
        self.app = create_app('TestingConfig')

    def test_an_invalid_template_id(self):
        with self.app.app_context():
            with self.assertRaises(KeyError):
                notify = NotifyService()
                notify._get_template_id(template_name='invalid_template')

    def test_a_valid_template_id(self):
        with self.app.app_context():
            notify = NotifyService()
            template_id = notify._get_template_id(template_name='due_deletion_first_notification_templates')
            self.assertEqual(template_id, 'due_deletion_first_notification_templates')

    def test_a_successful_send_to_pub_sub(self):
        with self.app.app_context():
            publisher = MagicMock()
            publisher.topic_path.return_value = 'projects/test-project-id/topics/ras-rm-notify-test'
            notify = NotifyService()
            notify.publisher = publisher
            result = notify.request_to_notify(email='test@test.test',
                                              template_name='due_deletion_first_notification_templates')
            data = b'{"notify": {"email_address": "test@test.test", ' \
                   b'"template_id": "due_deletion_first_notification_templates"}}'

            publisher.publish.assert_called()
            publisher.publish.assert_called_with('projects/test-project-id/topics/ras-rm-notify-test', data=data)
            self.assertIsNone(result)

    def test_a_unsuccessful_send_to_pub_sub(self):
        with self.app.app_context():
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
        with self.app.app_context():
            future = MagicMock()
            future.result.side_effect = Exception("bad")
            publisher = MagicMock()
            publisher.publish.return_value = future
            notify = NotifyService()
            notify.publisher = publisher
            with self.assertRaises(NotifyError):
                notify.request_to_notify(email='test@test.test',
                                         template_name='due_deletion_first_notification_templates')
