import requests as rq
import datetime as dt
import os as o

#My Said URLs
URL = "https://app.100daysofpython.dev"
SHEETY_API_END = "https://api.sheety.co/730aac9e4e18d7c1db79088dfe53112a/cpy/workouts"

#My Static Values Masked
YOUR_APP_ID = o.environ["NUTRITIONIX_APP_ID"]
YOUR_NUTRITION_API_KEY = o.environ["NUTRITIONIX_API_KEY"]

hdrs = {
    'x-app-id' : YOUR_APP_ID,
    'x-app-key' : YOUR_NUTRITION_API_KEY   
}

#The Post Endpoints Masked (':)' Apologies for naming it PUT_)
PUT_UL = f'{URL}//v1/nutrition/natural/exercise'
PUT_PMS = {
    'query' : "ran 15 kilometres", #Required
    'weight_kg' : 70 ,#Optional Argument
    'height_cm' : 150, #Optional Argument
    'age' : 20, #Optional Argument
    'gender' : 'male' #Optional Argument
}
SHEETY_HEADERS = {
    "Authorization": f"Bearer {o.environ['SHEETY_BEARER_TOKEN']}",
    "Content-Type": "application/json"
}

#The Main Part
res = rq.post(url = PUT_UL , json = PUT_PMS , headers = hdrs)
res.raise_for_status()
if res.status_code == 200:
    re_js = res.json()

    #Getting the Particular Value
    t_d = dt.datetime.now().strftime("%Y%m%d")
    t_n = dt.datetime.now().strftime("%X")

    for ex in re_js['exercises']:
        s_in = {
            'workout' :{
                'date' : t_d,
                'now' : t_n,
                'exercise' : ex['name'],
                'duration' : ex['duration_min'],
                'calories' : ex['nf_calories']
            }
        }
        rd = rq.post(url = SHEETY_API_END , json = s_in , headers = SHEETY_HEADERS)
        print(f"\nThe Requested API Returned {rd.status_code}\n")
        print(rd.text)
        rd.raise_for_status()