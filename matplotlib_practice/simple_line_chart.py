import matplotlib.pyplot as plt
import time as ti
import sys as s
import os as o
import platform as pt
import random as r
import pandas as pd

try:
    n = abs(int(input("Enter the number of elements you wanna enter into the graph : ")))

    if not n:
        print("\nI'm sorry but you cant put this here\n")
        ti.sleep(1)
        o.system('cls' if pt.system() == 'Windows' else 'clear')
        s.exit()

    elif n == 0:
        print("Not Allowed Here \nThe Number cant be zero\nPlease (RE)Enter the same")
        ti.sleep(1)
        o.system('cls' if pt.system() == 'Windows' else 'clear')
        s.exit()
    
    elif n > 30:
        print(f"I am sorry buddy\nI don't have the patience to type so much so as {n} items\n")
        ti.sleep(1)
        o.system('cls' if pt.system() == 'Windows' else 'clear')
        s.exit()

except (KeyboardInterrupt , EOFError) as kb:
    print("\nExitting Please Dont Spam ......\n")
    ti.sleep(1)
    o.system('cls' if pt.system() == 'Windows' else 'clear')
    s.exit()

except ValueError as v:
    print(f"String Input Value is not allowed please enter a Numeric Value\nPlease Re-Enter\nError code {v}")
    ti.sleep(1)
    o.system('cls' if pt.system() == 'Windows' else 'clear')
    s.exit()

except OverflowError as ov:
    print("Due to wrong input some error occurred\n")
    ti.sleep(1)
    o.system('cls' if pt.system() == 'Windows' else 'clear')
    s.exit()    

except Exception as e:
    print("Some Uncapped Exception has occurred however we have successfully caught the exception nicely\n")
    ti.sleep(1)
    o.system('cls' if pt.system() == 'Windows' else 'clear')
    s.exit()    

else:
    num = r.randint(2 , n) if n >= 2 else 1

    print(f"The Algorithm has decided the number of Items to be {num}")

    lis = []
    for i in range(num):
        try:
            a = float(input(f"Enter the Value number {i+1} here : "))

        except (KeyboardInterrupt , EOFError) as kb:
            print("\nExitting Please Dont Spam ......\n")
            ti.sleep(1)
            o.system('cls' if pt.system() == 'Windows' else 'clear')
            s.exit()

        except ValueError as v:
            print(f"String Input Value is not allowed please enter a Numeric Value\nPlease Re-Enter\nError code {v}")
            ti.sleep(1)
            o.system('cls' if pt.system() == 'Windows' else 'clear')
            s.exit()

        else:
            lis.append(a)

    idx = [f'v{i+1}' for i in range(len(lis)) ]
    ser = pd.Series(lis , name = 'Sample Plot Series' , index = idx)
    print(f"Finally the List is Made ----\nMaking the Graph\nPlease Wait ...")

    ti.sleep(1)
    plt.plot(ser)

    print("The Plot is Made here it is .....")
    plt.title("My Graph")
    plt.show()
finally:
    print("\nReverse Search by 🄯 RSNPIIT (Ramrup Satpati) IIT Madras\nReleased under GNU GPLv3 License")