import colorgram as co

# Getting the Colours (Top 30 in this case)
clr = co.extract('tux.jpg' , 30)

# Now We convert the Colour Objects to RGB Integers Via List Comprehension
lis = [(c.rgb.r , c.rgb.g , c.rgb.b) for c in clr]

print(f"\nThe Colours in Tux are :- \n{lis}")
