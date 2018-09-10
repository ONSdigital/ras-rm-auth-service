import logging
from distutils.util import strtobool

import structlog
from flask import Blueprint, make_response, request, jsonify
from passlib.hash import bcrypt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from ras_rm_auth_service.db_session_handlers import transactional_session
from ras_rm_auth_service.models.models import User

logger = structlog.wrap_logger(logging.getLogger(__name__))

account = Blueprint('account_view', __name__, url_prefix='/api/account')


@account.route('/create', methods=['POST'])
def post_account():
    post_params = request.form

    try:
        user = User(username=post_params['username'])
        user.hash = bcrypt.using(rounds=12).hash(post_params['password'])
    except KeyError as e:
        logger.debug("Missing request parameter", exception=e)
        return make_response(jsonify({"detail": "Missing 'username' or 'password'"}), 400)

    try:
        with transactional_session() as session:
            session.add(user)
    except IntegrityError as e:
        return make_response(jsonify({"detail": "Unable to create account with requested username"}), 409)
    except SQLAlchemyError as e:
        return make_response(jsonify({"detail": "Unable to commit account to database"}), 500)

    return make_response(jsonify({"account": user.username, "created": "success"}), 201)


@account.route('/create', methods=['PUT'])
def put_account():
    put_params = request.form

    try:
        with transactional_session() as session:
            user = session.query(User).filter(User.username == put_params.get('username', "")).first()

            if not user:
                return make_response(
                    jsonify({"detail": "Unauthorized user credentials. This user does not exist on the OAuth2 server"}),
                    401)

            user.is_verified = strtobool(put_params.get('account_verified'))
    except ValueError as e:
        return make_response(jsonify({"detail": "account_verified status is invalid"}), 400)
    except SQLAlchemyError as e:
        return make_response(jsonify({"detail": "Unable to commit updated account to database"}), 500)

    return make_response(jsonify({"account": user.username, "updated": "success"}), 201)
