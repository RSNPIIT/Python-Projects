#UDEMY DAY15 Completed
import random
import turtle
screen = turtle.Screen() 
pour_turtle = turtle.Turtle()
pour_turtle.hideturtle()
pour_turtle.speed(0)
pour_turtle.penup()
pour_turtle.goto(0, -100)  
Menu = {
    'espresso': {
        'ingredients': {
            'milk': 0,
            'water': 50,
            'coffee': 100
        },
        'cost': 1.5
    },
    'latte': {
        'ingredients': {
            'milk': 150,
            'water': 200,
            'coffee': 24
        },
        'cost': 2.5
    },
    'cappuccino': {
        'ingredients': {
            'milk': 100,
            'water': 250,
            'coffee': 24
        },
        'cost': 3.0
    }
}
resource = {
    'water' : 300,
    'milk' : 300,
    'coffee' : 300
}

def is_resource_suff(order):
    for item in order:
        if order[item] >= resource[item]:
            print(f"Sorry We have run out of : {item}")
            return False
    return True

def process_coins():
    total = abs(int(input("How Many Quarters ? : "))) * 0.25
    total += abs(int(input("How Many Dimes ? : ")))* 0.1
    total += abs(int(input("How Many Nickels ? : ")))* 0.05
    total += abs(int(input("How Many Pennies ? : ")))* 0.01
    print(f"The total value of your money is : ${round(total,2)}")
    return total

def is_transaction_successful(money_received , drink_cost):
    if money_received >= drink_cost:
        change =round(money_received - drink_cost , 2)
        print(f"Here ${change} in change")
        global profit
        profit += drink_cost
        return True
    else:
        print("Sorry that's not enough money, Amount Refunded")
        return False

def make_drink(drink , order_ingredients):
    """ Deduct the said ingredients from the resources """
    try:
        pour_turtle.clear()
        pour_turtle.color("brown")
        pour_turtle.pendown()
        pour_turtle.begin_fill()
        for i in range(100):
            pour_turtle.forward(2)
            pour_turtle.left(5)
        pour_turtle.end_fill()
        pour_turtle.penup()
    except turtle.Terminator:
        # If the screen was closed, skip animation
        pass

    for item in order_ingredients:
        resource[item] -= order_ingredients[item]
    print(f"Here is your {drink}")

profit = 0
is_on = True
while is_on:
    print("Enter the Item you wanna purchase or enter off if you wanna quit or enter report to see the resoirces availaible")
    ch = input("Enter whatever you thought ,the options are (espresso/latte/cappuchino) : ").strip().lower()
    if ch == 'off':
        print("Thankyou for coming we hope you'll love our coffee")
        is_on = False
    elif ch == 'report':
        print("Here is all the progress of orders done so far")
        print(f"Water : {resource['water']}ml")
        print(f"Milk : {resource['milk']}ml")
        print(f"Coffee : {resource['coffee']}g")
        print(f"Money : ${profit}")
    else:
        if ch in Menu:
            drink = Menu[ch]
            print(drink)
            if is_resource_suff(drink['ingredients']):
                payment = process_coins()
                if is_transaction_successful(payment,drink['cost']):
                    make_drink(ch, drink['ingredients'])
        else:
            print("Your Selected Drink is not in Menu \nPlease make an existing choice of itens")
            continue