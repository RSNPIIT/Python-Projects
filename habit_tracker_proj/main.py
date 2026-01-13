import requests as rq
import datetime as dt

#Static Variables
U_NAME = 'ramrup'
U_TKN = "hjhk34h3jk4hj34h3jk4"
KRE = 'yes'
URL = "https://pixe.la/v1/users"
GR_ID = 'grph1'

#JSON Parameters
U_PARAMS = {
    'token' : U_TKN,
    'username' : U_NAME,
    'agreeTermsOfService' : KRE,
    'notMinor' : KRE,
}

GR_PRMS = {
    'id' : GR_ID,
    'name' : 'Coding Graph',
    'unit' : 'commit',
    'type' : 'float',
    'color' : 'ichou'
}

hdrs = {
    'X-USER-TOKEN' : U_TKN
}

#Pulling the Today's Date in YYYYMMDD Format and putting in the Said JSON
now = dt.datetime.now()
if now.month < 10 and now.month > 0:
    mnt = f'0{now.month}'
else:
    mnt = now.month
if now.day < 10 and now.day > 0:
    dy = f'0{now.day}'
else:
    dy = now.day

DT_VAL = f'{now.year}{mnt}{dy}'

ADD_PR = {
    'date' : now.strftime('%Y%m%d'), #In Place of this strftime this can be 
    'quantity' : '10'
}

#Making the Said Account
res = rq.post(url = URL , json = U_PARAMS)
print(f'\n{res.status_code}\n')
print(f'\n{res.text}\n')
try:
    print(f'\n{res.json()}\n')
except ValueError as v:
    print("Value's Not JSON Type")

#Now Making the Graph
GRAPH_UL = f'{URL}/{U_NAME}/graphs'
val = rq.post(url = GRAPH_UL , json = GR_PRMS , headers = hdrs)
print(f'\n{val.status_code}\n')
print(f'\n{val.text}\n')
try:
    print(f'\n{val.json()}\n')
except ValueError as v:
    print("Value is not JSON Type")

#Now Adding the Said Pixels to the Graph (Note - Visiblity is Subject to JST Japan Standard Time while Now Gives in IST Format)
ADD_PIX_UL = f'{URL}/{U_NAME}/graphs/{GR_ID}'
d_v = rq.post(url = ADD_PIX_UL , json = ADD_PR , headers = hdrs)
print(f'\n{d_v.status_code}\n')
print(f'\n{d_v.text}\n')
try:
    print(f'\n{d_v.json()}\n')
except ValueError as v:
    print("Value is not JSON Type")