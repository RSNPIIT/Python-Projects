import requests as rq
import os as o

my_api_key = o.getenv('OPENWEATHER_API_KEY')

if not my_api_key:
    raise RuntimeError("OPENWEATHER_API_KEY Not Set")

paras = {
    'lat' : 22.79,
    'lon' : 86.20,
    'cnt' : 40,
    'appid' : my_api_key
}
URL = 'https://api.openweathermap.org/data/2.5/forecast'

#This will get the required response ---The Open Parameters ---
res = rq.get(url = URL , params = paras)

is_rain = False
if res.status_code == 200:
    print("\nSuccessful API Extraction\n")
    val = res.json()
    # print(val['list'][0]['weather'])
    for x in val['list']:
        id_val = x['weather'][0]['id']
        id_val = int(id_val)
        if id_val < 700:
            is_rain = True
            break
        else:
            continue

else:
    print("\nExtraction Failed\n")
    res.raise_for_status()

if is_rain:
    print("\nCarry An Umbrella\nIt's Probably Going To Rain\n")
else:
    print("\nNot Gonna Rain\nIt's Sunny\n")