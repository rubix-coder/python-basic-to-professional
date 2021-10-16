from twilio.rest import Client

TWILIO_SID = "ACf507be8ced0d1e71b68f1f48f4cbfa45"
TWILIO_AUTH_TOKEN = "67d66e080fa43dbe7318d9a27b0cf19b"
TWILIO_VIRTUAL_NUMBER = "+918140253130"
TWILIO_VERIFIED_NUMBER = "+919624622239"


class NotificationManager:

    def __init__(self):
        self.client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    def send_sms(self, message):
        message = self.client.messages.create(
            body=message,
            from_=TWILIO_VIRTUAL_NUMBER,
            to=TWILIO_VERIFIED_NUMBER,
        )
        # Prints if successfully sent.
        print(message.sid)
