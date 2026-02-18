import requests as rq
import datetime as dt
import time as ti
from bs4 import BeautifulSoup as bs

#Taking Inputs
now = dt.datetime.now()

try:
    yr = abs(int(input("Enter the Year You Wanna Travel to in YYYY : ")))
    mon = abs(int(input("Enter the Month You Wanna Travel to in MM : ")))
    day = abs(int(input("Enter the Day You Wanna Travel to in DD : ")))
except KeyboardInterrupt as k:
    print("Please Dont Spam\nExiting Nicely...")
    ti.sleep(1)
    exit()
except ValueError as vl:
    print("Non Integral Values Given")
    exit()

if yr >= now.year:
    print("Wrong Year\nHow are you Living in the Future ?")
    exit()
elif yr < 1958:
    diff = abs(yr - 1958)
    print(f"Billboard Didn't Form it's 100 hit charts till 1958\nYou are {diff} years behind")
    exit()

if day >= 31 or mon >= 12:
    print(f"Wrong Month and Day Input Given")
    exit()

elif day == 0 or mon == 0:
    print(f"Wrong Month and Day Input Given")
    exit()

val = f'{yr}-{mon}-{day}'

if not val:
    print("\nError :-> The Date Given is wrong or has incorrect formatting")
    exit()

#API Header Parameters
hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"}

#GETTing the API Headers Value
URL = f'https://www.billboard.com/charts/hot-100/{val}'
res = rq.get(url = URL , headers = hdr)

#Running the Beautiful Soup Instance
soup = bs(res.text, 'html.parser')
sng_span = soup.select("li ul li h3")
song_lis = [s.getText().strip().title() for s in sng_span]

print(f"The Set Song List is {song_lis}\n")
