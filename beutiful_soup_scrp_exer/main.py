from bs4 import BeautifulSoup as bls

FILENAME = 'website.html'

with open(FILENAME) as f:
    con = f.read()

#Making an Instance of Beautiful Soup and telling it Parse HTML
soup = bls(con , 'html.parser')
print(soup.title.string)
print(f'\n{soup.prettify()}')

#Getting all the said A tags and then looping through them
all_atags = soup.find_all(name = 'a')
print(all_atags)

for x in all_atags:
    y = x.get('href')
    print(y)

#Finding The Said Tag using the id name and class_ kwargs in Python
hdg = soup.find_all(name = 'h1', id = 'name')
print(f'\n{hdg}')

for h in hdg:
    print(h.getText())

#Getting only one the top value using select one and selector
se_val = soup.select_one(selector = "p a").string
my_n = soup.select_one('#name').string
hdgs = soup.select('.heading')

print(f"The Said Value is : {se_val} and {my_n} and {hdgs}")