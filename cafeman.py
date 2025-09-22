#This mini peoject I have built to revise Dictionaries and conditional statements and Looping Iterators
menu = {
    'pizza' : 40,
    'burger' : 50,
    'salad' : 20,
    'fries' : 15,
    'pasta' : 60,
    'noodles' : 55,
    'coffee' : 35,
    'biriyani' : 90,
    'fried Rice' : 65,
    'toast' : 20,
    'nuggets' : 45,
    'fish' : 64,
    'egg' : 46
}
price = 0
print("The Menu is :\nPizza : 40\nBurger : 50\nSalad : 20\nFries : 15\nPasta : 60\nNoodles : 55\nCoffee : 35\nBiriyani : 90\nFried Rice : 65\nToast : 20\nNuggets : 45\nFish : 64\nEgg : 46")
print("This Restaurant belongs to the same chain ass the FOSS , same as Tux Rest. and Bugdroid's Rest.")
flag = False
while not flag:
    order = input("Enter your Order Here :").strip().lower()
    if order in menu:
        price += menu[order]
        print("The Menu is :\nPizza : 40\nBurger : 50\nSalad : 20\nFries : 15\nPasta : 60\nNoodles : 55\nCoffee : 35\nBiriyani : 90\nFried Rice : 65\nToast : 20\nNuggets : 45\nFish : 64\nEgg : 46")
        print(f"The order {order} is placed successfully")
        while True:
            print("Now You make a choice | The Choices are :\n1 - Make another Order\n2 - Exit\n")
            choice = abs(int(input("Enter a Choice Here : ")))
            if choice == 1:
                sec_ch = input("Enter the second choice of menu : ").strip().lower()
                if sec_ch in menu:
                    price += menu[sec_ch]
                    print(f"Congratulations {sec_ch} has been placed\n")
                else:
                    print("The selected item is unavailable currently , Please check again later\n")
        
            elif choice == 2:
                if price > 500:
                    price = 0.9 * price
                print(f"--Your Grand Total is : {price} ---")
                print("-- Thankyou Very Much For Visiting Our Restaurant --")
                flag = True
                break
            else:
                print("-- Wrong Choice --")
                continue 
    else:
        print("Your Order is not in Menu , Maybe try something else")
        continue        