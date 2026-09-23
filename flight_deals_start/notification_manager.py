import os as o
from twilio.rest import Client

TW_PHN_NO = o.getenv("TWILIO_PHONE_NUMBER")
MY_PHN_NO = o.getenv("MY_PHONE_NUMBER")
ACCD_SID = o.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = o.getenv("TWILIO_AUTH_TOKEN")

class NotificationManager:
    def __init__(self):
        self.phn_no = TW_PHN_NO
        self.to_no = MY_PHN_NO
        self.client = Client(ACCD_SID , AUTH_TOKEN)

    def send_mess(self , destin , price_act , given_pr):
        mes = self.client.messages.create(
            body = f'LOW PRICE ALERT !!!! \nFrom LON_UK to {destin}\nPrice Down From {given_pr} to {price_act} .\nRECOMMENDED FAST and Immediate Booking as this is a Limited period offer\n',
            from_ = self.phn_no,
            to = self.to_no
        )