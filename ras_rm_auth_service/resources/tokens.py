import logging

import structlog
from sqlalchemy import func
from flask import Blueprint, make_response, request, jsonify

from ras_rm_auth_service.basic_auth import auth
from ras_rm_auth_service.db_session_handlers import transactional_session
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

    with transactional_session() as session:
        user = session.query(User).filter(func.lower(User.username) == func.lower(username)).first()

        if not user:
            logger.debug("User does not exist")
            return make_response(
                jsonify({"detail": "Unauthorized user credentials. This user does not exist on the OAuth2 server"}),
                401)

        successfully_authorised, error_message = user.authorise(password)

        if not successfully_authorised:
            return make_response(jsonify({"detail": error_message}), 401)

    return make_response(
        jsonify({"id": 895725, "access_token": "NotImplementedInAuthService", "expires_in": 3600,
                 "token_type": "Bearer", "scope": "", "refresh_token": "NotImplementedInAuthService"}), 201)
