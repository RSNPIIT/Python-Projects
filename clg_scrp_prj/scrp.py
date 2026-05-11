from bs4 import BeautifulSoup as bls
import time as ti
import os as o
import sys as s
import subprocess as sb

FILE = 'site.html'
PRSR = 'html.parser'

if not o.path.exists(FILE):
    print(f"Scraping File {FILE} not found in the current directory\n")

    try:
        print("Making the HTML File here")      
        sb.run(
            ["python3" , "studius.py"],
            capture_output = True,
            text = True,
            check = True
        )
    except:
        pass

with open(FILE) as f:
    cont = f.read()

soup = bls(cont , PRSR)

print("---Here are the Top Engineering Universities in the entire world---")

strong_tags = soup.find_all("strong")

keywords = [
    "University",
    "Institute",
    "College",
    "Technology",
    "IIT"
]

bad_words = [
    "Campus",
    "Facilities",
    "Courses",
    "Interview",
    "Fee",
    "Career",
    "Engineering",
    "Level",
    "Life"
]

colg_set = set()

for tag in strong_tags:
    tdf = tag.get_text(strip = True)
    # print('-'*50)

    keywords = [
        "University",
        "Institute",
        "College",
        "Technology",
        "IIT"
    ]

    bad_words = [
        "Campus",
        "Facilities",
        "Courses",
        "Interview",
        "Fee",
        "Career",
        "Engineering",
        "Level",
        "Life",
        "Testing"
    ]

    if(
        any(word in tdf for word in keywords) 
        and not any(word in tdf for word in bad_words)
    ):
        colg_set.add(tdf)

for idx , w in enumerate(sorted(colg_set) , start = 1):
    print("-"*50)
    print(f"Rank -> {idx} || College -> {w}")

print('-'*50)