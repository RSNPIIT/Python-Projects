import colorgram as co

#Extract Colors
colors = co.extract('images.jpg' , 10)
my_l = []

#Taking All Colours Into Something we can read
for c in colors:
    re = c.rgb.r
    gr = c.rgb.g
    bl = c.rgb.b
    n_t = (re , gr , bl)
    my_l.append(n_t)

print(f"\nThe Colours Are :\n{my_l}")