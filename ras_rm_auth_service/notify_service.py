import json
import logging
import structlog
from flask import current_app as app
from google.cloud import pubsub_v1

logger = structlog.wrap_logger(logging.getLogger(__name__))


class NotifyService:
    def __init__(self):
        self.due_deletion_first_notification_templates = app.config['DUE_DELETION_FIRST_NOTIFICATION_TEMPLATE']
        self.due_deletion_second_notification_templates = app.config['DUE_DELETION_SECOND_NOTIFICATION_TEMPLATE']
        self.due_deletion_third_notification_templates = app.config['DUE_DELETION_THIRD_NOTIFICATION_TEMPLATE']
        self.topic_id = app.config['PUBSUB_TOPIC']
        self.project_id = app.config['GOOGLE_CLOUD_PROJECT']
        self.publisher = None

    def _send_message(self, email, template_id):
        """
        Send message to gov.uk notify via pubsub topic
        :param email: str email address of recipient
        :param template_id: the template id on gov.uk notify to be used
        """
        if not app.config['SEND_EMAIL_TO_GOV_NOTIFY']:
            logger.info("Notification not sent. Notify is disabled.")
            return

        notification = {
            'notify': {
                'email_address': email,
                'template_id': template_id
            }
        }
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
            raise NotifyError('There was a problem sending a notification via pub-sub topic to GOV.UK Notify.'
                              'Communication to pub-sub topic timed-out',
                              pubsub_topic=self.topic_id, error=e)
        except Exception as e:
            raise NotifyError('There was a problem sending a notification via pub-sub topic to GOV.UK Notify. '
                              'Communication to pub-sub topic raised an exception.', pubsub_topic=self.topic_id,
                              error=e)

    def request_to_notify(self, template_name, email):
        logger.info("Request to notify ", email=email, template_name=template_name)
        template_id = self._get_template_id(template_name)
        self._send_message(email, template_id)

    def _get_template_id(self, template_name):
        templates = {'due_deletion_first_notification_templates': self.due_deletion_first_notification_templates,
                     'due_deletion_second_notification_templates': self.due_deletion_second_notification_templates,
                     'due_deletion_third_notification_templates': self.due_deletion_third_notification_templates, }
        if template_name in templates:
            return templates[template_name]
        else:
            raise KeyError('Template does not exist')


class NotifyError(Exception):
    def __init__(self, description=None, error=None, **kwargs):
        self.description = description
        self.error = error
        for k, v in kwargs.items():
            self.__dict__[k] = v
