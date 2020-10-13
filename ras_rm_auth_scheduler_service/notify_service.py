import json

import requests
from google.cloud import pubsub_v1

import config as cfg
from ras_rm_auth_scheduler_service.logger import logger


class NotifyService:
    def __init__(self):
        self.first_notification = cfg.Config.DUE_DELETION_FIRST_NOTIFICATION_TEMPLATE
        self.second_notification = cfg.Config.DUE_DELETION_SECOND_NOTIFICATION_TEMPLATE
        self.third_notification = cfg.Config.DUE_DELETION_THIRD_NOTIFICATION_TEMPLATE
        self.topic_id = cfg.Config.PUBSUB_TOPIC
        self.project_id = cfg.Config.GOOGLE_CLOUD_PROJECT
        self.publisher = None
        self.party_url = cfg.Config.PARTY_URL
        self.basic_auth = cfg.Config.BASIC_AUTH

    def _send_message(self, email, template_id, personalisation):
        """
        Send message to gov.uk notify via pubsub topic
        :param email: str email address of recipient
        :param template_id: the template id on gov.uk notify to be used
        """
        if not cfg.Config.SEND_EMAIL_TO_GOV_NOTIFY:
            logger.info("Notification not sent. Notify is disabled.")
            return

        notification = {
            'notify': {
                'email_address': email,
                'template_id': template_id,
                'personalisation': {}
            }
        }
        if personalisation:
            notification['notify']['personalisation'] = personalisation

        notification_str = json.dumps(notification)
        if self.publisher is None:
            self.publisher = pubsub_v1.PublisherClient()
        topic_path = self.publisher.topic_path(self.project_id, self.topic_id)
        logger.info('Publishing notification message to pub-sub topic', pubsub_topic=self.topic_id)
        future = self.publisher.publish(topic_path, data=notification_str.encode())
        # It's okay for us to catch a broad Exception here because the documentation for future.result() says it
        # throws either a TimeoutError or an Exception.
        try:
            msg_id = future.result()
            logger.info('Notification message published to pub-sub.', msg_id=msg_id, pubsub_topic=self.topic_id)
        except TimeoutError as e:
            logger.exception(e)
            raise NotifyError('There was a problem sending a notification via pub-sub topic to GOV.UK Notify.'
                              'Communication to pub-sub topic timed-out',
                              pubsub_topic=self.topic_id, error=e)
        except Exception as e:
            logger.exception(e)
            raise NotifyError('There was a problem sending a notification via pub-sub topic to GOV.UK Notify. '
                              'Communication to pub-sub topic raised an exception.', pubsub_topic=self.topic_id,
                              error=e)

    def request_to_notify(self, template_name, email):
        logger.info("Request to notify ", template_name=template_name)
        template_id = self._get_template_id(template_name)
        first_name = self._get_user_first_name(email)
        self._send_message(email, template_id, {'FIRST_NAME': first_name})

    def _get_template_id(self, template_name):
        templates = {'first_notification': self.first_notification,
                     'second_notification': self.second_notification,
                     'third_notification': self.third_notification, }
        if template_name in templates:
            return templates[template_name]
        else:
            raise KeyError('Template does not exist')

    def _get_user_first_name(self, email):
        type(email)
        url = f'{self.party_url}/party-api/v1/respondents/email'
        request_json = {
            'email': email
        }
        try:
            response = requests.get(url, json=request_json, auth=self.basic_auth)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            logger.exception(
                "Unable to send request to party service. Can't proceed with notification.",
                error=error)
            raise error
        return response.json()['firstName']


class NotifyError(Exception):
    def __init__(self, description=None, error=None, **kwargs):
        self.description = description
        self.error = error
        for k, v in kwargs.items():
            self.__dict__[k] = v
