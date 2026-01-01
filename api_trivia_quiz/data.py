#Taking Changing values accd to the Series
import requests as rq

par = {
    'amount' : 10,
    'type' : 'boolean'
}

URL = 'https://opentdb.com/api.php'

res = rq.get(url = URL , params = par)

if res.status_code == 200:
    val = res.json()
    # print(f"The JSON Value of the Request is : \n\n{val['results']}\n")

    question_data = val['results'] #So as to replce the Hardcoded Values and all

else:
    print(f"Some Error Occurred\nOr Maybe Internet Problem \nERR:Response Code {res.status_code}")
    res.raise_for_status()