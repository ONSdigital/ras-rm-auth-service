import base64
import unittest

import pytest
from ras_rm_auth_service.models import models
from ras_rm_auth_service.resources.tokens import obfuscate_email
from run import create_app


class TestTokens(unittest.TestCase):

    def setUp(self):
        app = create_app('TestingConfig')
        models.Base.metadata.drop_all(app.db)
        models.Base.metadata.create_all(app.db)
        app.db.session.commit()
        self.client = app.test_client()

        auth = "{}:{}".format('admin', 'secret').encode('utf-8')
        self.headers = {
            'Authorization': 'Basic %s' % base64.b64encode(bytes(auth)).decode("ascii")
        }

    def test_verifed_user_can_login(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then I can login
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When

        form_data = {"username": "testuser@email.com",
                     "account_verified": "true"}
        response = self.client.put('/api/account/create', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 201)

        form_data = {"username": "testuser@email.com", "password": "password"}
        response = self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 204)

    def test_verifed_user_can_login_with_case_insensitive_email(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then I can login with a case insensitive email address
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create',
                         data=form_data, headers=self.headers)

        # When

        form_data = {"username": "testuser@email.com",
                     "account_verified": "true"}
        response = self.client.put(
            '/api/account/create', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 201)

        form_data = {"username": "TeStUsER@eMAil.com", "password": "password"}
        response = self.client.post(
            '/api/v1/tokens/', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 204)

    def test_unverifed_user_cannot_login(self):
        """
        Given a user account has been created but not verified
        When I login
        Then I should be presented with error
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When
        form_data = {"username": "testuser@email.com", "password": "password"}
        response = self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)

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
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When

        form_data = {"username": "testuser@email.com", "account_verified": "true"}
        response = self.client.put('/api/account/create', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 201)

        form_data = {"username": "testuser@email.com", "password": "wrongpassword"}
        response = self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"detail": "Unauthorized user credentials"})

    def test_user_does_not_exist(self):
        """
        Given a no user exists
        When I verify the account
        Then i should b presented with an error
        """
        # Given
        # no users

        # When
        form_data = {"username": "testuser@email.com", "password": "password"}
        response = self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(),
                         {"detail": "Unauthorized user credentials. This user does not exist on the OAuth2 server"})

    def test_post_tokens_missing_password_bad_request(self):
        """
        Given a user exists
        When I verify the account without password
        Then i should be presented with bad request
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When
        form_data = {"username": "testuser@email.com"}
        response = self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"detail": "Missing 'username' or 'password'"})

    def test_post_tokens_missing_username_bad_request(self):
        """
        Given a user exists
        When I verify the account without username
        Then i should be presented with bad request
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When
        form_data = {"password": "password"}
        response = self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"detail": "Missing 'username' or 'password'"})

    def test_account_locked_after_10_failed_attempts(self):
        """
        Given a verfied user exists
        When I verify the account wrong 10 times
        Then account should be locked
        And should not be able to login with correct password
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        form_data = {"username": "testuser@email.com", "account_verified": "true"}
        self.client.put('/api/account/create', data=form_data, headers=self.headers)

        # When
        form_data = {"username": "testuser@email.com", "password": "wrongpassword"}
        for _ in range(9):
            response = self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)
            self.assertEqual(response.get_json(), {"detail": "Unauthorized user credentials"})

        # tenth try
        response = self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"detail": "User account locked"})

        # And Then
        form_data = {"username": "testuser@email.com", "password": "password"}
        response = self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"detail": "User account locked"})

    def test_post_tokens_empty_password_bad_request(self):
        """
        Given a user exists
        When I verify the account without password
        Then i should be presented with bad request
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When
        form_data = {"username": "testuser@email.com", "password": ""}
        response = self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"detail": "Missing 'username' or 'password'"})

    def test_post_tokens_empty_username_bad_request(self):
        """
        Given a user exists
        When I verify the account without username
        Then i should be presented with bad request
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post('/api/account/create', data=form_data, headers=self.headers)

        # When
        form_data = {"username": "", "password": "password"}
        response = self.client.post('/api/v1/tokens/', data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"detail": "Missing 'username' or 'password'"})

    def test_invalid_basic_auth_user_returns_401_with_detail(self):
        form_data = {"username": "testuser@email.com", "password": "password"}
        auth = "notadmin:secret".encode('utf-8')
        headers = {'Authorization': 'Basic %s' % base64.b64encode(bytes(auth)).decode("ascii")}

        response = self.client.post('/api/account/create', data=form_data, headers=headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"detail": "Incorrect basic auth"})

    def test_invalid_basic_auth_password_returns_401_with_detail(self):
        form_data = {"username": "testuser@email.com", "password": "password"}
        auth = "admin:notsecret".encode('utf-8')
        headers = {'Authorization': 'Basic %s' % base64.b64encode(bytes(auth)).decode("ascii")}

        response = self.client.post('/api/account/create', data=form_data, headers=headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"detail": "Incorrect basic auth"})

    @pytest.mark.parametrize('email, obfuscated_email', [
        ('example@example.com', 'e*****e@e*********m'),
        ('prefix@domain.co.uk', 'p****x@d*********k'),
        ('first.name@place.gov.uk', 'f********e@p********k'),
        ('me+addition@gmail.com', 'm*********n@g*******m'),
        ('a.b.c.someone@example.com', 'a***********e@e*********m'),
        ('john.smith123456@londinium.ac.co.uk', 'j**************6@l****************k'),
        ('me!?@example.com', 'm**?@e*********m'),
        ('m@m.com', 'm@m***m'),
    ])
    @staticmethod
    def test_obfuscate_email(email, obfuscated_email):
        """Test obfuscate email correctly changes inputted emails"""
        assert obfuscate_email(email) == obfuscated_email
