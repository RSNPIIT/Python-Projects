import time as ti
import subprocess as sb
import os as o
from bs4 import BeautifulSoup as bls

# Static Variables 
FILE = "scrper.html"
PARSER = 'html.parser'
TFILE = 'saver.txt'
WMOD = 'w'
ENCD = 'utf-8'

# We Will Extract the File But what if the File is Deleted or Does not Exist so Ideally We need to run the Runner.py first to get the HTML file
if not o.path.exists(FILE):
    print(f"File := {FILE} does not exists\n(RE)Creating it...")
    val = sb.run(
        ['python3' ,'runner.py'],
        check = True,
        capture_output = True,
        text = True
        )
    print(f'{val.stdout}\nSuccessfully Created the HTML/LXML File')
else:
    print(f"File {FILE} exits\nContinuining....")
    ti.sleep(1)

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

# Now We Create the TXT File and Save the Elements of the List in reversed order
with open(TFILE , WMOD , encoding = ENCD) as w:
    w.write(f"-"*50)
    w.write(f"\n{tilte}\n")
    w.write('-'*50)
    for j in trt:
        w.write(f'\n{j}\n')
        w.write('-'*50)

ti.sleep(1)
print("Successfully Written and Saved to the Text File")
