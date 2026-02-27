import requests as rq
import os as o
import time as ti
import datetime as dt
import pandas as pd
import prettytable as pt
from pprint import pprint as pp

#Extracting the data in a list form from the CSV
FILE = 'currency.csv'
data = pd.read_csv(FILE)
lis_val = data.Code.to_list()
curr_sym_val = data.Symbol.to_list()
name_val = data['Currency Name'].to_list()

#The Currency Formats the API Supports are given here
this_t = pt.PrettyTable(['Symbol' , 'Currency Code' , 'Currency Name'])
for i in range(len(lis_val)):
    this_t.add_row([curr_sym_val[i] , lis_val[i] , name_val[i]])

print(f'The Formats that are supported currently are :- \n\n{this_t}')

#Getting the Current Date and Time based on Indian Standard Time (I.S.T)
now = dt.datetime.now()
mn = now.month
dy = now.day
yr = now.year
fvb = f'{dy}-{mn}-{yr}'

#Taking the User currency input
inp = input('Enter your Currency code here : ').strip().upper()
to_which = input("Enter the Currency You wanna Check here : ").strip().upper()

if inp not in lis_val or to_which not in lis_val:
    print('\nNot Found any Data\nTry Again ....')
    exit()

# #Static and secret Variables
API_KEY =  o.environ.get("EXCHANGE_API_KEY")

if not API_KEY:
    print('\nNot Allowed to Proceed ....')
    o.system('cls' if o.name == 'nt' else 'clear')
    exit()

URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{inp}'

#Getting the Set Result
res = rq.get(url = URL)
res.raise_for_status()

data = res.json()
print('Processing ....')
ti.sleep(1)
print('Done ......\n')
print(f"Relative to {inp} the rates are :->\n")
pp(data['conversion_rates'])

print('\nIn a more beautiful format is here :- \n\n')
myTable = pt.PrettyTable(["Currency ID","Current Value"])
for i,j in data['conversion_rates'].items():
    myTable.add_row([i , j])

print(myTable)

val = data['conversion_rates'][to_which]

print(f'\n1{inp} = {val}{to_which} as per the current I.S.T. Time {fvb}\n')