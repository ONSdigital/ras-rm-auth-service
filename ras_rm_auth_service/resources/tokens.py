import logging

import structlog
from flask import Blueprint, make_response, request, jsonify
from passlib.hash import bcrypt

from ras_rm_auth_service.basic_auth import auth
from ras_rm_auth_service.db_session_handlers import non_transactional_session
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
    except KeyError as e:
        logger.debug("Missing request parameter", exception=e)
        return make_response(jsonify({"detail": "Missing 'username' or 'password'"}), 400)

    with non_transactional_session() as session:
        user = session.query(User).filter(User.username == username).first()

    if not user:
        logger.debug("User does not exist")
        return make_response(
            jsonify({"detail": "Unauthorized user credentials. This user does not exist on the OAuth2 server"}), 401)

    if not bcrypt.verify(password, user.hash):
        return make_response(jsonify({"detail": "Unauthorized user credentials"}), 401)

    if not user.is_verified:
        return make_response(jsonify({"detail": "User account not verified"}), 401)

    return make_response(
        jsonify({"id": 895725, "access_token": "fakefake-4bc1-4254-b43a-f44791ecec75", "expires_in": 3600,
                 "token_type": "Bearer", "scope": "", "refresh_token": "fakefake-2151-4b11-b0d5-a9a68f2c53de"}), 201)
