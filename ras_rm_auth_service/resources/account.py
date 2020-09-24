import base64
import json
import logging
from datetime import datetime, timedelta

import requests
from flask import Blueprint, make_response, request, jsonify
from marshmallow import ValidationError, EXCLUDE
from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound
import structlog
from ras_rm_auth_service.basic_auth import auth
from ras_rm_auth_service.db_session_handlers import transactional_session
from ras_rm_auth_service.models.models import User, AccountSchema
from ras_rm_auth_service.resources.tokens import obfuscate_email
from flask import current_app as app

logger = structlog.wrap_logger(logging.getLogger(__name__))

account = Blueprint('account_view', __name__, url_prefix='/api/account')

account_schema = AccountSchema(unknown=EXCLUDE)


@account.before_request
@auth.login_required
def before_account_view():
    pass


@account.route('/create', methods=['POST'])
def post_account():
    post_params = request.form

    try:
        payload = account_schema.load(post_params)
    except ValidationError as ex:
        logger.info("Missing request parameter", exc_info=ex)
        return make_response(jsonify({"title": "Authentication error in Auth service",
                                      "detail": "Missing 'username' or 'password'"}), 400)

    try:
        with transactional_session() as session:
            user = User(username=payload.get('username'))
            user.set_hashed_password(payload.get('password'))
            session.add(user)
    except IntegrityError:
        logger.exception("Unable to create account with requested username")
        return make_response(jsonify({"title": "Auth service account create error",
                                      "detail": "Unable to create account with requested username"}), 500)
    except SQLAlchemyError:
        logger.exception("Unable to commit account to database")
        return make_response(jsonify({"title": "Auth service account create db error",
                                      "detail": "Unable to commit account to database"}), 500)

    logger.info("Successfully created account", user_id=user.id)
    return make_response(jsonify({"account": user.username, "created": "success"}), 201)


@account.route('/create', methods=['PUT'])
def put_account():
    put_params = request.form

    try:
        username = put_params['username']
    except KeyError as ex:
        logger.info("Missing request parameter", exc_info=ex)
        return make_response(jsonify({"title": "Auth service account update user error",
                                      "detail": "Missing 'username'"}), 400)

    try:
        with transactional_session() as session:
            user = session.query(User).filter(User.username == username).first()

            if not user:
                logger.info("User does not exist")
                return make_response(
                    jsonify({"title": "Auth service account update user error",
                             "detail": "Unauthorized user credentials. This user does not exist on the Auth server"}),
                    401)

            user.update_user(put_params)
    except ValueError as ex:
        logger.info("Request param is an invalid type", exc_info=ex)
        return make_response(jsonify({"title": "Auth service account update user error",
                                      "detail": "account_verified status is invalid"}), 400)
    except SQLAlchemyError:
        logger.exception("Unable to commit updated account to database")
        return make_response(jsonify({"title": "Auth service account update user error",
                                      "detail": "Unable to commit updated account to database"}), 500)

    logger.info("Successfully updated account", user_id=user.id)
    return make_response(jsonify({"account": user.username, "updated": "success"}), 201)


@account.route('/user', methods=['DELETE'])
def delete_account():
    """
    Updates user data to be marked for deletion.
    """
    params = request.form
    try:
        username = params['username']
        logger.info("Deleting user", username=obfuscate_email(username))
        with transactional_session() as session:
            user = session.query(User).filter(func.lower(User.username) == username.lower()).one()
            user.mark_for_deletion = True
            session.commit()
    except KeyError:
        logger.exception("Missing request parameter")
        return make_response(jsonify({"title": "Auth service delete user error",
                                      "detail": "Missing 'username'"}), 400)
    except NoResultFound:
        logger.info("User does not exist", username=obfuscate_email(username))
        return make_response(
            jsonify({"title": "Auth service delete user error",
                     "detail": "This user does not exist on the Auth server"}), 404)

    except SQLAlchemyError:
        logger.exception("Unable to commit delete operation", username=obfuscate_email(username))
        return make_response(jsonify({"title": "Auth service delete user error",
                                      "detail": "Unable to commit delete operation"}), 500)

    logger.info("Successfully deleted user", username=obfuscate_email(username))
    return '', 204


@account.route('/batch/users', methods=['DELETE'])
def delete_accounts():
    """
    Deletes all user marked for deletion. to be called from scheduler
    """
    try:
        logger.info("Scheduler deleting users marked for deletion")
        with transactional_session() as session:
            marked_for_deletion_users = session.query(User).filter(User.mark_for_deletion == True)  # noqa
            if marked_for_deletion_users.count() > 0:
                logger.info("sending request to party service to remove ")
                delete_party_respondents(marked_for_deletion_users)
                marked_for_deletion_users.delete()
                logger.info("Scheduler successfully deleted users marked for deletion")
            else:
                logger.info("No user marked for deletion at this time. Nothing to delete.")

    except SQLAlchemyError:
        logger.exception("Unable to perform scheduler delete operation")
        return make_response(jsonify({"title": "Scheduler operation for delete users error",
                                      "detail": "Unable to perform delete operation"}), 500)
    return '', 204


@account.route('/batch/users/mark-for-deletion', methods=['DELETE'])
def mark_for_deletion_accounts():
    """
    Deletes all user marked for deletion. to be called from scheduler
    """
    try:
        with transactional_session() as session:
            logger.info("Scheduler processing Accounts not accessed in the last 36 months ")
            _since_360_days = datetime.now() - timedelta(days=1095)
            _last_login_before_360_months = session.query(User).filter(and_(
                User.last_login_date != None,  # noqa
                User.last_login_date < _since_360_days
            ))
            _last_login_before_360_months.update({'mark_for_deletion': True})
            _account_created_before_360_months = session.query(User).filter(and_(
                User.last_login_date == None,  # noqa
                User.account_creation_date < _since_360_days
            ))
            _account_created_before_360_months.update({'mark_for_deletion': True})
            logger.info("Scheduler finished processing Accounts not accessed in last 36 months")

    except SQLAlchemyError:
        logger.exception("Unable to perform scheduler mark for delete operation")
        return make_response(jsonify({"title": "Scheduler operation for mark for delete users error",
                                      "detail": "Unable to perform delete operation for accounts not accessed in last "
                                                "36 months"}), 500)
    return '', 204


def auth_headers():
    return {
        'Authorization': 'Basic %s' % base64.b64encode(
            bytes(app.config['SECURITY_USER_NAME'] + ':' + app.config['SECURITY_USER_PASSWORD'],
                  "utf-8")).decode("ascii")
    }


def create_request(method, path, body, headers):
    return {"method": method,
            "path": path,
            "body": body,
            "headers": headers}


def delete_party_respondents(users):
    batch_url = f'{app.config["PARTY_URL"]}/party-api/v1/batch/requests'
    payload = []
    for user in users:
        payload.append(
            create_request("DELETE", "/party-api/v1/respondents/email", {'email': user.username},
                           auth_headers()), )

    try:
        response = requests.post(batch_url, auth=app.config['BASIC_AUTH'], data=json.dumps(payload))
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        logger.exception("Unable to send request to party service for user deletion. Can't proceed with user deletion.",
                         error=error)
        raise error

    logger.info('Successfully sent request to party service for user deletion', status_code=response.status_code,
                response_json=response.json())
