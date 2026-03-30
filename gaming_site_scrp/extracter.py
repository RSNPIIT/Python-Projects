import time as ti
from bs4 import BeautifulSoup as bls

# Static Variables 
FILE = "scrper.html"
PARSER = 'html.parser'
TFILE = 'saver.txt'
WMOD = 'w'
ENCD = 'utf-8'

# Extracting the File Here
with open(FILE) as rf:
    hgf = rf.read()

# Giving the Output to Beautiful Soup
soup = bls(hgf ,PARSER)
tilte = soup.title.string

# Now Getting the Titles of the games here
titl = soup.find_all('h2')
tup = []
for t in titl:
    sth = t.find('strong')
    if sth:
        tex = sth.getText().strip()
        tup.append(tex)

trt = list(reversed(tup))

with open(TFILE , WMOD , encoding = ENCD) as w:
    w.write(f"-"*50)
    w.write(f"\n{tilte}\n")
    w.write('-'*50)
    for j in trt:
        w.write(f'\n{j}\n')
        w.write('-'*50)

ti.sleep(1)
print("Successfully Written to the Text File")