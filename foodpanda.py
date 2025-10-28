#Revision By Ramrup_Satpati based off of Day 16 Udemy Python Bootcamp by Dr.Angela Yu and The London App Brewery
print(r"""
     _____ ____  ____  ____    ____  ____  ____  _____ ____ 
    /    //  _ \/  _ \/  _ \  /  _ \/  __\/  _ \/  __//  __\
    |  __\| / \|| / \|| | \|  | / \||  \/|| | \||  \  |  \/|
    | |   | \_/|| \_/|| |_/|  | \_/||    /| |_/||  /_ |    /
    \_/   \____/\____/\____/  \____/\_/\_\\____/\____\\_/\_\
                                                        
    """)

menu = {
    'potatofry': {
        'ingredients': {
            'oil': 50,
            'vegetables': 25,
            'water': 10
        },
        'cost': 25
    },
    'vegcurry': {
        'ingredients': {
            'oil': 40,
            'vegetables': 30,
            'water': 20
        },
        'cost': 35
    },
    'mixedsalad': {
        'ingredients': {
            'oil': 10,
            'vegetables': 40,
            'water': 5
        },
        'cost': 20
    }
}
resources = {
    'oil': 200,
    'vegetables': 300,
    'water': 400
}
profit = 0

def check_resources(order):
    for item in order:
        if order[item] > resources[item]:
            print(f"Sorry We have run out of {item}")
            return False
    return True


def process_money():
    val = abs(int(input("Enter the number of rupee coins : ")))*1
    val += abs(int(input("Enter the number of paise coins : ")))*0.01
    print(f"The Net Value of Your Money is : ₹{round(val,2)}")
    return val

def transaction(user_amt, val_amt):
    if user_amt > val_amt:
        print("TRANSACTION SUCCESSFUL")
        change = user_amt - val_amt
        print(f"Here is : ₹{round(change,2)} in change")
        global profit
        profit += val_amt
        return True
    else:
        print(f"Sorry ₹{user_amt} is insufficient for your order.")
        short = val_amt - user_amt
        print(f"You are : ₹{round(short,2)} amount short")
        return False

def make_food(food , order):
    for item in order:
        resources[item] -= order[item]
    print(f"Here is your {food}")

machine_state = True
print("The Menu Items are :-\nPotato Fry : ₹25\nVeg Curry : ₹35\nMixed Salad : ₹20")
while machine_state:
    choice = input("Enter Your Choice amongst the menu items or enter off to exit or report to show current resources : ").strip().lower()
    if choice == 'off':
        print("Really Nice to Meet You \nGoodbye Please Come back later :)")
        machine_state = False
        break
    elif choice == 'report':
        print("The Current State of The Storehouse is :-")
        print(f"Oil : {resources['oil']}L")
        print(f"Vegetables : {resources['vegetables']}kg")
        print(f"Water : {resources['water']}L")
        print(f"Profit : ₹{profit}")
    else:
        if choice in menu:
            val = menu[choice]
            if check_resources(val['ingredients']):
                amt = process_money()
                if transaction(amt,val['cost']):
                    make_food(choice,val['ingredients'])
        else:
            print("Selected Choice not in Menu \nPlease Come back later")
            continue