import logging

import structlog
from flask import Blueprint, jsonify, make_response, request
from marshmallow import EXCLUDE, ValidationError
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import Unauthorized

from ras_rm_auth_service.basic_auth import auth
from ras_rm_auth_service.db_session_handlers import transactional_session
from ras_rm_auth_service.models.models import AccountSchema, User

logger = structlog.wrap_logger(logging.getLogger(__name__))

tokens = Blueprint("tokens_view", __name__, url_prefix="/api/v1/tokens")

account_schema = AccountSchema(unknown=EXCLUDE)

AUTH_TOKEN_ERROR = "Auth service tokens error"


@tokens.before_request
@auth.login_required
def before_tokens_view():
    pass


@tokens.route("/", methods=["POST"])
def post_token():
    """This endpoint looks weird because it has a history with the previous authentication service.
    The previous one had a /tokens endpoint to provide oauth tokens for users who provided correct credentials.
    In the changeover from the old auth service to this one, to make the changeover less risky, we kept this endpoint
    with the same name, but instead of it returning a json payload with tokens, we decided a 204 would suffice as
    the HTTP equivalent of a thumbs up that the credentials were correct.

    Once the old service has been retired, this endpoint and this services API as a whole needs to be reviewed
    and cleaned up.
    """
    post_params = request.form

    try:
        payload = account_schema.load(post_params)
    except ValidationError as ex:
        logger.info("Missing request parameter", exc_info=ex)
        return make_response(jsonify({"title": AUTH_TOKEN_ERROR, "detail": "Missing 'username' or 'password'"}), 400)

    bound_logger = logger.bind(obfuscated_username=obfuscate_email(payload.get("username")))

    try:
        with transactional_session() as session:
            bound_logger.info("Searching for user")
            user = session.query(User).filter(func.lower(User.username) == func.lower(payload.get("username"))).first()

            if not user:
                bound_logger.info("User does not exist")
                return make_response(
                    jsonify(
                        {
                            "title": AUTH_TOKEN_ERROR,
                            "detail": "Unauthorized user credentials. This user does not exist on the Auth server",
                        }
                    ),
                    401,
                )

            bound_logger.info("User found")
            try:
                user.authorise(payload.get("password"))
            except Unauthorized as ex:
                bound_logger.info("User is unauthorised", description=ex.description)
                return make_response(jsonify({"title": AUTH_TOKEN_ERROR, "detail": ex.description}), 401)

            logger.info("User credentials correct")
            return make_response("", 204)
    except SQLAlchemyError as e:
        logger.info(f"{e.__class__.__name__} occurred when committing to database", code=e.code)
        return make_response(jsonify({"title": AUTH_TOKEN_ERROR, "detail": e.__class__.__name__}), 500)


def obfuscate_email(email):
    """Takes an email address and returns an obfuscated version of it.
    For example: test@example.com would turn into t**t@e*********m
    """
    if email is None:
        return None
    splitmail = email.split("@")
    # If the prefix is 1 character, then we can't obfuscate it
    if len(splitmail[0]) <= 1:
        prefix = splitmail[0]
    else:
        prefix = f'{splitmail[0][0]}{"*"*(len(splitmail[0])-2)}{splitmail[0][-1]}'
    # If the domain is missing or 1 character, then we can't obfuscate it
    if len(splitmail) <= 1 or len(splitmail[1]) <= 1:
        return f"{prefix}"
    else:
        domain = f'{splitmail[1][0]}{"*"*(len(splitmail[1])-2)}{splitmail[1][-1]}'
        return f"{prefix}@{domain}"
