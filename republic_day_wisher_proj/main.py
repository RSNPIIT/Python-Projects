#Import The Required Modules
import pandas as pd
import random as r
import datetime as dt
import prettytable as pt
import pyperclip as pl
import os as o
import time as ti
import smtplib as sm
from twilio.rest import Client

#Static Variables
FILE = 'people_data.csv'
TI = 1
TEMP = '[Name]'
SERV = 'smtp.gmail.com'
PORT = 587

#Environment variables
TW_PHN_NO = o.getenv("TWILIO_PHONE_NUMBER")
ACCD_SID = o.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = o.getenv("TWILIO_AUTH_TOKEN")
EMAIL = o.getenv("EMAIL")
PAS = o.getenv("EMAIL_PASSWORD")

# Checking For Whether the PHN Number and Keys Exists or Not
if not TW_PHN_NO or not ACCD_SID or not AUTH_TOKEN or not EMAIL or not PAS:
    print("Environment Variables Not Set")
    exit()

#Extracting the Data From CSV
val = pd.read_csv(FILE)
ti.sleep(TI)
print(f"Extracted Data Successfully\n(A Sneak Peek it's) :-> \n\n{val}")
print('\n')

name_split = val['Name'].str.split()
fname_list = name_split.str[0].tolist()
lname_list = name_split.str[1].fillna('').tolist()
cnt_numli = val['Contact_Number'].tolist()
email_li = val['Email'].tolist()
city_li = val['City'].tolist()
role_li = val['Role'].tolist()

REG_LIM = len(fname_list)

#Using PrettyTable to make it prettier
print("A More Visually Appealing Output is :->\n\n")
tab = pt.PrettyTable()
tab.field_names = ['F.Name', 'L.Name', 'Contact Number', 'Email', 'City', 'Role']

for i in range(REG_LIM):
    tab.add_row([fname_list[i], lname_list[i] , cnt_numli[i], email_li[i], city_li[i], role_li[i]])

print(tab)

#Extracting the letter from the template 
for i in range(REG_LIM):
    chc = r.randint(1,3)
    some_name = f'templates/letter_{chc}.txt'
    with open(some_name) as fl:
        j = fl.read()
        v = j.replace(TEMP , fname_list[i])
    
    o.makedirs("template", exist_ok=True)
    a_new_path = f'template/letter_to_{fname_list[i]}.txt'

    with open(a_new_path ,'w') as k:
        k.write(v)

pl.copy(v)
print("It's Done\nYeah")
ti.sleep(1)

#Calculating the Current Date_Time from the Module
now = dt.datetime.now()
mn = now.month
dy = now.day
se = (dy , mn)
print(f"The Current Month is {mn} and Current Day is {dy}")

#Sending all of em the Message and Email Cause People Like Both

if se == (26 , 1):
    print("\nIt's Republic Day")
    cli = Client(ACCD_SID , AUTH_TOKEN)


    with sm.SMTP(SERV , PORT) as conn:
        conn.starttls()
        conn.login(user = EMAIL , password = PAS)

        for i in range(REG_LIM):
            path = f'template/letter_to_{fname_list[i]}.txt'

            with open(path) as pt:
                rx = pt.read()

            #Sending the Messages From the Set Phone Number
            mess = cli.messages.create(
                body = rx,
                from_ = TW_PHN_NO,
                to = cnt_numli[i] 
            )
            print(f"The Status of the Sent Message is : {mess.status}")

            ti.sleep(1)
            conn.sendmail(
                from_addr = EMAIL,
                to_addrs = email_li[i],
                msg = f'Subject :- Happy Republic Day \n{rx}'
            )
else:
    print("\nApologies Comrade\nToday's not Republic Day")
    ti.sleep(1)