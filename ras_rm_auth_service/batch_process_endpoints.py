import logging
import base64
import json

import requests
import structlog
from flask import Blueprint, make_response, jsonify
from datetime import datetime, timedelta
from sqlalchemy import and_
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError

from ras_rm_auth_service.basic_auth import auth
from ras_rm_auth_service.db_session_handlers import transactional_session
from ras_rm_auth_service.models.models import User
from ras_rm_auth_service.notify_service import NotifyService

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


@batch.route('users/third-notification', methods=['POST'])
def send_third_notifications():
    """
    sends due deletion third notification for users who's account has not been accessed for the last 35 months
    (account accessed is <= 35 months and >= 36 months) via NotifyService (pubsub)
    """
    try:
        with transactional_session() as session:
            logger.info("Scheduler processing Accounts not accessed in the last 35 months ")
            _datetime_35_months_ago = datetime.utcnow() - timedelta(days=1065)
            _datetime_36_months_ago = datetime.utcnow() - timedelta(days=1095)
            _last_login_before_35_months = session.query(User.username).filter(and_(
                User.last_login_date != None,  # noqa
                User.last_login_date <= _datetime_35_months_ago,
                User.last_login_date >= _datetime_36_months_ago.date(),
                User.due_deletion_third_notification_date == None  # noqa
            ))
            for username in _last_login_before_35_months:
                NotifyService.request_to_notify(template_name='due_deletion_third_notification_templates',
                                                email=username)
            _last_login_before_35_months.update({'due_deletion_third_notification_date': datetime.utcnow()})
            _account_created_before_35_months = session.query(User.username).filter(and_(
                User.last_login_date == None,  # noqa
                User.account_creation_date <= _datetime_35_months_ago,
                User.account_creation_date >= _datetime_36_months_ago.date(),
                User.due_deletion_third_notification_date == None  # noqa
            ))
            for username in _account_created_before_35_months:
                NotifyService.request_to_notify(template_name='due_deletion_third_notification_templates',
                                                email=username)
            _account_created_before_35_months.update({'due_deletion_third_notification_date': datetime.utcnow()})
            logger.info("Scheduler finished processing Accounts not accessed in last 35 months")

    except SQLAlchemyError:
        logger.exception("Unable to perform scheduler send due deletion third notification")
        return make_response(jsonify({"title": "Scheduler operation for due deletion third notification error",
                                      "detail": "Unable to send emails for the third due deletion notification for "
                                                "accounts not accessed in last 35 months."}), 500)
    return make_response("Success", 201)


@batch.route('users/second-notification', methods=['POST'])
def send_second_notifications():
    """
    sends due deletion second notification for users who's account has not been accessed for the last 30 months
    (account accessed is <= 30 months and >= 35 months) via NotifyService (pubsub)
    """
    try:
        with transactional_session() as session:
            logger.info("Scheduler processing Accounts not accessed in the last 30 months ")
            _datetime_35_months_ago = datetime.utcnow() - timedelta(days=1065)
            _datetime_30_months_ago = datetime.utcnow() - timedelta(days=913)
            _last_login_before_30_months = session.query(User.username).filter(and_(
                User.last_login_date != None,  # noqa
                User.last_login_date <= _datetime_30_months_ago,
                User.last_login_date >= _datetime_35_months_ago.date(),
                User.due_deletion_third_notification_date == None  # noqa
            ))
            for username in _last_login_before_30_months:
                NotifyService.request_to_notify(template_name='due_deletion_second_notification_templates',
                                                email=username)
            _last_login_before_30_months.update({'due_deletion_second_notification_date': datetime.utcnow()})
            _account_created_before_30_months = session.query(User.username).filter(and_(
                User.last_login_date == None,  # noqa
                User.account_creation_date <= _datetime_30_months_ago,
                User.account_creation_date >= _datetime_35_months_ago.date(),
                User.due_deletion_third_notification_date == None  # noqa
            ))
            for username in _account_created_before_30_months:
                NotifyService.request_to_notify(template_name='due_deletion_second_notification_templates',
                                                email=username)
            _account_created_before_30_months.update({'due_deletion_second_notification_date': datetime.utcnow()})
            logger.info("Scheduler finished processing Accounts not accessed in last 30 months")

    except SQLAlchemyError:
        logger.exception("Unable to perform scheduler send due deletion second notification")
        return make_response(jsonify({"title": "Scheduler operation for due deletion second notification error",
                                      "detail": "Unable to send emails for the second due deletion notification for "
                                                "accounts not accessed in last 30 months."}), 500)
    return make_response("Success", 201)


@batch.route('users/first-notification', methods=['POST'])
def send_first_notifications():
    """
    sends due deletion second notification for users who's account has not been accessed for the last 24 months
    (account accessed is <= 24 months and >= 30 months) via NotifyService (pubsub)
    """
    try:
        with transactional_session() as session:
            logger.info("Scheduler processing Accounts not accessed in the last 24 months ")
            _datetime_24_months_ago = datetime.utcnow() - timedelta(days=730)
            _datetime_30_months_ago = datetime.utcnow() - timedelta(days=913)
            _last_login_before_24_months = session.query(User.username).filter(and_(
                User.last_login_date != None,  # noqa
                User.last_login_date <= _datetime_24_months_ago,
                User.last_login_date >= _datetime_30_months_ago.date(),
                User.due_deletion_third_notification_date == None  # noqa
            ))
            for username in _last_login_before_24_months:
                NotifyService.request_to_notify(template_name='due_deletion_first_notification_templates',
                                                email=username)
            _last_login_before_24_months.update({'due_deletion_first_notification_date': datetime.utcnow()})
            _account_created_before_24_months = session.query(User.username).filter(and_(
                User.last_login_date == None,  # noqa
                User.account_creation_date <= _datetime_24_months_ago,
                User.account_creation_date >= _datetime_30_months_ago.date(),
                User.due_deletion_third_notification_date == None  # noqa
            ))
            for username in _account_created_before_24_months:
                NotifyService.request_to_notify(template_name='due_deletion_first_notification_templates',
                                                email=username)
            _account_created_before_24_months.update({'due_deletion_first_notification_date': datetime.utcnow()})
            logger.info("Scheduler finished processing Accounts not accessed in last 24 months")

    except SQLAlchemyError:
        logger.exception("Unable to perform scheduler send due deletion first notification")
        return make_response(jsonify({"title": "Scheduler operation for due deletion first notification error",
                                      "detail": "Unable to send emails for the first due deletion notification for "
                                                "accounts not accessed in last 24 months."}), 500)
    return make_response("Success", 201)


@batch.route('users/mark-for-deletion', methods=['DELETE'])
def mark_for_deletion_accounts():
    """
    Marks user accounts for deletion which has not been accessed in the last 36 months.
    To be called from scheduler
    """
    try:
        with transactional_session() as session:
            logger.info("Scheduler processing Accounts not accessed in the last 36 months ")
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
