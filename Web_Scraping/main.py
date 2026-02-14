import requests as rq
from bs4 import BeautifulSoup as bs

URL = 'https://news.ycombinator.com/news'

res = rq.get(url = URL)
rtx = res.text

#Getting the Heading Text From the URL API
soup = bs(rtx , 'html.parser')
tex = soup.find_all('tr', class_='athing')
art_txt = []
art_lnk = []
pois = []
for jh in tex:
    texl = jh.find('span' , class_ = 'titleline').find('a')
    texs = texl.getText()
    texlnk = texl.get('href')
    art_txt.append(texs)
    art_lnk.append(texlnk)

    stxt = jh.find_next_sibling('tr')
    stag = stxt.find('span', class_='score')
    scr_val = stag.getText() if stag else "0 points"
    pois.append(scr_val)

    print('-' * 60)
    print(f'Heading -> {texs}')
    print(f'URL -> {texlnk} ')
    print(f'Points -> {scr_val}')
    print('-' * 60)