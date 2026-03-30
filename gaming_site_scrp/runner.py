import requests as rq
import time as ti
import os as o
from bs4 import BeautifulSoup as bls

# Static Variables ->
URL = 'https://in.ign.com/portal-2/201591/lists/the-top-100-video-games-of-all-time'
FILE = 'scrper.html'
MODE = 'w'
PARSER = 'html.parser'
HRD = {
    "User-Agent": "Mozilla/5.0"
}
ENCD = 'utf-8'

# Getting the Response and Making the HTML of that
res = rq.get(url = URL, headers = HRD)
res.raise_for_status()
rtx = res.text
print(len(rtx))

# Using the bs4 Beautiful Soup method to get the things
soup = bls(rtx ,PARSER)
soup_prtify = soup.prettify()

# Now basically writing the same to an HTML File
with open(FILE , MODE , encoding = ENCD) as f:
    f.write(soup_prtify)

# Formatting for a good UI
print("Written to HTML File Successfully")
ti.sleep(1)
o.system('cls' if o.name == 'nt' else 'clear')