import base64
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, PropertyMock
from ras_rm_auth_service.models import models
from sqlalchemy.exc import SQLAlchemyError

from ras_rm_auth_service.db_session_handlers import transactional_session
from ras_rm_auth_service.models.models import User
from run import create_app, app


def mock_response():
    mock_res = MagicMock()
    type(mock_res).status_code = PropertyMock(return_value=207)
    mock_res.json.return_value = "{}"
    return mock_res


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
    ci_upload_url = f'{app.config["PARTY_URL"]}/party-api/v1/batch/requests'

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
        Test bach delete endpoint @batch.route('/users', methods=['DELETE'])
        Given:
        Four user exists in the system
        When:
        Three of the users are marked ready for deletion &
        Scheduler calls the batch endpoint for hard delete
        Then:
        Once the scheduler finishes three users who were marked for deletion
        does not exist in the system &
        One user who was not marked for the deletion, exist in the system
        And a request to partysvc was made to mark the users being deleted ready for deletion
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
        self.assertTrue(self.is_user_marked_for_deletion(self.user_0))
        self.assertTrue(self.is_user_marked_for_deletion(self.user_1))
        self.assertTrue(self.is_user_marked_for_deletion(self.user_3))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_2))
        with patch('ras_rm_auth_service.batch_process_endpoints.requests.post') as mock_request:
            mock_request.return_value = mock_response()
            batch_delete_request = self.client.delete('/api/batch/account/users', headers=self.headers)
            self.assertTrue(mock_request.called)
            self.assertEqual(1, mock_request.call_count)
        # Then:
        self.assertEqual(batch_delete_request.status_code, 204)
        self.assertTrue(self.does_user_exists(self.user_2))
        self.assertFalse(self.does_user_exists(self.user_0))
        self.assertFalse(self.does_user_exists(self.user_1))
        self.assertFalse(self.does_user_exists(self.user_3))

    def test_batch_delete_with_out_users_marked_for_deletion(self):
        """
        Test Batch delete endpoint @batch.route('/users', methods=['DELETE'])
        Given:
        Four user exists in the system
        When:
        None of the users are marked ready for deletion &
        Scheduler calls the batch endpoint for hard delete
        Then:
        All four users are present in the system
        """
        # Given:
        self.batch_setup()
        # When:
        with patch('ras_rm_auth_service.batch_process_endpoints.requests.post') as mock_request:
            mock_request.return_value = mock_response()
            batch_delete_request = self.client.delete('/api/batch/account/users', headers=self.headers)
            # Then:
            self.assertFalse(mock_request.called)
            self.assertEqual(0, mock_request.call_count)
        self.assertEqual(batch_delete_request.status_code, 204)
        self.assertTrue(self.does_user_exists(self.user_2))
        self.assertTrue(self.does_user_exists(self.user_0))
        self.assertTrue(self.does_user_exists(self.user_1))
        self.assertTrue(self.does_user_exists(self.user_3))

    @patch('ras_rm_auth_service.batch_process_endpoints.transactional_session')
    def test_batch_delete_users_unable_to_commit(self, session_scope_mock):
        """
        Test Batch delete endpoint @batch.route('/users', methods=['DELETE'])
        Given:
        side effect has been configured
        When:
        Scheduler calls the batch endpoint for hard delete
        Then:
        500 error is raised
        """
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
        """
        Test mark for deletion endpoint @batch.route('users/mark-for-deletion', methods=['DELETE'])
        Provided the last login date is not null and the user has not logged in for the last
        36 months the accounts will be marked for deletion
        """
        # Given:
        self.batch_setup()
        # When:
        criteria = {'last_login_date': datetime(1999, 1, 1, 0, 0)}
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
        Test mark for deletion endpoint @batch.route('users/mark-for-deletion', methods=['DELETE'])
        Provided the last login is null and the user account got created
        36 months ago the accounts will be marked for deletion
        """
        # Given:
        self.batch_setup()
        # When:
        criteria = {'account_creation_date': datetime(1999, 1, 1, 0, 0)}
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
        Test mark for deletion endpoint @batch.route('users/mark-for-deletion', methods=['DELETE'])
        Provided the last login date is present and the user account creation is present
        users has not logged in for the last
        36 months the accounts will be marked for deletion
        """
        # Given:
        self.batch_setup()
        # When:
        criteria = {'account_creation_date': datetime(1999, 1, 1, 0, 0)}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.update_test_data(self.user_2, {'last_login_date': datetime.utcnow()})
        self.update_test_data(self.user_2, {'account_verified': True})
        self.client.delete('/api/batch/account/users/mark-for-deletion', headers=self.headers)
        # Then:
        self.assertTrue(self.is_user_marked_for_deletion(self.user_0))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_2))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_1))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_3))

    def test_batch_delete_users_mark_for_deletion_for_not_verified_account(self):
        """
        Test mark for deletion endpoint @batch.route('users/mark-for-deletion', methods=['DELETE'])
        Provided the account has been created 80 hrs ago but the account is not verified, the account
        will be marked for deletion to be picked up for hard delete
        """
        # Given:
        self.batch_setup()
        # When:
        criteria = {'account_creation_date': datetime.utcnow() - timedelta(hours=80)}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.client.delete('/api/batch/account/users/mark-for-deletion', headers=self.headers)
        # Then:
        self.assertTrue(self.is_user_marked_for_deletion(self.user_0))
        self.assertTrue(self.is_user_marked_for_deletion(self.user_2))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_1))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_3))

    def test_batch_delete_users_mark_for_deletion_for_verified_account(self):
        """
        Test mark for deletion endpoint @batch.route('users/mark-for-deletion', methods=['DELETE'])
        Provided the account has been created 80 hrs ago but the account is verified, the account
        will not be marked for deletion to be picked up for hard delete
        """
        # Given:
        self.batch_setup()
        # When:
        criteria = {'account_creation_date': datetime.utcnow() - timedelta(hours=80)}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        criteria = {'account_verified': True}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.client.delete('/api/batch/account/users/mark-for-deletion', headers=self.headers)
        # Then:
        self.assertFalse(self.is_user_marked_for_deletion(self.user_0))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_2))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_1))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_3))

    def test_account_marked_for_deletion_resets_when_user_login(self):
        """
        Provided the accounts has been marked for deletion, when the user login
        the mark_for_deletion should reset
        """
        # Given:
        self.batch_setup()
        criteria = {'account_creation_date': datetime.utcnow() - timedelta(hours=80)}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.client.delete('/api/batch/account/users/mark-for-deletion', headers=self.headers)
        self.assertTrue(self.is_user_marked_for_deletion(self.user_0))
        self.assertTrue(self.is_user_marked_for_deletion(self.user_2))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_1))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_3))
        # When:
        form_data = {"username": self.user_0, "account_verified": "true"}
        self.client.put('/api/account/create', data=form_data, headers=self.headers)
        # Then:
        self.assertFalse(self.is_user_marked_for_deletion(self.user_0))
        self.assertTrue(self.is_user_marked_for_deletion(self.user_2))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_1))
        self.assertFalse(self.is_user_marked_for_deletion(self.user_3))

    def test_get_users_eligible_for_fist_notification_with_last_login_not_null(self):
        """
        Test users_eligible_for_fist_notification endpoint @batch.route('users/eligible_for_fist_notification',
        methods=['GET'])
        """
        # Given:
        self.batch_setup()
        # When:
        _datetime_24_months_ago = datetime.utcnow() - timedelta(days=730)
        criteria = {'last_login_date': _datetime_24_months_ago}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        response = self.client.get('/api/batch/account/users/eligible-for-first-notification', headers=self.headers)
        # Then:
        self.assertTrue(200, response.status_code)
        users = response.get_json()
        self.assertEqual(2, len(users))
        self.assertIn(self.user_0, users)
        self.assertIn(self.user_2, users)
        self.assertNotIn(self.user_1, users)
        self.assertNotIn(self.user_3, users)

    def test_get_users_eligible_for_fist_notification_with_last_login_null(self):
        """
        Test users_eligible_for_fist_notification endpoint @batch.route('users/eligible_for_fist_notification',
        methods=['GET'])
        """
        # Given:
        self.batch_setup()
        # When:
        _datetime_24_months_ago = datetime.utcnow() - timedelta(days=730)
        criteria_one = {'account_creation_date': _datetime_24_months_ago}
        criteria = {'last_login_date': None}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.update_test_data(self.user_0, criteria_one)
        self.update_test_data(self.user_2, criteria_one)
        response = self.client.get('/api/batch/account/users/eligible-for-first-notification', headers=self.headers)
        # Then:
        self.assertTrue(200, response.status_code)
        users = response.get_json()
        self.assertEqual(2, len(users))
        self.assertIn(self.user_0, users)
        self.assertIn(self.user_2, users)
        self.assertNotIn(self.user_1, users)
        self.assertNotIn(self.user_3, users)

    def test_get_users_eligible_for_fist_notification(self):
        """
        Test users_eligible_for_fist_notification endpoint @batch.route('users/eligible_for_fist_notification',
        methods=['GET'])
        """
        # Given:
        self.batch_setup()
        # When:
        _datetime_24_months_ago = datetime.utcnow() - timedelta(days=750)
        criteria = {'last_login_date': _datetime_24_months_ago}
        criteria_one = {'account_creation_date': _datetime_24_months_ago}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.update_test_data(self.user_1, criteria_one)
        self.update_test_data(self.user_3, criteria_one)
        response = self.client.get('/api/batch/account/users/eligible-for-first-notification', headers=self.headers)
        # Then:
        self.assertTrue(200, response.status_code)
        users = response.get_json()
        self.assertEqual(4, len(users))
        self.assertIn(self.user_0, users)
        self.assertIn(self.user_2, users)
        self.assertIn(self.user_1, users)
        self.assertIn(self.user_3, users)

    def test_get_users_eligible_for_fist_notification_with_no_result(self):
        """
        Test users_eligible_for_fist_notification endpoint @batch.route('users/eligible_for_fist_notification',
        methods=['GET'])
        """
        # Given:
        self.batch_setup()
        # When:
        response = self.client.get('/api/batch/account/users/eligible-for-first-notification', headers=self.headers)
        # Then:
        self.assertTrue(200, response.status_code)
        users = response.get_json()
        self.assertEqual(0, len(users))
        self.assertNotIn(self.user_0, users)
        self.assertNotIn(self.user_2, users)
        self.assertNotIn(self.user_1, users)
        self.assertNotIn(self.user_3, users)

    def test_get_users_eligible_for_second_notification_with_last_login_not_null(self):
        """
        Test users_eligible_for_fist_notification endpoint @batch.route('users/eligible-for-second-notification',
        methods=['GET'])
        """
        # Given:
        self.batch_setup()
        # When:
        _datetime_30_months_ago = datetime.utcnow() - timedelta(days=913)
        criteria = {'last_login_date': _datetime_30_months_ago}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        response = self.client.get('/api/batch/account/users/eligible-for-second-notification', headers=self.headers)
        # Then:
        self.assertTrue(200, response.status_code)
        users = response.get_json()
        self.assertEqual(2, len(users))
        self.assertIn(self.user_0, users)
        self.assertIn(self.user_2, users)
        self.assertNotIn(self.user_1, users)
        self.assertNotIn(self.user_3, users)

    def test_get_users_eligible_for_second_notification_with_last_login_null(self):
        """
        Test users_eligible_for_fist_notification endpoint @batch.route('users/eligible-for-second-notification',
        methods=['GET'])
        """
        # Given:
        self.batch_setup()
        # When:
        _datetime_30_months_ago = datetime.utcnow() - timedelta(days=913)
        criteria_one = {'account_creation_date': _datetime_30_months_ago}
        criteria = {'last_login_date': None}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.update_test_data(self.user_0, criteria_one)
        self.update_test_data(self.user_2, criteria_one)
        response = self.client.get('/api/batch/account/users/eligible-for-second-notification', headers=self.headers)
        # Then:
        self.assertTrue(200, response.status_code)
        users = response.get_json()
        self.assertEqual(2, len(users))
        self.assertIn(self.user_0, users)
        self.assertIn(self.user_2, users)
        self.assertNotIn(self.user_1, users)
        self.assertNotIn(self.user_3, users)

    def test_get_users_eligible_for_second_notification(self):
        """
        Test users_eligible_for_fist_notification endpoint @batch.route('users/eligible-for-second-notification',
        methods=['GET'])
        """
        # Given:
        self.batch_setup()
        # When:
        _datetime_30_months_ago = datetime.utcnow() - timedelta(days=1064)
        criteria = {'last_login_date': _datetime_30_months_ago}
        criteria_one = {'account_creation_date': _datetime_30_months_ago}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.update_test_data(self.user_1, criteria_one)
        self.update_test_data(self.user_3, criteria_one)
        response = self.client.get('/api/batch/account/users/eligible-for-second-notification', headers=self.headers)
        # Then:
        self.assertTrue(200, response.status_code)
        users = response.get_json()
        self.assertEqual(4, len(users))
        self.assertIn(self.user_0, users)
        self.assertIn(self.user_2, users)
        self.assertIn(self.user_1, users)
        self.assertIn(self.user_3, users)

    def test_get_users_eligible_for_second_notification_with_no_result(self):
        """
        Test users_eligible_for_fist_notification endpoint @batch.route('users/eligible-for-second-notification',
        methods=['GET'])
        """
        # Given:
        self.batch_setup()
        # When:
        response = self.client.get('/api/batch/account/users/eligible-for-second-notification', headers=self.headers)
        # Then:
        self.assertTrue(200, response.status_code)
        users = response.get_json()
        self.assertEqual(0, len(users))
        self.assertNotIn(self.user_0, users)
        self.assertNotIn(self.user_2, users)
        self.assertNotIn(self.user_1, users)
        self.assertNotIn(self.user_3, users)

    def test_get_users_eligible_for_third_notification_with_last_login_not_null(self):
        """
        Test users_eligible_for_fist_notification endpoint @batch.route('users/eligible-for-third-notification',
        methods=['GET'])
        """
        # Given:
        self.batch_setup()
        # When:
        _datetime_35_months_ago = datetime.utcnow() - timedelta(days=1065)
        criteria = {'last_login_date': _datetime_35_months_ago}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        response = self.client.get('/api/batch/account/users/eligible-for-third-notification', headers=self.headers)
        # Then:
        self.assertTrue(200, response.status_code)
        users = response.get_json()
        self.assertEqual(2, len(users))
        self.assertIn(self.user_0, users)
        self.assertIn(self.user_2, users)
        self.assertNotIn(self.user_1, users)
        self.assertNotIn(self.user_3, users)

    def test_get_users_eligible_for_third_notification_with_last_login_null(self):
        """
        Test users_eligible_for_fist_notification endpoint @batch.route('users/eligible-for-third-notification',
        methods=['GET'])
        """
        # Given:
        self.batch_setup()
        # When:
        _datetime_35_months_ago = datetime.utcnow() - timedelta(days=1069)
        criteria_one = {'account_creation_date': _datetime_35_months_ago}
        criteria = {'last_login_date': None}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.update_test_data(self.user_0, criteria_one)
        self.update_test_data(self.user_2, criteria_one)
        response = self.client.get('/api/batch/account/users/eligible-for-third-notification', headers=self.headers)
        # Then:
        self.assertTrue(200, response.status_code)
        users = response.get_json()
        self.assertEqual(2, len(users))
        self.assertIn(self.user_0, users)
        self.assertIn(self.user_2, users)
        self.assertNotIn(self.user_1, users)
        self.assertNotIn(self.user_3, users)

    def test_get_users_eligible_for_third_notification(self):
        """
        Test users_eligible_for_fist_notification endpoint @batch.route('users/eligible-for-third-notification',
        methods=['GET'])
        """
        # Given:
        self.batch_setup()
        # When:
        _datetime_35_months_ago = datetime.utcnow() - timedelta(days=1069)
        criteria = {'last_login_date': _datetime_35_months_ago}
        criteria_one = {'account_creation_date': _datetime_35_months_ago}
        self.update_test_data(self.user_0, criteria)
        self.update_test_data(self.user_2, criteria)
        self.update_test_data(self.user_1, criteria_one)
        self.update_test_data(self.user_3, criteria_one)
        response = self.client.get('/api/batch/account/users/eligible-for-third-notification', headers=self.headers)
        # Then:
        self.assertTrue(200, response.status_code)
        users = response.get_json()
        self.assertEqual(4, len(users))
        self.assertIn(self.user_0, users)
        self.assertIn(self.user_2, users)
        self.assertIn(self.user_1, users)
        self.assertIn(self.user_3, users)

    def test_get_users_eligible_for_third_notification_with_no_result(self):
        """
        Test users_eligible_for_fist_notification endpoint @batch.route('users/eligible-for-third-notification',
        methods=['GET'])
        """
        # Given:
        self.batch_setup()
        # When:
        response = self.client.get('/api/batch/account/users/eligible-for-third-notification', headers=self.headers)
        # Then:
        self.assertTrue(200, response.status_code)
        users = response.get_json()
        self.assertEqual(0, len(users))
        self.assertNotIn(self.user_0, users)
        self.assertNotIn(self.user_2, users)
        self.assertNotIn(self.user_1, users)
        self.assertNotIn(self.user_3, users)
