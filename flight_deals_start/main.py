from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager
import pprint as pp

yk = FlightSearch()
dm = DataManager()
nnt = NotificationManager()

rd = dm.api_talk()
for rw in rd:
    if rw['iataCode'] == '':
        rw['iataCode'] = yk.get_iata_code(rw['city'])

    dm.update_it(rw['id'] , rw['iataCode'])
    yk.search_flights(rw['iataCode'])

for row in rd:
    dest = row['iataCode']
    trg_price = row['lowestPrice']
    cit = row['city']

    chp_prc = yk.search_flights(dest)
    if  chp_prc is None:
        continue

    if  chp_prc < trg_price:
        nnt.send_mess(cit ,trg_price ,chp_prc)

print('\nUpdated Sheet Data is : \n\n')
pp.pprint(rd)
