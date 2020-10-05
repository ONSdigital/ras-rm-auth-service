import base64
import unittest
import datetime
from unittest.mock import patch
from collections import namedtuple
from ras_rm_auth_service.models import models
from sqlalchemy.exc import SQLAlchemyError

from ras_rm_auth_service.db_session_handlers import transactional_session
from ras_rm_auth_service.models.models import User
from run import create_app


class TestBatchProcessEndpoints(unittest.TestCase):
    user_0 = "test0@email.com"
    user_1 = "test1@email.com"
    user_2 = "test2@email.com"
    user_3 = "test3@email.com"
    pwd = "password"
    form_data_0 = {"username": user_0, "password": pwd}
    form_data_1 = {"username": user_1, "password": pwd}
    form_data_2 = {"username": user_2, "password": pwd}
    form_data_3 = {"username": user_3, "password": pwd}

    def setUp(self):
        self.app = create_app('TestingConfig')
        models.Base.metadata.drop_all(self.app.db)
        models.Base.metadata.create_all(self.app.db)
        self.app.db.session.commit()
        self.client = self.app.test_client()

        auth = "{}:{}".format('admin', 'secret').encode('utf-8')
        self.headers = {
            'Authorization': 'Basic %s' % base64.b64encode(bytes(auth)).decode("ascii")
        }

    def batch_setup(self):
        create_user_0 = self.client.post('/api/account/create', data=self.form_data_0, headers=self.headers)
        self.assertEqual(create_user_0.status_code, 201)
        self.assertEqual(create_user_0.get_json(), {"account": self.user_0, "created": "success"})
        self.assertTrue(self.does_user_exists(self.user_0))
        create_user_1 = self.client.post('/api/account/create', data=self.form_data_1, headers=self.headers)
        self.assertEqual(create_user_1.status_code, 201)
        self.assertEqual(create_user_1.get_json(), {"account": self.user_1, "created": "success"})
        self.assertTrue(self.does_user_exists(self.user_1))
        create_user_2 = self.client.post('/api/account/create', data=self.form_data_2, headers=self.headers)
        self.assertEqual(create_user_2.status_code, 201)
        self.assertEqual(create_user_2.get_json(), {"account": self.user_2, "created": "success"})
        self.assertTrue(self.does_user_exists(self.user_2))
        create_user_3 = self.client.post('/api/account/create', data=self.form_data_3, headers=self.headers)
        self.assertEqual(create_user_3.status_code, 201)
        self.assertEqual(create_user_3.get_json(), {"account": self.user_3, "created": "success"})
        self.assertTrue(self.does_user_exists(self.user_3))

    def update_test_data(self, user, criteria):
        self.app.db.session.query(User).filter(User.username == user).update(criteria)
        self.app.db.session.commit()

    def does_user_exists(self, user_name):
        with self.app.app_context():
            with transactional_session() as session:
                return bool(session.query(User).filter(User.username == user_name).first())

    def is_user_marked_for_deletion(self, user_name):
        with self.app.app_context():
            with transactional_session() as session:
                user = session.query(User.mark_for_deletion).filter(User.username == user_name).first()
                return user.mark_for_deletion == True  # noqa

    def is_third_notification_set(self, user_name):
        with self.app.app_context():
            with transactional_session() as session:
                user = session.query(User.third_notification).filter(
                    User.username == user_name).first()
                return user.third_notification != None  # noqa

    def is_second_notification_set(self, user_name):
        with self.app.app_context():
            with transactional_session() as session:
                user = session.query(User.second_notification).filter(
                    User.username == user_name).first()
                return user.second_notification != None  # noqa

    def is_first_notification_set(self, user_name):
        with self.app.app_context():
            with transactional_session() as session:
                user = session.query(User.first_notification).filter(
                    User.username == user_name).first()
                return user.first_notification != None  # noqa

    def test_batch_delete(self):
        """
        Test bach delete
        """
        # Given:
        self.batch_setup()
        # When:
        self.client.delete('/api/account/user',
                           data={"username": self.user_0},
                           headers=self.headers)
        self.client.delete('/api/account/user',
                           data={"username": self.user_1},
                           headers=self.headers)
        self.client.delete('/api/account/user',
                           data={"username": self.user_3},
                           headers=self.headers)
        # Then:

        self.assertTrue(self.is_user_marked_for_deletion(self.user_0))
        self.assertTrue(self.is_user_marked_for_deletion(self.user_1))
        self.assertTrue(self.is_user_marked_for_deletion(self.user_3))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_2))
        fake_response = namedtuple('Response', 'status_code json')
        with patch('ras_rm_auth_service.batch_process_endpoints.requests') as mock_request:
            mock_request().post.return_value = fake_response(status_code=207, json=lambda: [])
            batch_delete_request = self.client.delete('/api/batch/account/users', headers=self.headers)
            mock_request.post().assert_called_once
        self.assertEqual(batch_delete_request.status_code, 204)
        self.assertTrue(self.does_user_exists(self.user_2))
        self.assertFalse(self.does_user_exists(self.user_0))
        self.assertFalse(self.does_user_exists(self.user_1))
        self.assertFalse(self.does_user_exists(self.user_3))

    def test_batch_delete_with_out_users_marked_for_deletion(self):
        """
        Test Batch delete
        """
        # Given:
        self.batch_setup()
        # When:
        fake_response = namedtuple('Response', 'status_code json')
        with patch('ras_rm_auth_service.batch_process_endpoints.requests') as mock_request:
            mock_request().post.return_value = fake_response(status_code=207, json=lambda: [])
            batch_delete_request = self.client.delete('/api/batch/account/users', headers=self.headers)
            # Then:
            mock_request.post().assert_called_once
        self.assertEqual(batch_delete_request.status_code, 204)
        self.assertTrue(self.does_user_exists(self.user_2))
        self.assertTrue(self.does_user_exists(self.user_0))
        self.assertTrue(self.does_user_exists(self.user_1))
        self.assertTrue(self.does_user_exists(self.user_3))

    @patch('ras_rm_auth_service.batch_process_endpoints.transactional_session')
    def test_batch_delete_users_unable_to_commit(self, session_scope_mock):
        # Given:
        session_scope_mock.side_effect = SQLAlchemyError()
        form_data = {"username": "testuser@email.com"}
        # When:
        response = self.client.delete('/api/batch/account/users', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 500)
        # Then:
        self.assertEqual(response.get_json(), {"title": "Scheduler operation for delete users error",
                                               "detail": "Unable to perform delete operation"})

    def test_batch_delete_users_mark_for_deletion_when_last_login_is_not_null(self):
        # Given:
        self.batch_setup()
        # When:
        criteria = {'last_login_date': datetime.datetime(1999, 1, 1, 0, 0)}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.client.delete('/api/batch/account/users/mark-for-deletion', headers=self.headers)
        # Then:
        self.assertTrue(self.is_user_marked_for_deletion(self.user_0))
        self.assertTrue(self.is_user_marked_for_deletion(self.user_2))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_1))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_3))

    def test_batch_delete_users_mark_for_deletion_when_last_login_is_null(self):
        """
          Test scheduler endpoint for the account not accessed in the last 36 months
        """
        # Given:
        self.batch_setup()
        # When:
        criteria = {'account_creation_date': datetime.datetime(1999, 1, 1, 0, 0)}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.client.delete('/api/batch/account/users/mark-for-deletion', headers=self.headers)
        # Then:
        self.assertTrue(self.is_user_marked_for_deletion(self.user_0))
        self.assertTrue(self.is_user_marked_for_deletion(self.user_2))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_1))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_3))

    def test_batch_delete_users_mark_for_deletion_when_last_login_is_present(self):
        """
          Test scheduler endpoint for the account not accessed in the last 36 months
        """
        # Given:
        self.batch_setup()
        # When:
        criteria = {'account_creation_date': datetime.datetime(1999, 1, 1, 0, 0)}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.update_test_data(self.user_2, {'last_login_date': datetime.datetime.utcnow()})
        self.client.delete('/api/batch/account/users/mark-for-deletion', headers=self.headers)
        # Then:
        self.assertTrue(self.is_user_marked_for_deletion(self.user_0))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_2))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_1))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_3))
