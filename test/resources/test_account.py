import base64
import unittest
from datetime import UTC, datetime
from unittest.mock import patch

from sqlalchemy.exc import SQLAlchemyError

from ras_rm_auth_service.models import models
from run import create_app


class TestAccount(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        models.Base.metadata.drop_all(self.app.db)
        models.Base.metadata.create_all(self.app.db)
        self.app.db.session.commit()
        self.client = self.app.test_client()

        auth = "{}:{}".format("admin", "secret").encode("utf-8")
        self.headers = {"Authorization": "Basic %s" % base64.b64encode(bytes(auth)).decode("ascii")}

    def test_user_create(self):
        """
        Test create user end point
        """
        form_data = {"username": "testuser@email.com", "password": "password"}

        response = self.client.post("/api/account/create", data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"account": "testuser@email.com", "created": "success"})

    @patch("ras_rm_auth_service.resources.account.transactional_session")
    def test_user_create_unable_to_commit(self, session_scope_mock):
        """
        Test create user end point unable to commit account
        """
        session_scope_mock.side_effect = SQLAlchemyError()
        form_data = {"username": "testuser@email.com", "password": "password"}

        response = self.client.post("/api/account/create", data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {"title": "Auth service account create db error", "detail": "Unable to commit account to database"},
        )

    def test_user_create_email_conflict(self):
        """
        Given a user account has been created
        When another account is being created with the same email
        Then a server error is thrown
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)

        # When
        response = self.client.post("/api/account/create", data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {
                "title": "Auth service account create error",
                "detail": "Unable to create account with requested username",
            },
        )

    def test_user_create_bad_request(self):
        """
        Test create user end point with bad request
        """
        form_data = {"password": "password"}  # missing username

        response = self.client.post("/api/account/create", data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {"title": "Authentication error in Auth service", "detail": "Missing 'username' or 'password'"},
        )

    def test_user_can_be_verified(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then user is verified
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)

        # When

        form_data = {"username": "testuser@email.com", "account_verified": "true"}
        response = self.client.put("/api/account/create", data=form_data, headers=self.headers)

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
        response = self.client.put("/api/account/create", data=data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json(),
            {
                "title": "Auth service account update user error",
                "detail": "Unauthorized user credentials. This user does not exist on the Auth server",
            },
        )

    def test_user_must_verify_with_true_or_false(self):
        """
        Given a user account has been created but not verified
        When I verify the account
        Then I can login
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)

        # When

        form_data = {"username": "testuser@email.com", "account_verified": "garbage"}
        response = self.client.put("/api/account/create", data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 400)

    @patch("ras_rm_auth_service.resources.account.transactional_session")
    def test_user_verified_unable_to_commit(self, session_scope_mock):
        """
        Test verify user end point unable to commit updateed account
        """
        session_scope_mock.side_effect = SQLAlchemyError()
        form_data = {"username": "testuser@email.com", "account_verified": "true"}
        response = self.client.put("/api/account/create", data=form_data, headers=self.headers)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {
                "title": "Auth service account update user error",
                "detail": "Unable to commit updated account to database",
            },
        )

    def test_user_can_change_email(self):
        """
        Given a user account has been created
        When I change account email
        Then user email is updated
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)

        # When

        form_data = {"username": "testuser@email.com", "new_username": "anotheremail@email.com"}
        response = self.client.put("/api/account/create", data=form_data, headers=self.headers)

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
        response = self.client.put("/api/account/create", data=data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json(),
            {
                "title": "Auth service account update user error",
                "detail": "Unauthorized user credentials. This user does not exist on the Auth server",
            },
        )

    def test_user_change_email_conflict(self):
        """
        Given a user account has been created
        When another account is being updated with the same email
        Then a server error is thrown
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)

        form_data = {"username": "anothertestuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)

        # When
        data = {"username": "testuser@email.com", "new_username": "anothertestuser@email.com"}
        response = self.client.put("/api/account/create", data=data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {
                "title": "Auth service account update user error",
                "detail": "Unable to commit updated account to database",
            },
        )

    def test_user_can_change_password(self):
        """
        Given a user account has been created
        When I change account password
        Then user password is updated
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)

        # When
        form_data = {"username": "testuser@email.com", "password": "anotherpassword"}
        response = self.client.put("/api/account/create", data=form_data, headers=self.headers)

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
        self.client.post("/api/account/create", data=form_data, headers=self.headers)

        form_data = {"username": "testuser@email.com", "password": "wrongpassword"}
        for _ in range(10):
            self.client.post("/api/v1/tokens/", data=form_data, headers=self.headers)

        # When
        form_data = {"username": "testuser@email.com", "account_locked": False}
        response = self.client.put("/api/account/create", data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        # Then
        form_data = {"username": "testuser@email.com", "password": "password"}
        response = self.client.post("/api/v1/tokens/", data=form_data, headers=self.headers)
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
        self.client.post("/api/account/create", data=form_data, headers=self.headers)
        # When
        form_data = {"username": "testuser@email.com"}

        response = self.client.delete("/api/account/user", data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 204)

    def test_delete_user_force_delete(self):
        """
        Test delete user end point

                Given a locked user exists
                When I unlock account
                Then account should be deleted and verified
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)
        # When
        form_data = {"username": "testuser@email.com", "force_delete": True}

        response = self.client.delete("/api/account/user", data=form_data, headers=self.headers)
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
        self.client.post("/api/account/create", data=form_data, headers=self.headers)
        # When
        form_data = {"username": "TeStUsEr@EmAiL.com"}

        response = self.client.delete("/api/account/user", data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 204)

    @patch("ras_rm_auth_service.resources.account.transactional_session")
    def test_delete_user_unable_to_commit(self, session_scope_mock):
        """
        Test delete user end point unable to commit account
        """
        session_scope_mock.side_effect = SQLAlchemyError()
        form_data = {"username": "testuser@email.com"}

        response = self.client.delete("/api/account/user", data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {"title": "Auth service delete user error", "detail": "Unable to commit delete operation"},
        )

    def test_delete_user_bad_request(self):
        """
        Test delete user end point with bad request
        """
        form_data = {}  # missing username

        response = self.client.delete("/api/account/user", data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(), {"title": "Auth service delete user error", "detail": "Missing 'username'"}
        )

    def test_delete_user_that_does_not_exist(self):
        """
        Given no user account exist
        When delete a non-existing the account
        Then get an authentication error
        """
        # Given
        # Verify the user doesn't exist by trying to change one that doesn't exist.
        data = {"username": "idonotexist@example.com", "password": "password"}
        response = self.client.put("/api/account/create", data=data, headers=self.headers)
        self.assertEqual(response.status_code, 401)

        # When
        form_data = {"username": "idonotexist@example.com"}
        response = self.client.delete("/api/account/user", data=form_data, headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json(),
            {"title": "Auth service delete user error", "detail": "This user does not exist on the Auth server"},
        )

    def test_get_user_account(self):
        """
        Test get user end point

                Given a user exists
                When get user account
                Then account should be retrieved
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)
        # When
        response = self.client.get("/api/account/user/testuser@email.com", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["mark_for_deletion"], False)

    def test_user_account_that_does_not_exist(self):
        """
        Given no user account exist
        When get a non-existing the account
        Then get an error
        """
        # Given
        # Verify the user doesn't exist by trying to change one that doesn't exist.
        data = {"username": "idonotexist@example.com", "password": "password"}
        response = self.client.put("/api/account/create", data=data, headers=self.headers)
        self.assertEqual(response.status_code, 401)

        # When
        response = self.client.get("/api/account/user/idonotexist@example.com", headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json(),
            {"title": "Auth service get user error", "detail": "This user does not exist on the Auth server"},
        )

    def test_user_account_bad_request(self):
        """
        Test get user end point with bad request
        """
        response = self.client.get("/api/account/user/", headers=self.headers)

        self.assertEqual(response.status_code, 405)

    @patch("ras_rm_auth_service.resources.account.transactional_session")
    def test_get_user_with_SQL_error(self, session_mock):
        # Given
        session_mock.side_effect = SQLAlchemyError()

        # When
        response = self.client.get("/api/account/user/testuser@email.com", headers=self.headers)

        # Then
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"detail": "SQLAlchemyError", "title": "Auth service get user error"})

    def test_patch_user_account(self):
        """
        Test undo delete user end point
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)
        self.client.delete("/api/account/user", data=form_data, headers=self.headers)
        # When
        response = self.client.get("/api/account/user/testuser@email.com", headers=self.headers)
        self.assertEqual(response.get_json()["mark_for_deletion"], True)
        form_data_new = {"mark_for_deletion": False}
        # Then
        upsert = self.client.patch("/api/account/user/testuser@email.com", data=form_data_new, headers=self.headers)
        self.assertEqual(upsert.status_code, 204)
        new_response = self.client.get("/api/account/user/testuser@email.com", headers=self.headers)
        self.assertEqual(new_response.get_json()["mark_for_deletion"], False)

    def test_patch_user_account_force_delete(self):
        """
        Test undo delete user end point
        """
        # Given
        form_data = {"username": "testuser@email.com", "password": "password", "force_delete": True}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)
        self.client.delete("/api/account/user", data=form_data, headers=self.headers)
        # When
        response = self.client.get("/api/account/user/testuser@email.com", headers=self.headers)
        self.assertEqual(response.get_json()["mark_for_deletion"], True)
        form_data_new = {"mark_for_deletion": False, "force_delete": False}
        # Then
        upsert = self.client.patch("/api/account/user/testuser@email.com", data=form_data_new, headers=self.headers)
        self.assertEqual(upsert.status_code, 204)
        new_response = self.client.get("/api/account/user/testuser@email.com", headers=self.headers)
        self.assertEqual(new_response.get_json()["mark_for_deletion"], False)

    def test_patch_user_that_does_not_exist(self):
        """
        Given no user account exist
        When patch a non-existing the account
        Then get an error
        """
        # Given
        # Verify the user doesn't exist by trying to change one that doesn't exist.
        data = {"username": "idonotexist@example.com", "password": "password"}
        response = self.client.put("/api/account/create", data=data, headers=self.headers)
        self.assertEqual(response.status_code, 401)

        # When
        form_data_new = {"mark_for_deletion": False}
        response = self.client.patch(
            "/api/account/user/idonotexist@example.com", data=form_data_new, headers=self.headers
        )

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json(),
            {"title": "Auth service undo delete user error", "detail": "This user does not exist on the Auth server"},
        )

    def test_patch_user_bad_request(self):
        """
        Test patch user end point with bad request
        """
        response = self.client.patch(
            "/api/account/user/idonotexist@example.com", data={"something": "something"}, headers=self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {"title": "Bad Request error in Auth service", "detail": "Patch data validation failed"},
        )

    @patch("ras_rm_auth_service.resources.account.transactional_session")
    def test_undo_delete_user_unable_to_commit(self, session_scope_mock):
        """
        Test patch user end point unable to commit account
        """
        session_scope_mock.side_effect = SQLAlchemyError()
        form_data = {"mark_for_deletion": False}

        response = self.client.patch("/api/account/user/idonotexist@example.com", data=form_data, headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {"title": "Auth service undo delete user error", "detail": "Unable to commit undo delete operation"},
        )

    def test_patch_user_account_first_notification(self):
        """
        Test update first_notification
        """
        time = datetime.now(UTC)
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)
        # When
        response = self.client.get("/api/account/user/testuser@email.com", headers=self.headers)
        self.assertEqual(response.get_json()["first_notification"], None)
        form_data_new = {"first_notification": time}
        # Then
        upsert = self.client.patch("/api/account/user/testuser@email.com", data=form_data_new, headers=self.headers)
        self.assertEqual(upsert.status_code, 204)
        new_response = self.client.get("/api/account/user/testuser@email.com", headers=self.headers)
        self.assertIsNot(None, new_response.get_json()["first_notification"])

    def test_patch_user_account_second_notification(self):
        """
        Test update first_notification
        """
        time = datetime.now(UTC)
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)
        # When
        response = self.client.get("/api/account/user/testuser@email.com", headers=self.headers)
        self.assertEqual(response.get_json()["first_notification"], None)
        form_data_new = {"second_notification": time}
        # Then
        upsert = self.client.patch("/api/account/user/testuser@email.com", data=form_data_new, headers=self.headers)
        self.assertEqual(upsert.status_code, 204)
        new_response = self.client.get("/api/account/user/testuser@email.com", headers=self.headers)
        self.assertIsNot(None, new_response.get_json()["second_notification"])

    def test_patch_user_account_third_notification(self):
        """
        Test update first_notification
        """
        time = datetime.now(UTC)
        # Given
        form_data = {"username": "testuser@email.com", "password": "password"}
        self.client.post("/api/account/create", data=form_data, headers=self.headers)
        # When
        response = self.client.get("/api/account/user/testuser@email.com", headers=self.headers)
        self.assertEqual(response.get_json()["first_notification"], None)
        form_data_new = {"third_notification": time}
        # Then
        upsert = self.client.patch("/api/account/user/testuser@email.com", data=form_data_new, headers=self.headers)
        self.assertEqual(upsert.status_code, 204)
        new_response = self.client.get("/api/account/user/testuser@email.com", headers=self.headers)
        self.assertIsNot(None, new_response.get_json()["third_notification"])
