from bs4 import BeautifulSoup as bls

FILE = 'sample.html'
print("Hello Everyone\nWelcome to RSNPIIT Scrapes the Web Directory\nThis is Me Navigating my Way through the Beautiful Soup (bls4) Web Scraping tool\n")
print("-"*50)

print("The HTML File is :-\n")
with open(FILE) as f:
    con = f.read()

soup = bls(con , 'html.parser')
# print(soup.prettify())
print(f"As a Sample File We Will Extract Info from this cause why not\nTitle :- {soup.title.string}")

crd = soup.find_all('div', class_ = 'project-card')
print('-'*50)
for c in crd:
    name = c.find('h2' , class_ = 'project-title').getText()
    stats = c.find('span' , class_ = 'status-tag').getText()
    lic = c.find('p', class_ = "license").getText()
    print(f'Name -> {name}')
    print(f"Status -> {stats}")
    print(f"License -> {lic}")
    if not lic:
        print("This Project is either unLicensed or under an unknown License")
    elif any(x in lic for x in ['PSF', 'BSD', 'MIT' , 'Apache']):
        print("This Project is under an Open Source Permissive License")
    elif any(x in lic for x in ['GPLv2', 'GPLv3', 'LGPL', 'AGPL']):
        print("This Project is under an Open Source CopyLeft License")
    else:
        print("This Project is under a proprietary Copyright License")    
    print("-"*50)
