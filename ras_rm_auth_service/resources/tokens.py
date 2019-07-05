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
    """This endpoint looks weird because it has a history with the previous authentication service.
    The previous one had a /tokens endpoint to provide oauth tokens for users who provided correct credentials.
    In the changeover from the old auth service to this one, to make the changeover less risky, we kept this endpoint
    with the same name, but instead of it returning a json payload with tokens, we decided a 204 would suffice as
    the HTTP equivalent of a thumbs up that the credentials were correct.

    Once the old service has been retired, this endpoint and this services API as a whole needs to be reviewed and cleaned
    up.
    """
    logger.info("Verifying user credentials")
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

    logger.info("User credentials correct")
    return make_response('', 204)
