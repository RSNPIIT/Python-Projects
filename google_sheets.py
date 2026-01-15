import requests as rq

#Variables
GIVEN_NAME = input("Enter the Name to be Given to the Said Sheets : ").strip().title()
SOME_CONSTS = round(float(input("Enter the set Constants value here : ")) , 3)
SOME_VAR = int(input("Enter the set Variables here : "))
SOME_VALUES = int(input("Enter the given Values here : "))

#Google_API_Endpoints
URL = 'https://api.sheety.co/730aac9e4e18d7c1db79088dfe53112a/pythonTestTest/sheet1'
SHEETS_LINK = 'https://docs.google.com/spreadsheets/d/1USmxfwrgCEamDXfmrcIjKnWylwWxgczlcBCnnf8aZLg/edit?gid=0#gid=0'
#The Sheets Link has been Posted so as to test the code's working

RQ_PMS = {
    "sheet1" :{
        'name' : GIVEN_NAME,
        'values' : SOME_VALUES,
        'variables' : SOME_VAR,
        'constants' : SOME_CONSTS
    }
}
gt = rq.post(url = URL , json = RQ_PMS)
y = gt.status_code
if y == 200:
    print(f"The Given HTTP Feature Status Code is {y}\n")
    print(f"The Set Posted Data is : {gt.json()}\nIt Has been Successfully Pushed and posted\n")
else:
    print(f"The Given HTTP Feature Status Code is {y}\n")
    print(gt.text)
    gt.raise_for_status()