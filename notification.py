
from abc import abstractmethod, ABC
import logging
import json
from os import environ
import requests
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)

class Notification(ABC):
    @abstractmethod
    def notify(self, msg: str):
        pass

class TextNotification(Notification):
    def notify(self, msg: str):
        try:
            client = Client(environ.get('TWILIO_SID'), environ.get('TWILIO_AUTH'))
            client.messages.create(
                body= msg,
                from_=environ.get('TWILIO_FROM'),
                to=environ.get('TWILIO_TO')
            )
        except Exception as e:
            logger.error("Error occurred with Twilio: " + str(e))

class EmailNotification(Notification):
    def notify(self, msg: str):
        try:
            message = Mail(
                from_email=environ.get('SENDGRID_FROM'),
                to_emails=environ.get('SENDGRID_TO'),
                subject='NRG Balance Update',
                html_content=f'<strong>{msg}</strong>'
            )
            sg = SendGridAPIClient(environ.get('SENDGRID_API_KEY'))
            sg.send(message)
        except Exception as e:
            logger.error("Error occurred using SendGrid: " + str(e))

class AlexaNotification(Notification):
    def notify(self, msg: str):
        try:
            body = json.dumps({
                "notification": msg,
                "accessCode": environ.get('ALEXA_API_KEY')
            })
            response = requests.post(url=environ.get('ALEXA_NOTIFY_API_URL'), data=body)
            logger.info(response.text)
        except Exception as e:
            logger.error("Error occurred with Alexa notification: " + str(e))