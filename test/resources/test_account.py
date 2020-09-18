import base64
import unittest
from unittest.mock import patch

from sqlalchemy.exc import SQLAlchemyError

from ras_rm_auth_service.db_session_handlers import transactional_session
from ras_rm_auth_service.models import models
from ras_rm_auth_service.models.models import User
from run import create_app


class TestAccount(unittest.TestCase):

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

    def does_user_exists(self, user_name):
        with self.app.app_context():
            with transactional_session() as session:
                return bool(session.query(User).filter(User.username == user_name).first())

    def is_user_marked_for_deletion(self, user_name):
        with self.app.app_context():
            with transactional_session() as session:
                user = session.query(User.mark_for_deletion).filter(User.username == user_name).first()
                return user.mark_for_deletion == True

    def test_user_create(self):
        """
        Test create user end point
        """
        form_data = {"username": "testuser@email.com", "password": "password"}

        response = self.client.post('/api/account/create', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"account": "testuser@email.com", "created": "success"})

    @patch('ras_rm_auth_service.resources.account.transactional_session')
    def test_user_create_unable_to_commit(self, session_scope_mock):
        """
        Test create user end point unable to commit account
        """
        session_scope_mock.side_effect = SQLAlchemyError()
        form_data = {"username": "testuser@email.com", "password": "password"}

        response = self.client.post('/api/account/create', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"title": "Auth service account create db error",
                                               "detail": "Unable to commit account to database"})

    def test_user_create_email_conflict(self):
        """
        Given a user account has been created
        When another account is being created with the same email
        Then a server error is thrown
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When
        response = self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"title": "Auth service account create error",
                                               "detail": "Unable to create account with requested username"})

    def test_user_create_bad_request(self):
        """
        Test create user end point with bad request
        """
        form_data = {"password": "password"}  # missing username

        response = self.client.post('/api/account/create', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"title": "Authentication error in Auth service",
                                               "detail": "Missing 'username' or 'password'"})

    def test_user_can_be_verified(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then user is verified
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When

        form_data = {"username": "testuser@email.com", "account_verified": "true"}
        response = self.client.put('/api/account/create', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 201)

    def test_cannot_verify_a_user_that_does_not_exist(self):
        """
        Given no accounts exist
        When I verify a non-existant the account
        Then I get an authetication error
        """
        # Given
        # There are no accounts

        # When

        data = {"username": "idonotexist@example.com", "account_verified": "true"}
        response = self.client.put('/api/account/create', data=data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "title": "Auth service account update user error",
            "detail": "Unauthorized user credentials. This user does not exist on the Auth server"})

    def test_user_must_verify_with_true_or_false(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then I can login
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When

        form_data = {"username": "testuser@email.com", "account_verified": "garbage"}
        response = self.client.put('/api/account/create', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 400)

    @patch('ras_rm_auth_service.resources.account.transactional_session')
    def test_user_verified_unable_to_commit(self, session_scope_mock):
        """
        Test verify user end point unable to commit updateed account
        """
        session_scope_mock.side_effect = SQLAlchemyError()
        form_data = {"username": "testuser@email.com", "account_verified": "true"}
        response = self.client.put('/api/account/create', data=form_data, headers=self.headers)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"title": "Auth service account update user error",
                                               "detail": "Unable to commit updated account to database"})

    def test_user_can_change_email(self):
        """
        Given a user account has been created
        When I change account email
        Then user email is updated
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When

        form_data = {"username": "testuser@email.com", "new_username": "anotheremail@email.com"}
        response = self.client.put('/api/account/create', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 201)

    def test_cannot_change_email_for_a_user_that_does_not_exist(self):
        """
        Given no accounts exist
        When I change account email
        Then I get an authentication error
        """
        # Given
        # There are no accounts

        # When

        data = {"username": "idonotexist@example.com", "new_username": "anotheremail@email.com"}
        response = self.client.put('/api/account/create', data=data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "title": "Auth service account update user error",
            "detail": "Unauthorized user credentials. This user does not exist on the Auth server"})

    def test_user_change_email_conflict(self):
        """
        Given a user account has been created
        When another account is being updated with the same email
        Then a server error is thrown
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        form_data = {"username": "anothertestuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When
        data = {"username": "testuser@email.com", "new_username": "anothertestuser@email.com"}
        response = self.client.put('/api/account/create', data=data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"title": "Auth service account update user error",
                                               "detail": "Unable to commit updated account to database"})

    def test_user_can_change_password(self):
        """
        Given a user account has been created
        When I change account password
        Then user password is updated
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When
        form_data = {"username": "testuser@email.com", "password": "anotherpassword"}
        response = self.client.put('/api/account/create', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 201)

    def test_locked_account_can_be_unlocked(self):
        """
        Given a locked user exists
        When I unlock account
        Then account should be unlocked and verified
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        form_data = {"username": "testuser@email.com", "password": "wrongpassword"}
        for _ in range(10):
            self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)

        # When
        form_data = {"username": "testuser@email.com", "account_locked": False}
        response = self.client.put('/api/account/create', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        # Then
        form_data = {"username": "testuser@email.com", "password": "password"}
        response = self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 204)

    def test_delete_user(self):
        """
        Test delete user end point

                Given a locked user exists
                When I unlock account
                Then account should be deleted and verified
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)
        # When
        form_data = {"username": "testuser@email.com"}

        response = self.client.delete('/api/account/user', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 204)

    def test_delete_user_case_insensitive(self):
        """
        Test delete user end point

                Given a user exists
                When I delete that user with a case different that it was initially entered with
                Then account should be deleted
        """
        # Given
        form_data = {"username": "tEstuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)
        # When
        form_data = {"username": "TeStUsEr@EmAiL.com"}

        response = self.client.delete('/api/account/user', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 204)

    @patch('ras_rm_auth_service.resources.account.transactional_session')
    def test_delete_user_unable_to_commit(self, session_scope_mock):
        """
        Test delete user end point unable to commit account
        """
        session_scope_mock.side_effect = SQLAlchemyError()
        form_data = {"username": "testuser@email.com"}

        response = self.client.delete('/api/account/user', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"title": "Auth service delete user error",
                                               "detail": "Unable to commit delete operation"})

    def test_delete_user_bad_request(self):
        """
        Test delete user end point with bad request
        """
        form_data = {}  # missing username

        response = self.client.delete('/api/account/user', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"title": "Auth service delete user error",
                                               "detail": "Missing 'username'"})

    def test_delete_user_that_does_not_exist(self):
        """
        Given no user account exist
        When delete a non-existing the account
        Then get an authentication error
        """
        # Given
        # Verify the user doesn't exist by trying to change one that doesn't exist.
        data = {"username": "idonotexist@example.com", "password": "password"}
        response = self.client.put('/api/account/create', data=data, headers=self.headers)
        self.assertEqual(response.status_code, 401)

        # When
        form_data = {"username": "idonotexist@example.com"}
        response = self.client.delete('/api/account/user', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"title": "Auth service delete user error",
                                               "detail": "This user does not exist on the Auth server"})

    def test_batch_delete(self):
        """
        Test create user end point
        """
        user_0 = "test0@email.com"
        user_1 = "test1@email.com"
        user_2 = "test2@email.com"
        user_3 = "test3@email.com"
        pwd = "password"
        form_data_0 = {"username": user_0, "password": pwd}
        form_data_1 = {"username": user_1, "password": pwd}
        form_data_2 = {"username": user_2, "password": pwd}
        form_data_3 = {"username": user_3, "password": pwd}

        create_user_0 = self.client.post('/api/account/create', data=form_data_0, headers=self.headers)
        self.assertEqual(create_user_0.status_code, 201)
        self.assertEqual(create_user_0.get_json(), {"account": user_0, "created": "success"})
        self.assertTrue(self.does_user_exists(user_0))
        create_user_1 = self.client.post('/api/account/create', data=form_data_1, headers=self.headers)
        self.assertEqual(create_user_1.status_code, 201)
        self.assertEqual(create_user_1.get_json(), {"account": user_1, "created": "success"})
        self.assertTrue(self.does_user_exists(user_1))
        create_user_2 = self.client.post('/api/account/create', data=form_data_2, headers=self.headers)
        self.assertEqual(create_user_2.status_code, 201)
        self.assertEqual(create_user_2.get_json(), {"account": user_2, "created": "success"})
        self.assertTrue(self.does_user_exists(user_2))
        create_user_3 = self.client.post('/api/account/create', data=form_data_3, headers=self.headers)
        self.assertEqual(create_user_3.status_code, 201)
        self.assertEqual(create_user_3.get_json(), {"account": user_3, "created": "success"})
        self.assertTrue(self.does_user_exists(user_3))
        self.client.delete('/api/account/user',
                           data={"username": user_0},
                           headers=self.headers)
        self.client.delete('/api/account/user',
                           data={"username": user_1},
                           headers=self.headers)
        self.client.delete('/api/account/user',
                           data={"username": user_3},
                           headers=self.headers)
        self.assertTrue(self.is_user_marked_for_deletion(user_0))
        self.assertTrue(self.is_user_marked_for_deletion(user_1))
        self.assertTrue(self.is_user_marked_for_deletion(user_3))
        self.assertFalse(self.is_user_marked_for_deletion(user_2))
        batch_delete_request = self.client.delete('/api/account/batch/users', headers=self.headers)
        self.assertEqual(batch_delete_request.status_code, 204)
        self.assertTrue(self.does_user_exists(user_2))
        self.assertFalse(self.does_user_exists(user_0))
        self.assertFalse(self.does_user_exists(user_1))
        self.assertFalse(self.does_user_exists(user_3))

    def test_batch_delete_with_out_users_marked_for_deletion(self):
        """
        Test create user end point
        """
        user_0 = "test0@email.com"
        user_1 = "test1@email.com"
        user_2 = "test2@email.com"
        user_3 = "test3@email.com"
        pwd = "password"
        form_data_0 = {"username": user_0, "password": pwd}
        form_data_1 = {"username": user_1, "password": pwd}
        form_data_2 = {"username": user_2, "password": pwd}
        form_data_3 = {"username": user_3, "password": pwd}

        create_user_0 = self.client.post('/api/account/create', data=form_data_0, headers=self.headers)
        self.assertEqual(create_user_0.status_code, 201)
        self.assertEqual(create_user_0.get_json(), {"account": user_0, "created": "success"})
        self.assertTrue(self.does_user_exists(user_0))
        create_user_1 = self.client.post('/api/account/create', data=form_data_1, headers=self.headers)
        self.assertEqual(create_user_1.status_code, 201)
        self.assertEqual(create_user_1.get_json(), {"account": user_1, "created": "success"})
        self.assertTrue(self.does_user_exists(user_1))
        create_user_2 = self.client.post('/api/account/create', data=form_data_2, headers=self.headers)
        self.assertEqual(create_user_2.status_code, 201)
        self.assertEqual(create_user_2.get_json(), {"account": user_2, "created": "success"})
        self.assertTrue(self.does_user_exists(user_2))
        create_user_3 = self.client.post('/api/account/create', data=form_data_3, headers=self.headers)
        self.assertEqual(create_user_3.status_code, 201)
        self.assertEqual(create_user_3.get_json(), {"account": user_3, "created": "success"})
        self.assertTrue(self.does_user_exists(user_3))
        batch_delete_request = self.client.delete('/api/account/batch/users', headers=self.headers)
        self.assertEqual(batch_delete_request.status_code, 204)
        self.assertTrue(self.does_user_exists(user_2))
        self.assertTrue(self.does_user_exists(user_0))
        self.assertTrue(self.does_user_exists(user_1))
        self.assertTrue(self.does_user_exists(user_3))

    @patch('ras_rm_auth_service.resources.account.transactional_session')
    def test_batch_delete_users_unable_to_commit(self, session_scope_mock):
        session_scope_mock.side_effect = SQLAlchemyError()
        form_data = {"username": "testuser@email.com"}
        response = self.client.delete('/api/account/batch/users', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"title": "Scheduler operation for delete users error",
                                               "detail": "Unable to perform delete operation"})
