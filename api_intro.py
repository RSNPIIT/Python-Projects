import requests as rq

#Making an API Call From Python
res = rq.get(url = 'http://api.open-notify.org/iss-now.json')

#Getting a Response
print(f'The Response is : {res.status_code}\n')

res.raise_for_status() #It Automatically Raises Exception in case of a non 200 value

#Getting the API Data as a JSON Format
data = res.json()
print(f'The JSON Data is :\n{data}')

#Gettin the Latitude and Longitude as a Tuple
lat = data['iss_position']['latitude']
lo = data['iss_position']['longitude']
pos = (lat , lo)
print(f"The Position is :- {pos}")