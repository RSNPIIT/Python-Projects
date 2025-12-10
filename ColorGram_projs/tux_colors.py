import colorgram as co

clr = co.extract('tux.jpg' , 30)
lis = []

for cl in clr:
    re = cl.rgb.r
    gr = cl.rgb.g
    bl = cl.rgb.b
    new_t = (re , gr , bl)
    lis.append(new_t)

print(f"\nThe Colours in Tux are :- \n{lis}")
