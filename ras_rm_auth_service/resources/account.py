import logging
import structlog
from ras_rm_auth_service.resources.tokens import obfuscate_email
from flask import Blueprint, make_response, request, jsonify
from marshmallow import ValidationError, EXCLUDE
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from ras_rm_auth_service.basic_auth import auth
from ras_rm_auth_service.db_session_handlers import transactional_session
from ras_rm_auth_service.models.models import User, AccountSchema

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

    params = request.form

    try:
        username = params['username']

    except KeyError:
        logger.exception("Missing request parameter")
        return make_response(jsonify({"title": "Auth service delete user error",
                                      "detail": "Missing 'username'"}), 400)

    logger.info("Start deleting  User  :", email_id=obfuscate_email(username))

    try:
        with transactional_session() as session:
            user = session.query(User).filter(User.username == username).first()

            if not user:
                logger.info("User does not exist")
                return make_response(
                    jsonify({"title": "Auth service delete  user error",
                             "detail": "This user does not exist on the Auth server"}), 404)

            session.query(User).filter(User.username == username).delete()

    except ValueError:
        logger.exception("Request param is an invalid type")
        return make_response(jsonify({"title": "Auth service delete  user error",
                                     "detail": "Request param is an invalid type"}), 400)
    except SQLAlchemyError:
        logger.exception("Unable to commit delete operation")
        return make_response(jsonify({"title": "Auth service  delete user error",
                                      "detail": "Unable to commit delete  operation"}), 500)

    logger.info("Successfully deleted user ", email_id=obfuscate_email(username))
    return '', 204
