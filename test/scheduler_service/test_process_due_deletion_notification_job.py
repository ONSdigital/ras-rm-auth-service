# import unittest
# from collections import namedtuple
# from unittest.mock import Mock, patch
#
# import requests
#
# from ras_rm_auth_scheduler_service.process_due_deletion_notification_job import (
#     ProcessNotificationJob,
# )
#
# fake_response = namedtuple("Response", "status_code json")
#
#
# class TestNotificationJob(unittest.TestCase):
#     def test_successful_first_notification(self):
#         with patch("ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.get") as mock_get:
#             with patch(
#                 "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.patch"
#             ) as mock_patch:
#                 with patch(
#                     "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService"
#                     ".request_to_notify"
#                 ) as mock_notify:
#                     mock_notify.return_value = Mock()
#                     mock_get.return_value = fake_response(
#                         status_code=200, json=lambda: ["dummy@email.com", "dummy1@email.com", "dummy2@email.com"]
#                     )
#                     mock_patch.return_value = fake_response(status_code=204, json=lambda: [])
#                     ProcessNotificationJob().process_first_notification()
#                     self.assertEqual(mock_notify.call_count, 3)
#                     self.assertEqual(mock_get.call_count, 1)
#                     self.assertEqual(mock_patch.call_count, 3)
#
#     def test_no_notification_required_for_first_notification(self):
#         with patch("ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.get") as mock_get:
#             with patch(
#                 "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.patch"
#             ) as mock_patch:
#                 with patch(
#                     "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService"
#                     ".request_to_notify"
#                 ) as mock_notify:
#                     mock_notify.return_value = Mock()
#                     mock_get.return_value = fake_response(status_code=200, json=lambda: [])
#                     mock_patch.return_value = fake_response(status_code=204, json=lambda: [])
#                     ProcessNotificationJob().process_first_notification()
#                     self.assertEqual(mock_notify.call_count, 0)
#                     self.assertEqual(mock_get.call_count, 1)
#                     self.assertEqual(mock_patch.call_count, 0)
#
#     def test_no_connection_for_first_notification(self):
#         with patch("ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.get") as mock_get:
#             with patch(
#                 "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.patch"
#             ) as mock_patch:
#                 with patch(
#                     "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService"
#                     ".request_to_notify"
#                 ) as mock_notify:
#                     mock_notify.return_value = Mock()
#                     mock_get.side_effect = requests.exceptions.HTTPError("error")
#                     mock_patch.side_effect = requests.exceptions.HTTPError("error")
#                 with self.assertRaises(requests.exceptions.HTTPError):
#                     ProcessNotificationJob().process_first_notification()
#
#     def test_successful_second_notification(self):
#         with patch("ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.get") as mock_get:
#             with patch(
#                 "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.patch"
#             ) as mock_patch:
#                 with patch(
#                     "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService"
#                     ".request_to_notify"
#                 ) as mock_notify:
#                     mock_notify.return_value = Mock()
#                     mock_get.return_value = fake_response(
#                         status_code=200, json=lambda: ["dummy@email.com", "dummy1@email.com", "dummy2@email.com"]
#                     )
#                     mock_patch.return_value = fake_response(status_code=204, json=lambda: [])
#                     ProcessNotificationJob().process_second_notification()
#                     self.assertEqual(mock_notify.call_count, 3)
#                     self.assertEqual(mock_get.call_count, 1)
#                     self.assertEqual(mock_patch.call_count, 3)
#
#     def test_no_notification_required_for_second_notification(self):
#         with patch("ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.get") as mock_get:
#             with patch(
#                 "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.patch"
#             ) as mock_patch:
#                 with patch(
#                     "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService"
#                     ".request_to_notify"
#                 ) as mock_notify:
#                     mock_notify.return_value = Mock()
#                     mock_get.return_value = fake_response(status_code=200, json=lambda: [])
#                     mock_patch.return_value = fake_response(status_code=204, json=lambda: [])
#                     ProcessNotificationJob().process_second_notification()
#                     self.assertEqual(mock_notify.call_count, 0)
#                     self.assertEqual(mock_get.call_count, 1)
#                     self.assertEqual(mock_patch.call_count, 0)
#
#     def test_no_connection_for_second_notification(self):
#         with patch("ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.get") as mock_get:
#             with patch(
#                 "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.patch"
#             ) as mock_patch:
#                 with patch(
#                     "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService"
#                     ".request_to_notify"
#                 ) as mock_notify:
#                     mock_notify.return_value = Mock()
#                     mock_get.side_effect = requests.exceptions.HTTPError("error")
#                     mock_patch.side_effect = requests.exceptions.HTTPError("error")
#                 with self.assertRaises(requests.exceptions.HTTPError):
#                     ProcessNotificationJob().process_second_notification()
#
#     def test_successful_third_notification(self):
#         with patch("ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.get") as mock_get:
#             with patch(
#                 "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.patch"
#             ) as mock_patch:
#                 with patch(
#                     "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService"
#                     ".request_to_notify"
#                 ) as mock_notify:
#                     mock_notify.return_value = Mock()
#                     mock_get.return_value = fake_response(
#                         status_code=200, json=lambda: ["dummy@email.com", "dummy1@email.com", "dummy2@email.com"]
#                     )
#                     mock_patch.return_value = fake_response(status_code=204, json=lambda: [])
#                     ProcessNotificationJob().process_third_notification()
#                     self.assertEqual(mock_notify.call_count, 3)
#                     self.assertEqual(mock_get.call_count, 1)
#                     self.assertEqual(mock_patch.call_count, 3)
#
#     def test_no_notification_required_for_third_notification(self):
#         with patch("ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.get") as mock_get:
#             with patch(
#                 "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.patch"
#             ) as mock_patch:
#                 with patch(
#                     "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService"
#                     ".request_to_notify"
#                 ) as mock_notify:
#                     mock_notify.return_value = Mock()
#                     mock_get.return_value = fake_response(status_code=200, json=lambda: [])
#                     mock_patch.return_value = fake_response(status_code=204, json=lambda: [])
#                     ProcessNotificationJob().process_third_notification()
#                     self.assertEqual(mock_notify.call_count, 0)
#                     self.assertEqual(mock_get.call_count, 1)
#                     self.assertEqual(mock_patch.call_count, 0)
#
#     def test_no_connection_for_third_notification(self):
#         with patch("ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.get") as mock_get:
#             with patch(
#                 "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.requests.patch"
#             ) as mock_patch:
#                 with patch(
#                     "ras_rm_auth_scheduler_service.process_due_deletion_notification_job.NotifyService"
#                     ".request_to_notify"
#                 ) as mock_notify:
#                     mock_notify.return_value = Mock()
#                     mock_get.side_effect = requests.exceptions.HTTPError("error")
#                     mock_patch.side_effect = requests.exceptions.HTTPError("error")
#                 with self.assertRaises(requests.exceptions.HTTPError):
#                     ProcessNotificationJob().process_third_notification()
