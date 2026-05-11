import requests as rq
from bs4 import BeautifulSoup as bls

# Static Variables
URL = 'https://saitm.ac.in/blog/best-engineering-colleges-in-world-and-top-engineering-colleges-in-world/'
MODE = 'w'
FILE = 'site.html'
PRSR = 'html.parser'
ENCD = 'utf-8'

try:
    res = rq.get(url = URL)
    res.raise_for_status()
    txf = res.text

    soup = bls(txf , PRSR)

except Exception as ex:
    print(f"Exception Occurred as -> {ex}")

else:
    ptrtf = soup.prettify()

    with open(FILE , MODE, encoding = ENCD) as fl:
        fl.write(ptrtf)

    print("Written to file safely")