
from notification import Notification
from twilio.rest import Client

class TextNotification(Notification):
    def notify(self, twilio_sid, twilio_auth, twilio_to, twilio_from, msg):
        print("hello")
        client = Client(twilio_sid, twilio_auth)

        client.messages.create(
            body = msg,
            from_ = twilio_from,
            to = twilio_to
        )    