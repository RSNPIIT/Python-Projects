import smtplib as sm
import os as o
import requests as rq
import time as ti
from bs4 import BeautifulSoup as bs

#Static and Secret Variables
URL = 'https://appbrewery.github.io/instant_pot/'
PARS = 'html.parser'
FILENAME = 'site.html'
MY_EM = o.getenv("MY_EMAIL")
TO_SEND_EM = o.getenv("TO_SEND_EMAIL")
PAS = o.getenv("EMAIL_PASSWORD")
HOST = 'smtp.gmail.com'
HDR = {"Accept-Language": "en-IN"}

#Safety Net for Unavailable Env. var
if not all([MY_EM, TO_SEND_EM, PAS]):
    raise EnvironmentError("One or more environment variables not set.")

try:
    TARG_PR = abs(int(input("Enter Your Expected Price for the Item (in $):- ")))
except ValueError as v:
    print("The Value Given is Wrong\nNon Decimal Values Encountered\n")
    exit()
except (KeyboardInterrupt , EOFError) as erk:
    print("Exitting ....\nPlease Be Patient and Do Not Spam")
    ti.sleep(1)
    exit()

res = rq.get(url = URL, headers = HDR)
rtx = res.text

soup = bs(rtx , PARS)
brn = soup.find('span' , class_ = 'a-size-large product-title-word-break').getText()
sym = soup.find('span' , class_ = 'a-price-symbol').getText()
prc = round(float(soup.find('span' , class_ = 'a-price-whole').getText()) , 3)
print(f"The Price of a \n{brn}\n is :-> {sym}{prc}")

print(f"DEBUG → price = {prc}, expected price = {TARG_PR}")

if prc <= TARG_PR:
    with sm.SMTP(HOST) as conn:
        conn.starttls()
        conn.login(
            user = MY_EM, 
            password = PAS
        )
        conn.sendmail(
            from_addr = MY_EM,
            to_addrs = TO_SEND_EM,
            msg = f'Subject :- Low Price Alert\nThe Price of the item {brn} is only {sym}{prc} !!!\nRecommended SHOP NOW'
        )
else:
    print("\nNo Such Discount Found\n")