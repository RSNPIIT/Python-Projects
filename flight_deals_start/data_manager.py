import requests as rq

SHEET_URL = 'https://docs.google.com/spreadsheets/d/1BJUsYruoLtrLKU3-Xz08h2nTgQceaqI01UlzVg0WOq0/edit?gid=0#gid=0'
SHEETY_L = 'https://api.sheety.co/730aac9e4e18d7c1db79088dfe53112a/flightDeals/prices'

class DataManager:
    def __init__(self):
        self.ap = SHEETY_L

    def api_talk(self):
        res = rq.get(url = self.ap)
        self.gt = res.status_code
        if self.gt == 200:
            return res.json()['prices']         
        else:
            res.raise_for_status()
    
    def update_it(self ,id , iata_Code):
        SHEETY_PL = f'{SHEETY_L}/{id}'
        PAYLOAD = {
            'price': {
                'iataCode' : iata_Code
            } 
        }
        n_re = rq.put(url = SHEETY_PL , json = PAYLOAD)
        n_re.raise_for_status()