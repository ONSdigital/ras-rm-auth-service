import json
from urllib.parse import urlencode

from django.test import TestCase
from django.test.client import MULTIPART_CONTENT, BOUNDARY, encode_multipart
import base64


# curl - X POST http: // localhost: 8040 / api / account / create / -u ons @ ons.gov: password \
# -d 'username=testuser@email.com&password=password&client_id=ons@ons.gov.uk&client_secret=password'


class UserControllerTests(TestCase):
    def test_user_create(self):
        """
        Test create user end point
        """
        auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'username:password').decode("utf-8")}
        form_data = {"username": "testuser@email.com", "password": "password",
                     "client_id": "ons@ons.gov.uk", "client_secret": "password"}

        response = self.client.post('/api/account/create', form_data, **auth_headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content), {"account": "testuser@email.com", "created": "success"})

    def test_cannot_verify_a_user_that_does_not_exist(self):
        """
        Given no accounts exist
        When I verify a non-existant the account
        Then I get an authetication error
        """
        # Given
        # There are no accounts

        # When

        data = {"username": "idonotexist@example.com", "client_id": "ons@ons.gov.uk", "client_secret": "password",
                "account_verified": "true"}
        form_data = urlencode(data)
        auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'ons@ons.gov.uk:password').decode("utf-8")}
        response = self.client.put('/api/account/create', form_data, content_type='application/x-www-form-urlencoded',
                                   **auth_headers)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content), {
            "detail": "Unknown user credentials. This user does not exist on the OAuth2 server"
        })

    def test_verifed_user_can_login(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then I can login
        """
        # Given
        auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'username:password').decode("utf-8")}
        form_data = {"username": "testuser@email.com", "password": "password",
                     "client_id": "ons@ons.gov.uk", "client_secret": "password"}
        self.client.post('/api/account/create', form_data, **auth_headers)

        # When

        form_data = {"username": "testuser@email.com", "client_id": "ons@ons.gov.uk", "client_secret": "password",
                     "account_verified": "true"}
        auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'ons@ons.gov.uk:password').decode("utf-8")}
        response = self.client.put('/api/account/create', urlencode(form_data),
                                   content_type='application/x-www-form-urlencoded', **auth_headers)

        # Then
        self.assertEqual(response.status_code, 201)

        form_data = {"grant_type": "password", "username": "testuser@email.com", "password": "password",
                     "client_id": "ons@ons.gov.uk", "client_secret": "password"}
        response = self.client.post('/api/v1/tokens', form_data)
        self.assertEqual(response.status_code, 201)


    def test_user_must_verify_with_true_or_false(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then I can login
        """
        # Given
        auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'username:password').decode("utf-8")}
        form_data = {"username": "testuser@email.com", "password": "password",
                     "client_id": "ons@ons.gov.uk", "client_secret": "password"}
        self.client.post('/api/account/create', form_data, **auth_headers)

        # When

        form_data = {"username": "testuser@email.com", "client_id": "ons@ons.gov.uk", "client_secret": "password",
                     "account_verified": "garbage"}
        auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'ons@ons.gov.uk:password').decode("utf-8")}
        response = self.client.put('/api/account/create', urlencode(form_data),
                                   content_type='application/x-www-form-urlencoded', **auth_headers)

        # Then
        self.assertEqual(response.status_code, 400)

    def test_unverifed_user_cannot_login(self):
        """
        Given a user account has been created but not verified
        When I login
        Then I should be presented with error
        """
        # Given
        auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'username:password').decode("utf-8")}
        form_data = {"username": "testuser@email.com", "password": "password",
                     "client_id": "ons@ons.gov.uk", "client_secret": "password"}
        self.client.post('/api/account/create', form_data, **auth_headers)

        # When
        form_data = {"grant_type": "password", "username": "testuser@email.com", "password": "password",
                     "client_id": "ons@ons.gov.uk", "client_secret": "password"}
        response = self.client.post('/api/v1/tokens', form_data, content_type="application/json")

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content), {"detail": "User account not verified"})

    def test_wrong_password_is_rejected(self):
        """
        Given a user account has been created and verified
        When I attempt login with wrong password
        Then user is rejected
        """
        # Given
        auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'username:password').decode("utf-8")}
        form_data = {"username": "testuser@email.com", "password": "password",
                     "client_id": "ons@ons.gov.uk", "client_secret": "password"}
        self.client.post('/api/account/create', form_data, **auth_headers)

        # When

        form_data = {"username": "testuser@email.com", "client_id": "ons@ons.gov.uk", "client_secret": "password",
                     "account_verified": "true"}
        auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'ons@ons.gov.uk:password').decode("utf-8")}
        response = self.client.put('/api/account/create', urlencode(form_data),
                                   content_type='application/x-www-form-urlencoded', **auth_headers)

        # Then
        self.assertEqual(response.status_code, 201)

        form_data = {"grant_type": "password", "username": "testuser@email.com", "password": "wrongpassword",
                     "client_id": "ons@ons.gov.uk", "client_secret": "password"}
        response = self.client.post('/api/v1/tokens', form_data)
        self.assertEqual(response.status_code, 401)

    def test_health(self):
        """
        Given application is deployed
        When I hit the health endpoint
        Then I should be presented with success
        """
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)