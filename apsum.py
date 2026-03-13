#Simple AP sum is here 
import time as ti
import os as o
import prettytable as pt

try:
    a = float(input("Enter the Starting Number here : "))
    n = abs(int(input("Enter the Limit upto which sum should'be given  : ")))
    dif = float(input("Enter the Difference of consecutive terms : "))

except (KeyboardInterrupt , EOFError) as kb:
    print("\nExitting Please Don't Spam....\n")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    exit()

except ValueError as  v:
    print("\nNon Numeral Values given here as string input isnt given\n")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    exit()

else:
    trms = round(a + (n - 1) * dif , 3)
    su = round((n / 2) * (2* a + (n - 1)* dif) , 3)

    print(f"\nThe Status is : \nStarting Value -> {a}\nCommon Difference -> {dif}\nLimit on terms -> {n}\nThe Final Term -> {trms}\nSum upto the Final term -> {su}")

    myT = pt.PrettyTable(["Starting Value", "Common Difference", "Limiting", "nth Term" , "nth Sum"])
    myT.add_row([a , dif , n , trms , su])

    print(f"\nIn a More Beautiful Manner it is :-\n\n{myT}\n")
finally:
    print("\nThe AP Goes beautifully\nGiven By programmer RSNPIIT aka Ramrup Satpati from IIT Madras\n")