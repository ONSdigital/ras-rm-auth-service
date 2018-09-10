import unittest

from ras_rm_auth_service.models import models
from run import create_app


class TestTokens(unittest.TestCase):

    def setUp(self):
        app = create_app('TestingConfig')
        models.Base.metadata.drop_all(app.db)
        models.Base.metadata.create_all(app.db)
        app.db.session.commit()
        self.client = app.test_client()

    def test_verifed_user_can_login(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then I can login
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data)

        # When

        form_data = {"username": "testuser@email.com",
                     "account_verified": "true"}
        response = self.client.put('/api/account/create', data=form_data)

        # Then
        self.assertEqual(response.status_code, 201)

        form_data = {"grant_type": "password", "username": "testuser@email.com", "password": "password"}
        response = self.client.post('/api/v1/tokens/', data=form_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(),
                         {"id": 895725, "access_token": "fakefake-4bc1-4254-b43a-f44791ecec75", "expires_in": 3600,
                          "token_type": "Bearer", "scope": "", "refresh_token": "fakefake-2151-4b11-b0d5-a9a68f2c53de"})

    def test_unverifed_user_cannot_login(self):
        """
        Given a user account has been created but not verified
        When I login
        Then I should be presented with error
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data)

        # When
        form_data = {"grant_type": "password", "username": "testuser@email.com", "password": "password"}
        response = self.client.post('/api/v1/tokens/', data=form_data)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"detail": "User account not verified"})

    def test_wrong_password_is_rejected(self):
        """
        Given a user account has been created and verified
        When I attempt login with wrong password
        Then user is rejected
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data)

        # When

        form_data = {"username": "testuser@email.com", "account_verified": "true"}
        response = self.client.put('/api/account/create', data=form_data)

        # Then
        self.assertEqual(response.status_code, 201)

        form_data = {"grant_type": "password", "username": "testuser@email.com", "password": "wrongpassword"}
        response = self.client.post('/api/v1/tokens/', data=form_data)
        self.assertEqual(response.status_code, 401)

    def test_user_does_not_exist(self):
        """
        Given a no user exists
        When I verify the account
        Then i should b presented with an error
        """
        # Given
        # no users

        # When
        form_data = {"grant_type": "password", "username": "testuser@email.com", "password": "password"}
        response = self.client.post('/api/v1/tokens/', data=form_data)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(),
                         {"detail": "Unauthorized user credentials. This user does not exist on the OAuth2 server"})
