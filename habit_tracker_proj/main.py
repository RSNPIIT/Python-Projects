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
DT_val_mod = f'{now.year}-{mnt}-{dy}'
DT_VAL = f'{now.year}{mnt}{dy}'

ADD_PR = {
    'date' : now.strftime('%Y%m%d'), #In Place of this strftime this can be DT_VAL AS WELL
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

#Opt :- There can be a new date
# dt_n = dt.datetime(year = 2025 , month = 12 , day = 31)

#Modifying the Set Value -> HTTP Put
PUT_END = f'{URL}/{U_NAME}/graphs/{GR_ID}/{now.strftime("%Y%m%d")}'
New_d = {
    'quantity' : '15'
}
rej = rq.put(url = PUT_END , json = New_d , headers = hdrs)
print(f'\n{rej.status_code}\n')
print(f'\n{rej.text}\n')
try:
    print(f'\n{rej.json()}\n')
except ValueError as v:
    print("Value is not JSON Type")

#Deleting a Set Value -> HTTP Delete Method
DEL_END = f'{URL}/{U_NAME}/graphs/{GR_ID}/{now.strftime("%Y%m%d")}'
del_res = rq.delete(url = DEL_END , headers = hdrs)
print(f'\n{del_res.status_code}\n')
print(f'\n{del_res.text}\n')
try:
    print(f'\n{del_res.json()}\n')
except ValueError as v:
    print("Value is not JSON Type")
