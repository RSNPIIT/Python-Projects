import pprint as pp

sales_data = [
    {"item": "Laptop",  "price": 1000, "units": 5,  "category": "Electronics"},
    {"item": "Mouse",   "price": 25,   "units": -2, "category": "Electronics"},
    {"item": "Chair",   "price": 150,  "units": 10, "category": "Furniture"},
    {"item": "Desk",    "price": 300,  "units": 0,  "category": "Furniture"},
    {"item": "Phone",   "price": 500,  "units": 3,  "category": "Electronics"},
]

flis = lambda x : x['units'] > 0
vik_lis = list(filter(flis , sales_data))
print("The final List of true sales' data is ->\n")
pp.pprint(vik_lis)

final_l = list(filter(lambda x: x['category'] == 'Electronics' , vik_lis))
total_rev = sum(list(map(lambda x: x['price'] * x['units'] , final_l)))
print(f"\nThe sum of the true electronics items is -> ₹{total_rev}\n")