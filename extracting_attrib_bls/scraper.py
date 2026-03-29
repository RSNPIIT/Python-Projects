from bs4 import BeautifulSoup as bls

FILE = 'scrap_it.html'

with open(FILE) as f:
    val = f.read()

soup = bls(val , 'lxml')
# print(soup.prettify())

print("Welcome to RSNPIIT Scrapes it project\nHere we scrape things\n")
print('-'*50)
tils = soup.title.string
print(f"Title -> {tils}")

print('-'*50)
crd = soup.find_all('div' , class_ = 'item-card')

for c in crd:
    i_id = c.get('id')
    ver = c.find('h3').getText()
    prc = c.find('p' , class_ = 'price').getText()
    stt = c.find('p' , class_ = 'status').getText()
    lnk = c.find('a')
    rep = lnk.get('href')
    print(f"Item -> {ver}")
    print(f"ID -> {i_id}")
    print(f"Price -> {prc}")
    print(f"Status -> {stt}")
    print(f"Link -> {rep}")
    print("-"*50)
