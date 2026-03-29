import random as r

# Static Variables
FILE = 'scrap_it.html'
MODE = 'w'
categ = ['tools', 'ai', 'data', 'web', 'security', 'dev' ]
shipp = ['global', 'local', 'restricted', 'licensed']
stock_st = ['Out of Stock' , 'In Stock']

htm_str = """<!DOCTYPE html>
<html lang = 'en'>
<head>
<meta charset="UTF-8">
<title>RSNPIIT Mega Scrape Lab</title>
</head>
<body>
<h1>RSNPIIT ChipnScape Inventory</h1>
<div class="grid">
"""

htm_end = """</div>
</body>
</html>
"""

tiles = ""

for i in range(1 ,101):
    catf = r.choice(categ)
    ship = r.choice(shipp)
    stat = r.choice(stock_st)
    pr = round(r.uniform(10 , 500) , 2)
    stck_num = r.randint(0 ,100)
    lnk = r.randint(10,450)

    itms = f"""
    <div class="item-card" id="item-{i}" data-category="{catf}" data-shipping="{ship}">
        <h3 class="name">Scraper-Bot v{r.randint(1,5)}.{r.randint(0,9)}</h3>
        <p class="price" data-currency="INR">₹{pr}</p>
        <p class="status" data-stock="{stck_num}">{stat}</p>
        <a href="https://github.com/{lnk}" title="View Source" target="_blank">View Repository</a>
    </div>
    """
    tiles += itms

COMP_SCR = htm_str + tiles + htm_end
with open(FILE , MODE ,encoding = 'utf-8') as f:
    f.write(COMP_SCR)

print("Successfully Created the HTML File to scrape on")