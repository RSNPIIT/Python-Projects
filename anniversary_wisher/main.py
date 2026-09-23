import datetime as dt
import pandas as pd
import random as r
import smtplib as sm

#Static Values
FILE = 'tosend.csv'
LIS = [1,2,3]
r_n = r.choice(LIS)
FILEPATH = f'letter_templates/letter_{r_n}.txt'
TEXT = '[Name]'
HOST = 'smtp.gmail.com'
EMAIL = 'sampleuser@gmail.com'
PAS = 'hackkarlebhai'

#Getting the Current Month and Day
now = dt.datetime.now()
cr = (now.month , now.day)
print(f'The Current Month and Day is :- \n{cr}\n')

#Pulled the data from the csv and arranging them in a Simple Format
data = pd.read_csv(FILE)
print(f'The Pulled Data is :-\n{data}\n')

g_d = {(val.month , val.day) : val for index , val in data.iterrows()}
print(f"Our Extracted Data is :\n{g_d}\n")

#Now Check if today is the anniversary date
if cr in g_d:
    print("Yaey Today is Anniversary\n")

    #Other Static Values
    TO_SEND_MAIL = g_d[cr].email
    NAME = g_d[cr].name

    #Opening and Replacing the [Name] with a real name
    with open(FILEPATH) as fp:
        cur = fp.read()
        n_v = cur.replace(TEXT , NAME)
    
    print(f"The New Templating Value so formed is : \n{n_v}\n")

    #Now we send the email to the person
    with sm.SMTP(HOST , 587) as conn:
        conn.starttls()
        conn.login(user = EMAIL , password = PAS)
        conn.sendmail(
            from_addr = EMAIL,
            to_addrs = TO_SEND_MAIL,
            msg = f'Subject :- Happy Anniversary Buddy\n\n{n_v}\n'
        )
else:
    print("No Anniversaries as of today\nPlease Try again later\n")