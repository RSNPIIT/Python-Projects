from bs4 import BeautifulSoup as bls
import time as ti

# Static Variables 
FILE = "scrper.html"
PARSER = 'html.parser'
TFILE = 'saver.txt'
APMODE = 'a'

# Extracting the File Here
with open(FILE) as rf:
    hgf = rf.read()

# Giving the Output to Beautiful Soup
soup = bls(hgf ,PARSER)
tilte = soup.title.string
print(f'The Title is :- \n{tilte.strip()}')

# Now Getting the Titles of the games here
titl = soup.find_all('h2')
for t in titl:
    sth = t.find('strong')
    if sth:
        with open(TFILE , APMODE) as a:
            a.write(f"{sth.getText().strip()}\n")

ti.sleep(1)
print("Successfully Written to the Text File")