import os as o
import time as ti
import requests as rq
from bs4 import BeautifulSoup as bs

URL = 'https://web.archive.org/web/20200518073855/https://www.empireonline.com/movies/features/best-movies-2/'
FILENAME = 'movie/movies.txt'

res = rq.get(url = URL)
web = res.text

soup = bs(web , 'html.parser')
mv_l = []

all_m = soup.find_all(name = 'section' ,class_ = 'gallery__content-item')
for j in all_m:
    mvb = j.find('div', class_ = 'article-title-description').find('h3' , class_ = 'title').getText()
    mv_l.append(mvb)

mv_l.reverse()
o.makedirs('movie' , exist_ok = True)
with open(FILENAME , 'w') as j:
    print('Processing ...')
    
    for mov in mv_l:
        j.write(f'{mov}\n')

ti.sleep(1)
print('Done')