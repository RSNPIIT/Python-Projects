#Pizza Order Choice
print("---Welcome to the Tux (C) Corp Pizzerias---")
print("We serve three type of Authentic Pizzas i.e (Small(S)/Medium(M)/Large(L))")
ord = 0
cost = 0
while True:
    price = 0
    age = abs(int(input("May I know your age please : ")))
    choice = input("Which Choice do You Want (S/M/L) : ").strip().lower()
    if choice == 's':
        print("Small Pizza Added")
        price += 15
        cost += 15
    elif choice == 'm':
        print("Medium Pizza Added")
        price += 20
        cost += 20
    elif choice == 'l':
        print("Large Pizza Added")
        price += 25
        cost += 25
    else :
        print("Wrong Choice , Please Try again")
        break

    tp = input("Do you want to add toppings? (Y/N): ").strip().lower()
    if tp == 'y':
        print("Extra Veggie Toppings Added")
        price += 5
        cost += 5
    elif tp == 'n' :
        print("Fine, Extra Toppings Skipped")
    else:
        print("I'll Assume that as a No ; Fine , Toppings Skipped")

    mz = input("Do you want to add mozzarella cheese (Y/N): ").strip().lower()
    if mz == 'y':
        print("Extra Cheese Burst Added")
        price += 6
        cost += 6
    elif mz == 'n' :
        print("Fine, Extra Mozzarella Cheese Skipped")
    else:
        print("I'll Assume that as a No ;Fine Mozzarella Cheese Extra Skipped")

    hb = input("Do you want to add habanero sauce (Y/N): ").strip().lower()
    if hb == 'y':
        print("Extra Habanero and BBQ Sauce Added")
        price += 8
        cost += 8
    elif hb == 'n' :
        print("Fine, the item is Skipped")
    else:
        print("I'll Assume that as a No ;Fine Extra Item Skipped")

    co = input("Do you want to add a coke as a side drink (Y/N): ").strip().lower()
    if co == 'y':
        print("Coka Cola Added to the Order")
        price += 10
        cost += 10
    elif co == 'n' :
        print("Fine, Side Cola Skipped")
    else:
        print("I'll Assume that as a No ;It's Fine Side Cola Skipped")

    ord += 1

    if age <= 18 or price >= 150:
        price -= 0.1*price
        x = round(price,2)
        cost -= 0.1*cost
        y = round(cost/ord,2)
        print(f"Thankyou for coming here , Your total is : {x}$")

    else:
        price -= 0.05*price
        cost -= 0.05*cost
        x = round(price,2)
        y = round(cost/ord,2)
        print(f"Thankyou for coming here , Your total is : {x}$")
    
    
    x = round(price,2)
    y = round(cost/ord,2)

    print("Do you wanna make another order or Quit (Type any key to keep Going and a n or q to stop)")
    c = input("Make your decision : ").strip().lower()
    if c == 'n' or c == 'q' :
        print("Thankyou for the day , See You soon ")
        print(f"So far {ord} order(s) have been made with an average of {y}$ each order")
        break
    else:
        continue