import base64
import unittest
from unittest.mock import patch

from sqlalchemy.exc import SQLAlchemyError

from ras_rm_auth_service.models import models
from ras_rm_auth_service.resources.tokens import obfuscate_email
from run import create_app

AUTH_TOKEN_ERROR = "Auth service tokens error"
TEST_USER_EMAIL = "testuser@email.com"
ACCOUNT_CREATE_URL = "/api/account/create"
TOKENS_URL = "/api/v1/tokens/"
MISSING_USERNAME_PASSWORD = "Missing 'username' or 'password'"


class TestTokens(unittest.TestCase):
    def setUp(self):
        app = create_app("TestingConfig")
        models.Base.metadata.drop_all(app.db)
        models.Base.metadata.create_all(app.db)
        app.db.session.commit()
        self.client = app.test_client()

        auth = "{}:{}".format("admin", "secret").encode("utf-8")
        self.headers = {"Authorization": "Basic %s" % base64.b64encode(bytes(auth)).decode("ascii")}
        self.username = TEST_USER_EMAIL

    def test_verified_user_can_login(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then I can login
        """
        # Given
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        self.client.post(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        # When

        form_data = {"username": TEST_USER_EMAIL, "account_verified": "true"}
        response = self.client.put(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 201)

        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 204)

    def test_verifed_user_can_login_with_case_insensitive_email(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then I can login with a case insensitive email address
        """
        # Given
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        self.client.post(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        # When

        form_data = {"username": TEST_USER_EMAIL, "account_verified": "true"}
        response = self.client.put(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 201)

        form_data = {"username": "TeStUsER@eMAil.com", "password": "password"}
        response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 204)

    def test_unverifed_user_cannot_login(self):
        """
        Given a user account has been created but not verified
        When I login
        Then I should be presented with error
        """
        # Given
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        self.client.post(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        # When
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"title": AUTH_TOKEN_ERROR, "detail": "User account not verified"})

    def test_wrong_password_is_rejected(self):
        """
        Given a user account has been created and verified
        When I attempt login with wrong password
        Then user is rejected
        """
        # Given
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        self.client.post(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        # When

        form_data = {"username": TEST_USER_EMAIL, "account_verified": "true"}
        response = self.client.put(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 201)

        form_data = {"username": TEST_USER_EMAIL, "password": "wrongpassword"}
        response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"title": AUTH_TOKEN_ERROR, "detail": "Unauthorized user credentials"})

    def test_user_does_not_exist(self):
        """
        Given a no user exists
        When I verify the account
        Then i should b presented with an error
        """
        # Given
        # no users

        # When
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json(),
            {
                "title": AUTH_TOKEN_ERROR,
                "detail": "Unauthorized user credentials. This user does not exist on the Auth server",
            },
        )

    def test_post_tokens_missing_password_bad_request(self):
        """
        Given a user exists
        When I verify the account without password
        Then i should be presented with bad request
        """
        # Given
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        self.client.post(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        # When
        form_data = {"username": TEST_USER_EMAIL}
        response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"title": AUTH_TOKEN_ERROR, "detail": MISSING_USERNAME_PASSWORD})

    def test_post_tokens_missing_username_bad_request(self):
        """
        Given a user exists
        When I verify the account without username
        Then i should be presented with bad request
        """
        # Given
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        self.client.post(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        # When
        form_data = {"password": "password"}
        response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"title": AUTH_TOKEN_ERROR, "detail": MISSING_USERNAME_PASSWORD})

    def test_account_locked_after_10_failed_attempts(self):
        """
        Given a verfied user exists
        When I verify the account wrong 10 times
        Then account should be locked
        And should not be able to login with correct password
        """
        # Given
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        self.client.post(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        form_data = {"username": TEST_USER_EMAIL, "account_verified": "true"}
        self.client.put(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        # When
        form_data = {"username": TEST_USER_EMAIL, "password": "wrongpassword"}
        for _ in range(9):
            response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)
            self.assertEqual(
                response.get_json(), {"title": AUTH_TOKEN_ERROR, "detail": "Unauthorized user credentials"}
            )

        # tenth try
        response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"title": AUTH_TOKEN_ERROR, "detail": "User account locked"})

        # And Then
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"title": AUTH_TOKEN_ERROR, "detail": "User account locked"})

    def test_post_tokens_empty_password_bad_request(self):
        """
        Given a user exists
        When I verify the account without password
        Then i should be presented with bad request
        """
        # Given
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        self.client.post(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        # When
        form_data = {"username": TEST_USER_EMAIL, "password": ""}
        response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"title": AUTH_TOKEN_ERROR, "detail": MISSING_USERNAME_PASSWORD})

    def test_post_tokens_empty_username_bad_request(self):
        """
        Given a user exists
        When I verify the account without username
        Then i should be presented with bad request
        """
        # Given
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        self.client.post(ACCOUNT_CREATE_URL, data=form_data, headers=self.headers)

        # When
        form_data = {"username": "", "password": "password"}
        response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"title": AUTH_TOKEN_ERROR, "detail": MISSING_USERNAME_PASSWORD})

    def test_invalid_basic_auth_user_returns_401_with_detail(self):
        auth_credentials = "notadmin:secret".encode("utf-8")
        self._test_invalid_basic_auth_credentials(auth_credentials)

    def test_invalid_basic_auth_password_returns_401_with_detail(self):
        auth_credentials = "admin:notsecret".encode("utf-8")
        self._test_invalid_basic_auth_credentials(auth_credentials)

    def _test_invalid_basic_auth_credentials(self, auth_credentials):
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        headers = {"Authorization": "Basic %s" % base64.b64encode(bytes(auth_credentials)).decode("ascii")}

        response = self.client.post(ACCOUNT_CREATE_URL, data=form_data, headers=headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json(), {"title": "Basic auth error in Auth service", "detail": "Name or password incorrect"}
        )

    def test_obfuscate_email(self):
        """Test obfuscate email correctly changes inputted emails"""

        # TODO fix function for bottom scenario
        test_scenarios = [
            ["example@example.com", "e*****e@e*********m"],
            ["prefix@domain.co.uk", "p****x@d**********k"],
            ["first.name@place.gov.uk", "f********e@p**********k"],
            ["me+addition@gmail.com", "m*********n@g*******m"],
            ["a.b.c.someone@example.com", "a***********e@e*********m"],
            ["john.smith123456@londinium.ac.co.uk", "j**************6@l****************k"],
            ["me!?@example.com", "m**?@e*********m"],
            ["m@m.com", "m@m***m"],
        ]

        for scenario in test_scenarios:
            self.assertEqual(obfuscate_email(scenario[0]), scenario[1])

    @patch("ras_rm_auth_service.resources.tokens.transactional_session")
    def test_post_tokens_with_SQL_error(self, session_mock):
        # Given
        session_mock.side_effect = SQLAlchemyError()

        # When
        form_data = {"username": TEST_USER_EMAIL, "password": "password"}
        response = self.client.post(TOKENS_URL, data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"detail": "SQLAlchemyError", "title": AUTH_TOKEN_ERROR})
