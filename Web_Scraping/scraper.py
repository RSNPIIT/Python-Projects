import requests as rq
from bs4 import BeautifulSoup as bs

URL = 'https://news.ycombinator.com/news'

res = rq.get(url = URL)
rtx = res.text

#Getting the Heading Text From the URL API
soup = bs(rtx , 'html.parser')
print(soup.prettify())