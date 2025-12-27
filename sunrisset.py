#understanding API With Parameters
import requests as rq
import datetime as dt

#Static Values
URL = 'https://api.sunrise-sunset.org/json'
MY_LAT = 22.804565
MY_LONG = 86.202873
param = {
    'lat' : MY_LAT,
    'lng' : MY_LONG,
    'formatted' : 0
}

res = rq.get(url = URL , params = param)
if res.status_code == 200:
    val = res.json()
    print(f"Required JSON Value is :-\n{val}")

    sunr = val['results']['sunrise']
    suns = val['results']['sunset']
    print(f"The Sunrise and the Sunset Times are :- \n{sunr}\n{suns}")

    now = dt.datetime.now()
    print(f"The Current UNIX time accd IST is :\n{now}\n")
else:
    print("Wrong URL\n")
    res.raise_for_status()