import logging

import structlog
from marshmallow import ValidationError, EXCLUDE
from sqlalchemy import func
from flask import Blueprint, make_response, request, jsonify

from ras_rm_auth_service.basic_auth import auth
from ras_rm_auth_service.db_session_handlers import transactional_session
from ras_rm_auth_service.models.models import User, AccountSchema
from werkzeug.exceptions import Unauthorized

logger = structlog.wrap_logger(logging.getLogger(__name__))

tokens = Blueprint('tokens_view', __name__, url_prefix='/api/v1/tokens')

account_schema = AccountSchema(unknown=EXCLUDE)


@tokens.before_request
@auth.login_required
def before_tokens_view():
    pass


@tokens.route('/', methods=['POST'])
def post_token():
    post_params = request.form

    try:
        payload = account_schema.load(post_params)
    except ValidationError as ex:
        logger.debug("Missing request parameter", exc_info=ex)
        return make_response(jsonify({"detail": "Missing 'username' or 'password'"}), 400)

    with transactional_session() as session:
        user = session.query(User).filter(func.lower(User.username) == func.lower(payload.get('username'))).first()

        if not user:
            logger.debug("User does not exist")
            return make_response(
                jsonify({"detail": "Unauthorized user credentials. This user does not exist on the OAuth2 server"}),
                401)

        try:
            user.authorise(payload.get('password'))
        except Unauthorized as ex:
            logger.debug(ex.description, username=payload.get('username'))
            return make_response(jsonify({"detail": ex.description}), 401)

    return make_response(
        jsonify({"id": 895725, "access_token": "NotImplementedInAuthService", "expires_in": 3600,
                 "token_type": "Bearer", "scope": "", "refresh_token": "NotImplementedInAuthService"}), 201)
