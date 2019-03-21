import logging

import structlog
from flask import Blueprint, make_response, request, jsonify
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from ras_rm_auth_service.basic_auth import auth
from ras_rm_auth_service.db_session_handlers import transactional_session
from ras_rm_auth_service.models.models import User

logger = structlog.wrap_logger(logging.getLogger(__name__))

account = Blueprint('account_view', __name__, url_prefix='/api/account')


@account.before_request
@auth.login_required
def before_account_view():
    pass


@account.route('/create', methods=['POST'])
def post_account():
    post_params = request.form

    try:
        username = post_params['username']
        password = post_params['password']
    except KeyError:
        logger.debug("Missing request parameter")
        return make_response(jsonify({"detail": "Missing 'username' or 'password'"}), 400)

    try:
        with transactional_session() as session:
            user = User(username=username)
            user.set_hashed_password(password)
            session.add(user)
    except IntegrityError:
        logger.exception("Unable to create account with requested username")
        return make_response(jsonify({"detail": "Unable to create account with requested username"}), 500)
    except SQLAlchemyError:
        logger.exception("Unable to commit account to database")
        return make_response(jsonify({"detail": "Unable to commit account to database"}), 500)

    return make_response(jsonify({"account": user.username, "created": "success"}), 201)


@account.route('/create', methods=['PUT'])
def put_account():
    put_params = request.form

    try:
        username = put_params['username']
    except KeyError:
        logger.debug("Missing request parameter")
        return make_response(jsonify({"detail": "Missing 'username'"}), 400)

    try:
        with transactional_session() as session:
            user = session.query(User).filter(User.username == username).first()

            if not user:
                logger.debug("User does not exist")
                return make_response(
                    jsonify({"detail": "Unauthorized user credentials. This user does not exist on the OAuth2 server"}),
                    401)

            user.update_user(put_params)
    except ValueError:
        logger.debug("Request param is an invalid type")
        return make_response(jsonify({"detail": "account_verified status is invalid"}), 400)
    except SQLAlchemyError:
        logger.exception("Unable to commit updated account to database")
        return make_response(jsonify({"detail": "Unable to commit updated account to database"}), 500)

    return make_response(jsonify({"account": user.username, "updated": "success"}), 201)
