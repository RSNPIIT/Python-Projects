#This mini peoject I have built to revise Dictionaries and conditional statements
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
print("Welcome to Python Restaurant , Pytho is Elated to Welcome you")
print("This Restaurant belongs to the same chain ass the FOSS , same as Tux Rest. and Buggy Rest.")
print("The Menu is :\nPizza : 40\nBurger : 50\nSalad : 20\nFries : 15\nPasta : 60\nNoodles : 55\nCoffee : 35\nBiriyani : 90\nFried Rice : 65\nToast : 20\nNuggets : 45\nFish : 64\nEgg : 46")
print("What would you like to Order ? , आप क्या मंगवाना पसंद करेंगे ? :")
order = input("Enter your Order Here :")
price = 0
key = order.strip().lower()
if key in menu:
    price += menu[key]
    print("Do You want something else also ?")
    choice = input("Enter your Choice Yes/No :")
    xe = choice.strip().lower()
    if xe == "yes":
        sec_ord = input("And please make your second order :")
        ya = sec_ord.strip().lower()
        if ya in menu:
            price += menu[ya]
            print("Your Total Cost to Pay is : ",price)
        else:
            print(f"Sorry we dont have {sec_ord} yet. Please check again later")
            print(f"The Net Price is : {price}")
    elif (xe == "no") or (xe == "nope"):
        print("Alight No Problem ")
        print("The Total is :",total)
    else:
        print("ERR : Invalid Choice")
else:
    print(f"Sorry we dont have {order} yet. Please check again later")
print("Thankyou for Shopping with us")
        