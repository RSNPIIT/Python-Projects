import requests as rq
import os as o
from twilio.rest import Client

my_api_key = o.getenv('OPENWEATHER_API_KEY')
account_sid = "ACCOUNT_INFO"
auth_token = "ACCNT_AUTH_TOKEN"

if not my_api_key:
    raise RuntimeError("OPENWEATHER_API_KEY Not Set")

paras = {
    'lat' : 22.79,
    'lon' : 86.20,
    'cnt' : 4,
    'appid' : my_api_key
}
URL = 'https://api.openweathermap.org/data/2.5/forecast'

#This will get the required response --- (Open Weather Data Org)
res = rq.get(url = URL , params = paras)

is_rain = False
if res.status_code == 200:
    print("\nSuccessful API Extraction\n")
    val = res.json()
    
    for x in val['list']:
        id_val = x['weather'][0]['id']
        id_val = int(id_val)
        if id_val < 700:
            is_rain = True
            break
        else:
            continue

else:
    print("\nExtraction Failed\n")
    res.raise_for_status()

if is_rain:
    client = Client(account_sid , auth_token)
    message = client.messages.create(
            body = "It's Going to Rain Today Remember to Bring an Umbrella (☂️)",
            from_ = "FROM_NUMBER",
            to = "TO_NUMBER"
        )
    print("\nmessage.status")
else:
    client = Client(account_sid , auth_token)
    message = client.messages.create(
            body = "It's Going to be Sunny today Remember to Bring a Sunscreen (🧴)",
            from_ = "FROM_NUMBER",
            to = "TO_NUMBER"
        )
    print("message.status")
