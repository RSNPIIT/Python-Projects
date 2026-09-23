import requests as rq

par = {
    'amount' : 10 ,
    'type' : 'boolean' 
}

URL = 'https://opentdb.com/api.php'

res = rq.get(url = URL , params = par)

if res.status_code == 200:
    val = res.json()    
    question_data = val['results']
    # print(f'Data is :- \n\n{val['results']}')

else:
    print("\nERR: SOME ERROR\n")
    res.raise_for_status()