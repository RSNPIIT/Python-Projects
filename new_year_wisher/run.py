#Importing all the Modules
import pandas as pd
import datetime as dt
import random as r
import smtplib as sm 
import os as o
import prettytable as pt
import pyperclip as cl

#Static Variables
FILE = 'peopledata.csv'
YV = '[Year]'
MY_EM = 'sample_person@gmail.com'
MY_PASS = 'hack_it_buddy'
WHAT_TO = '[Name]'
HOST_NAME = 'smtp.gmail.com'
HD_NAMES = ['First Name' ,'Last Name' , 'E-Mail']
#Reading the csv file
data = pd.read_csv(FILE)

#Extracting everything into a list
f_n = data.Name.str.split().str[0].to_list()
l_n = data.Name.str.split().str[1].to_list()
email = data.Email.to_list()

#Displaying everything in a Pretty Format
my_t = pt.PrettyTable(HD_NAMES)
for i in range(len(f_n)):
    my_t.add_row([f_n[i] , l_n[i] , email[i]])

print(f"The Table So Formed is as follows :-\n\n{my_t}\n\n")

#Extracting The Current Year
now = dt.datetime.now()
yr = str(now.year)

for i in range(1 ,5):
    LETTER_CHOICE = r.randint(1,4)
    FILEPATH = f'letter_folder/letter_{LETTER_CHOICE}.txt'

    with open(FILEPATH) as j:
        val = j.read()
        nval = val.replace(YV , yr)

        try:
            o.mkdir('my_new_dir')
        except FileExistsError:
            pass        
        with open(f'my_new_dir/letter_{i}.txt' , 'w') as k:
            k.write(nval)

#This will check whether the extraction is successfull or not        
cl.copy(nval)

#Now replacing the Name and sending the mail
for i in range(len(f_n)):
    TO_SEND_MAIL = email[i]
    vk = r.randint(1,4)

    with open(f'my_new_dir/letter_{vk}.txt') as l:
        g = l.read()
        n_l = g.replace(WHAT_TO , f_n[i])

    with sm.SMTP(HOST_NAME) as conn:
        conn.starttls()
        conn.login(user = MY_EM , password = MY_PASS)
        conn.sendmail(
            from_addr = MY_EM,
            to_addrs = TO_SEND_MAIL,
            msg = f'SUBJECT :- Happy New Year {yr}\n\n{n_l}'
        )

cl.copy(n_l)