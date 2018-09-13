import logging

import structlog
from flask import Blueprint, make_response, request, jsonify

from ras_rm_auth_service.basic_auth import auth
from ras_rm_auth_service.db_session_handlers import non_transactional_session, transactional_session
from ras_rm_auth_service.models.models import User

logger = structlog.wrap_logger(logging.getLogger(__name__))

tokens = Blueprint('tokens_view', __name__, url_prefix='/api/v1/tokens')


@tokens.before_request
@auth.login_required
def before_tokens_view():
    pass


@tokens.route('/', methods=['POST'])
def post_token():
    post_params = request.form

    try:
        username = post_params['username']
        password = post_params['password']
    except KeyError:
        logger.debug("Missing request parameter 'username' or 'password'")
        return make_response(jsonify({"detail": "Missing 'username' or 'password'"}), 400)

    with non_transactional_session() as session:
        user = session.query(User).filter(User.username == username).first()

    if not user:
        logger.debug("User does not exist")
        return make_response(
            jsonify({"detail": "Unauthorized user credentials. This user does not exist on the OAuth2 server"}), 401)

    if not user.is_correct_password(password):

        with transactional_session() as session:
            user.failed_login()
            session.add(user)

        if user.account_locked:
            return make_response(jsonify({"detail": "User account locked"}), 401)

        return make_response(jsonify({"detail": "Unauthorized user credentials"}), 401)

    if user.account_locked:
        return make_response(jsonify({"detail": "User account locked"}), 401)

    if not user.account_verified:
        return make_response(jsonify({"detail": "User account not verified"}), 401)

    return make_response(
        jsonify({"id": 895725, "access_token": "NotImplementedInAuthService", "expires_in": 3600,
                 "token_type": "Bearer", "scope": "", "refresh_token": "NotImplementedInAuthService"}), 201)
