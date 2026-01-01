#Taking Data from the API and Formatting it correctly
import html
import requests as rq

par = {
    'amount' : 10,
    'type' : 'boolean'
}

URL = 'https://opentdb.com/api.php'

res = rq.get(url = URL , params = par)

if res.status_code == 200:
    val = res.json()
    my_val = html.unescape(val['results'])
    print(f"The JSON Value of the Request is : \n\n{my_val}\n")
else:
    print(f"Some Error Occurred\nOr Maybe Internet Problem \nERR:Response Code {res.status_code}")
    res.raise_for_status(
