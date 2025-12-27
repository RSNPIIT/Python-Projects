import requests as rq
import datetime as dt
import smtplib as sm
import time as ti
import random as r

#Static Variables
MY_LAT = 22.804565
MY_LONG = 86.202873
URL = 'http://api.open-notify.org/iss-now.json'
URL1 = 'https://api.sunrise-sunset.org/json'
HOST = 'smtp.gmail.com'
EMAIL = 'sample@gmail.com'
PAS = 'hackkarlebhai'
FILE = 'mess.txt'
parameters = {
    "lat": MY_LAT,
    "lng": MY_LONG,
    "formatted": 0,
}
NAMES = ['Arjun','Mikhail','Yuri']
o_n = r.choice(NAMES)
REP = '[Name]'
TO_SEND_MAIL = f'{o_n.lower()}@gmail.com'

#Fetching Values from the Sunrise and Sunset Api as per Jamshedpur's Location
response = rq.get(URL1 , params=parameters)
response.raise_for_status()
data = response.json()
sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

#Replace the Message File With a name in the List and then Send them the Email
while True:
    #Fetching Values From the ISS Api
    res = rq.get(url= URL)
    res.raise_for_status()
    data = res.json()

    iss_lat = float(data["iss_position"]["latitude"])
    iss_long = float(data["iss_position"]["longitude"])

    ti.sleep(60)  #So that this will test every one minute

    time_now = dt.datetime.now().hour

    is_dark = time_now >= sunset or time_now <= sunrise
    is_close = abs(MY_LAT - iss_lat) < 5 and abs(MY_LONG - iss_long) <= 5

    if is_dark and is_close:
        with open(FILE) as f:
            val = f.read()
            nu = val.replace(REP , o_n)
        #Preview of the Message
        print(f'The Message is :\n\n{nu}')

        #Sending the Mail
        with sm.SMTP(HOST) as conn:
            conn.starttls()
            conn.login(user = EMAIL , password = PAS)
            conn.sendmail(
                from_addr = EMAIL,
                to_addrs = TO_SEND_MAIL,
                msg = f'Subject : ISS Overhead\n\n{nu}'
            )
        break #We break so as to prevent spam
    
    else:
        continue