import logging
import base64
import json
from itertools import chain

import requests
import structlog
from flask import Blueprint, make_response, jsonify
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from ras_rm_auth_service.basic_auth import auth
from ras_rm_auth_service.db_session_handlers import transactional_session
from ras_rm_auth_service.models.models import User

logger = structlog.wrap_logger(logging.getLogger(__name__))

batch = Blueprint('batch_process', __name__, url_prefix='/api/batch/account')


@batch.before_request
@auth.login_required
def before_account_view():
    pass


@batch.route('/users', methods=['DELETE'])
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


@batch.route('users/eligible-for-first-notification', methods=['GET'])
def get_users_eligible_for_first_notification():
    _datetime_24_months_ago = datetime.utcnow() - timedelta(days=730)
    _datetime_30_months_ago = datetime.utcnow() - timedelta(days=913)
    try:
        with transactional_session() as session:
            logger.info("Getting users eligible for fist due deletion notification")
            users_eligible_for_first_notification = session.query(User.username).filter(or_(and_(
                User.last_login_date != None,  # noqa
                User.last_login_date.between(_datetime_30_months_ago, _datetime_24_months_ago),
                User.first_notification == None  # noqa
            ), and_(
                User.last_login_date == None,  # noqa
                User.account_creation_date.between(_datetime_30_months_ago, _datetime_24_months_ago),
                User.first_notification == None  # noqa
            )))
            logger.info("Found users eligible for first due deletion notification")
            return jsonify([x for x in chain.from_iterable(users_eligible_for_first_notification)
                            if isinstance(x, str)])
    except NoResultFound:
        logger.info("No existing user eligible for first due deletion notification")
        return {}, 404


@batch.route('users/eligible-for-second-notification', methods=['GET'])
def get_users_eligible_for_second_notification():
    _datetime_30_months_ago = datetime.utcnow() - timedelta(days=913)
    _datetime_35_months_ago = datetime.utcnow() - timedelta(days=1065)
    try:
        with transactional_session() as session:
            logger.info("Getting users eligible for second due deletion notification")
            users_eligible_for_second_notification = session.query(User.username).filter(or_(and_(
                User.last_login_date != None,  # noqa
                User.last_login_date.between(_datetime_35_months_ago, _datetime_30_months_ago),
                User.second_notification == None  # noqa
            ), and_(
                User.last_login_date == None,  # noqa
                User.account_creation_date.between(_datetime_35_months_ago, _datetime_30_months_ago),
                User.second_notification == None  # noqa
            )))
            logger.info("Found users eligible for second due deletion notification")
            return jsonify([x for x in chain.from_iterable(users_eligible_for_second_notification)
                            if isinstance(x, str)])
    except NoResultFound:
        logger.info("No existing user eligible for second due deletion notification")
        return {}, 404


@batch.route('users/eligible-for-third-notification', methods=['GET'])
def get_users_eligible_for_third_notification():
    _datetime_35_months_ago = datetime.utcnow() - timedelta(days=1065)
    _datetime_36_months_ago = datetime.utcnow() - timedelta(days=1095)
    try:
        with transactional_session() as session:
            logger.info("Getting users eligible for third due deletion notification")
            users_eligible_for_second_notification = session.query(User.username).filter(or_(and_(
                User.last_login_date != None,  # noqa
                User.last_login_date.between(_datetime_36_months_ago, _datetime_35_months_ago),
                User.third_notification == None # noqa
            ), and_(
                User.last_login_date == None,  # noqa
                User.account_creation_date.between(_datetime_36_months_ago, _datetime_35_months_ago),
                User.third_notification == None  # noqa
            )))
            logger.info("Found users eligible for third due deletion notification")
            return jsonify([x for x in chain.from_iterable(users_eligible_for_second_notification)
                            if isinstance(x, str)])
    except NoResultFound:
        logger.info("No existing user eligible for third due deletion notification")
        return {}, 404


@batch.route('users/mark-for-deletion', methods=['DELETE'])
def mark_for_deletion_accounts():
    """
    Marks user accounts for deletion which has not been accessed in the last 36 months.
    To be called from scheduler
    """
    try:
        with transactional_session() as session:
            logger.info("Scheduler processing Accounts not accessed in the last 36 months ")
            # process to mark account ready for deletion for
            # accounts not accessed in the last 36 months
            _since_36_months = datetime.utcnow() - timedelta(days=1095)
            _last_login_before_36_months = session.query(User).filter(and_(
                User.last_login_date != None,  # noqa
                User.last_login_date < _since_36_months
            ))
            _last_login_before_36_months.update({'mark_for_deletion': True})
            _account_created_before_36_months = session.query(User).filter(and_(
                User.last_login_date == None,  # noqa
                User.account_creation_date < _since_36_months
            ))
            _account_created_before_36_months.update({'mark_for_deletion': True})
            logger.info("Scheduler finished processing Accounts not accessed in last 36 months")
            # process to mark account ready for deletion for
            # accounts not been activated in the last 80 hrs.
            logger.info("Scheduler processing Account not activated for more than 80 hrs")
            _since_80_hrs = datetime.utcnow() - timedelta(hours=80)
            _account_not_activated_80_hrs = session.query(User).filter(and_(
                User.account_verified == False,  # noqa
                User.account_creation_date < _since_80_hrs
            ))
            _account_not_activated_80_hrs.update({'mark_for_deletion': True})
            logger.info("Scheduler finished* processing Account not activated for more than 80 hrs")
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
