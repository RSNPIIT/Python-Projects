#This class is responsible for talking to the Flight Search API.
import requests as rq
import datetime as dt
import os as o

MY_API_KEY = o.getenv("AMADEUS_API_KEY")
MY_API_SECRET = o.getenv("AMADEUS_API_SECRET")
TOKEN_ENDPOINT = 'https://test.api.amadeus.com/v1/security/oauth2/token'
CITY_ENDPOINT = 'https://test.api.amadeus.com/v1/reference-data/locations/cities'
BASE_UL_TOSEARCH = 'https://test.api.amadeus.com/v2/shopping/flight-offers'

class FlightSearch:
    def __init__(self):
        self.api_key = MY_API_KEY
        self.api_secret = MY_API_SECRET
        self._token = self.get_new_token()
        
    def get_iata_code(self ,city):
        HEDR = {
            'Authorization' : f'Bearer {self._token}'
        }
        PAR = {
            'keyword' : city,
            'max' : 1
        }
        red = rq.get(url = CITY_ENDPOINT , params = PAR , headers = HEDR)
        return red.json()['data'][0]['iataCode']
        

    def get_new_token(self):
        header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': 'client_credentials',
            'client_id': MY_API_KEY,
            'client_secret': MY_API_SECRET
        }
        response = rq.post(url= TOKEN_ENDPOINT, headers=header, data=body)
        return response.json()['access_token']
    
    def search_flights(self ,dest):
        tom = dt.datetime.now().date() + dt.timedelta(days = 1)
        after_time = dt.datetime.now().date() + dt.timedelta(days = 7)

        HDRS = {
            'Authorization' : f'Bearer {self._token}'
        }
        
        PAR = {
            "originLocationCode" : "LON",
            "destinationLocationCode" : dest,
            "departureDate" : tom.isoformat(),
            "returnDate" : after_time.isoformat(),
            "adults" : 1,
            "nonStop" : "true",
            "currencyCode" : "GBP",
            "max" : 5
        }
        rdf = rq.get(url = BASE_UL_TOSEARCH , params = PAR , headers = HDRS)
        rdf.raise_for_status()

        d_val = rdf.json().get('data')
        if not d_val:
            return None

        prices = []
        for offr in d_val:
            prices.append(float(offr['price']['grandTotal']))

        return min(prices)