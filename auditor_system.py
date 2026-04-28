items = ['Laptop' , 'Mouse' , 'Keyboard' , 'Headphones']
prices = [1000 , '25.50' , 'Unknown' , 150]
GRAND_TOTAL = 0

def add_to_total(amount):
    global GRAND_TOTAL
    GRAND_TOTAL += amount
    return GRAND_TOTAL

def audit_it(item , price):
    try:
        price = float(price)
        add_to_total(price)
        return (True , "Sucess")
    except:
        return (False , "Data Invalid")

COM_IT = enumerate(zip(items , prices) , start = 1)

for idx , (item , mrp) in COM_IT:
    print(f"ID -> {idx} | item -> {item} | mrp -> {mrp}")
    print(audit_it(item , mrp))

print(f"Grand Total :-> {GRAND_TOTAL}")