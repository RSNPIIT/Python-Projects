import random as r
import smtplib as sm
import datetime as dt
import pandas as pd

#Static Variables
FILENAME = 'birthdays.csv'
PORT = 'smtp.gmail.com'
EMAIL = 'ramrupsatpati@gmail.com'
PAS = 'hackkarlebhai'
NUM_L = [1,2,3]
num = r.choice(NUM_L)
LETTERNAME = f'letter_templates/letter_{num}.txt'
REP = '[NAME]'

#Exctracting Today's Month and Day accd to ANSI Format
now = dt.datetime.now()
today = (now.month , now.day)
print(f"Today's Status is :\n{today}\n")

#Extracting our Values in Pandas DataFrame then Extracting them into a Dictionary of Tuples
dt = pd.read_csv(FILENAME)
print(f"The DataBase is :\n{dt}")
dates_dict = {
    (val.month, val.day): val
    for index, val in dt.iterrows()
}
print(f"Our Dictionary of Dates are :\n\n{dates_dict}\n")

#Now Check if our date matches with any b'day
if today in dates_dict:
    PERSON_NAME = dates_dict[today].name
    TO_SEND = dates_dict[today].email

    #After matching Just open the Letter and Replace the [NAME] with the Actual Person's Name
    with open(LETTERNAME) as op:
        li = op.read()
        nw = li.replace(REP , PERSON_NAME)

    print(f"\nThe Replaced Letter is :\n\n{nw}")

    #Now Just Send the Mail
    with sm.SMTP(PORT , 587) as conn:
        conn.starttls()
        conn.login(user = EMAIL , password = PAS)
        conn.sendmail(
            from_addr = EMAIL,
            to_addrs = TO_SEND,
            msg = f'SUBJECT :- Birthday Wish\n\n{nw}'
        )
else:
    print("\nNo Birthdays Today\n")