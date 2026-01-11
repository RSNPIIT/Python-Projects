import requests as rq
from twilio.rest import Client
import os as o

#CUSTOM ERROR SYNTAX
class Error_This_Error_Made_By_RSNPIIT(Exception):
    pass

#URL CONTENT AND STATIC CONTENT
STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

#ENV VARIABLES
STOCK_API_KEY = o.getenv("STOCK_API_KEY")
NEWS_API_KEY = o.getenv("NEWS_API_KEY")
ACCD_SID = o.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = o.getenv("TWILIO_AUTH_TOKEN")
TW_PHN_NO = o.getenv("TWILIO_PHONE_NUMBER")
MY_PHN_NO = o.getenv("MY_PHONE_NUMBER")

if not STOCK_API_KEY or not NEWS_API_KEY or not ACCD_SID or not AUTH_TOKEN or not TW_PHN_NO or not MY_PHN_NO:
    raise Error_This_Error_Made_By_RSNPIIT("Environment Variable Doesn't Exist")

#PARAMETERS (IN PY-Dict Form or JSON Form)
REQ_PM = {
    'function' : "TIME_SERIES_DAILY",
    'symbol' : STOCK_NAME,
    'apikey' : STOCK_API_KEY

}
A_REQ_PM = {
    'apikey' : NEWS_API_KEY,
    'qInTitle' : COMPANY_NAME
}

#Extracting the Data From the Set API to get the Yesterday and the Day Before (Stock Price _ Closing)
res = rq.get(url = STOCK_ENDPOINT , params = REQ_PM)
if res.status_code == 200:

    val = res.json()

    my_l = [l for (k ,l) in val['Time Series (Daily)'].items()]
    yes_closing_val = float(my_l[0]['4. close'])
    day_bef_yes_clv = float(my_l[1]['4. close'])
    g_b = '▲' if yes_closing_val > day_bef_yes_clv else '▼'

    diff = abs(round(yes_closing_val - day_bef_yes_clv, 3))

    p_dif = (diff / day_bef_yes_clv) * 100
    p_dif = round(p_dif ,3)

    if p_dif >= 1:
        ret = rq.get(url = NEWS_ENDPOINT , params = A_REQ_PM)
        ret.raise_for_status()
        vbl = ret.json()
        artcl = vbl['articles'][:3]

        t_l = [f"\nSTOCK_STATUS : {g_b} by {p_dif}% \nTITLE : {i['title']} \nDESCRIPTION : {i['description']} \n" for i in artcl]

        client = Client(ACCD_SID, AUTH_TOKEN)
        for i in range(len(t_l)):
            mess = client.messages.create(
                body = t_l[i],
                from_ = TW_PHN_NO,
                to = MY_PHN_NO
            )
            # print(mess.status)
    else:
        print(f"\n{g_b} by {p_dif}%\n")
else:
    print("\nAPI FAILED\n")
    res.raise_for_status()