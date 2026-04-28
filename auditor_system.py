import time as ti
import os as o
import sys as s

# Static variables
items = []
prices = []
GRAND_TOTAL = 0

# Defining the Functions here
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

try:
    n = abs(int(input("Enter the number of items you wanna store here :-> ")))

except (KeyboardInterrupt , EOFError) as kb:
    print("\nExitting the app...\nPlease don't spam\n")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()

except ValueError as v:
    print("\nWrong Value given\nNon Integer values are not given here")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()

except OverflowError as o:
    print("\nOverflow Error happened")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()

except Exception as e:
    print(f"Some Exception occurred\n{e}")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()

else:
    for i in range(n):
        print('-'*50)
        try:
            xi = input(f"Enter the name of the item number {i+1} here : ").strip().title()
            items.append(xi)
            print('-'*50)
            pr = input(f"Enter the price of the item number {i+1} here : ").strip()
            prices.append(pr)
        except (KeyboardInterrupt , EOFError) as kb:
            print(f"\nIteration {i+1} skipped\nCtrl + C wont work here\n")
            continue

COM_IT = enumerate(zip(items , prices) , start = 1)

for idx , (item , mrp) in COM_IT:
    print(f"ID -> {idx} | item -> {item} | mrp -> {mrp}")
    print(audit_it(item , mrp))

print(f"Grand Total :-> {GRAND_TOTAL}")