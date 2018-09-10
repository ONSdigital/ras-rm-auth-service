import unittest
from unittest.mock import patch

from sqlalchemy.exc import SQLAlchemyError

from ras_rm_auth_service.models import models
from run import create_app


class TestAccount(unittest.TestCase):

    def setUp(self):
        app = create_app('TestingConfig')
        models.Base.metadata.drop_all(app.db)
        models.Base.metadata.create_all(app.db)
        app.db.session.commit()
        self.client = app.test_client()

    def test_user_create(self):
        """
        Test create user end point
        """
        form_data = {"username": "testuser@email.com", "password": "password"}

        response = self.client.post('/api/account/create', data=form_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"account": "testuser@email.com", "created": "success"})

    @patch('ras_rm_auth_service.resources.account.transactional_session')
    def test_user_create_unable_to_commit(self, session_scope_mock):
        """
        Test create user end point unable to commit account
        """
        session_scope_mock.side_effect = SQLAlchemyError()
        form_data = {"username": "testuser@email.com", "password": "password"}

        response = self.client.post('/api/account/create', data=form_data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"detail": "Unable to commit account to database"})

    def test_user_create_email_conflict(self):
        """
        Given a user account has been created
        When another account is being created with the same email
        Then a conflict error is thrown
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data)

        # When
        response = self.client.post('/api/account/create', data=form_data)

        # Then
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_json(), {"detail": "Unable to create account with requested username"})

    def test_user_create_bad_request(self):
        """
        Test create user end point with bad request
        """
        form_data = {"password": "password"}  # missing username

        response = self.client.post('/api/account/create', data=form_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"detail": "Missing 'username' or 'password'"})

    def test_user_can_be_verified(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then user is verified
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data)

        # When

        form_data = {"username": "testuser@email.com", "account_verified": "true"}
        response = self.client.put('/api/account/create', data=form_data)

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
        response = self.client.put('/api/account/create', data=data)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "detail": "Unauthorized user credentials. This user does not exist on the OAuth2 server"
        })

    def test_user_must_verify_with_true_or_false(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then I can login
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data)

        # When

        form_data = {"username": "testuser@email.com", "account_verified": "garbage"}
        response = self.client.put('/api/account/create', data=form_data)

        # Then
        self.assertEqual(response.status_code, 400)

    @patch('ras_rm_auth_service.resources.account.transactional_session')
    def test_user_verified_unable_to_commit(self, session_scope_mock):
        """
        Test verify user end point unable to commit updateed account
        """
        session_scope_mock.side_effect = SQLAlchemyError()
        form_data = {"username": "testuser@email.com", "account_verified": "true"}
        response = self.client.put('/api/account/create', data=form_data)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"detail": "Unable to commit updated account to database"})
