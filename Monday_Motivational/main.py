import datetime as dt
import random
import smtplib as sm

#Static Constants
MY_EMAIL = 'theghoul@gmail.com'
TO_SEND_MAIL = 'sample_user@gmail.com'
PASSWD = 'hackkarlebhai'
FILENAME = 'quotes.txt'

#Gettin the Current date
now = dt.datetime.now()

#Doing Things As Per the Day
week_day = now.weekday()
if week_day == 0:
    with open(FILENAME) as j:
        lis = j.readlines()
        qtes = random.choice(lis)
    
    print(f"The Said Quote is : \n{qtes}")
    with sm.SMTP('smtp.gmail.com') as conn:
        conn.starttls()
        conn.login(user = MY_EMAIL , password = PASSWD)
        conn.sendmail(
            from_addr = MY_EMAIL,
            to_addrs = TO_SEND_MAIL,
            msg = f'\nSubject :- Monday Motivation\n\n{qtes}'
        )
