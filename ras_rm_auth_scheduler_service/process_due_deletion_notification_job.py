import base64
from datetime import UTC, datetime

import requests

import config as cfg
from ras_rm_auth_scheduler_service.logger import logger
from ras_rm_auth_scheduler_service.notify_service import NotifyService
from ras_rm_auth_service.resources.tokens import obfuscate_email


class ProcessNotificationJob:
    def __init__(self):
        auth_url = cfg.Config.AUTH_URL
        self.first_notification_url = f"{auth_url}/api/batch/account/users/eligible-for-first-notification"
        self.second_notification_url = f"{auth_url}/api/batch/account/users/eligible-for-second-notification"
        self.third_notification_url = f"{auth_url}/api/batch/account/users/eligible-for-third-notification"
        self.patch_url = f"{auth_url}/api/account/user"
        auth = "{}:{}".format(cfg.Config.SECURITY_USER_NAME, cfg.Config.SECURITY_USER_PASSWORD).encode("utf-8")
        self.headers = {"Authorization": "Basic %s" % base64.b64encode(bytes(auth)).decode("ascii")}

    def process_first_notification(self):
        users = self._get_eligible_users(self.first_notification_url)
        if users:
            self._process_notification(users, "first_notification")
        else:
            logger.info("No user eligible for first notification")

    def process_second_notification(self):
        users = self._get_eligible_users(self.second_notification_url)
        if users:
            self._process_notification(users, "second_notification")
        else:
            logger.info("No user eligible for second notification")

    def process_third_notification(self):
        users = self._get_eligible_users(self.third_notification_url)
        if users:
            self._process_notification(users, "third_notification")
        else:
            logger.info("No user eligible for third notification")

    def _process_notification(self, users, scheduler):
        for username in users:
            logger.info(f"Sending due deletion {scheduler} to user", username=obfuscate_email(username))
            NotifyService().request_to_notify(template_name=scheduler, email=username)
            logger.info(f"Due deletion {scheduler} sent to user", username=obfuscate_email(username))
            self._update_user(username, scheduler)

    def _update_user(self, user, scheduler_column):
        logger.info("Updating user data with notification sent date", notification=scheduler_column)
        form_data = {scheduler_column: datetime.now(UTC)}
        try:
            requests.patch(f"{self.patch_url}/{user}", data=form_data, headers=self.headers)
        except requests.exceptions.HTTPError as error:
            logger.exception("Unable to update user notification date", username=obfuscate_email(user), error=error)
            raise error
        logger.info("user data with notification sent date updated", notification=scheduler_column)

    def _get_eligible_users(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            return response.json()
        except requests.exceptions.HTTPError as error:
            logger.exception("Unable to communicate to auth service to fetch eligible users", error=error)
            raise error
