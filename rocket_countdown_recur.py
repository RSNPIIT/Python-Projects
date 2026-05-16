import time as ti
import sys as s
import os as o

# Setting a Recursion Limit
s.setrecursionlimit(5000)

#  Static variables
SYM = '-' * 50
NIL = 'n'
ATM = 0

def countdown(tmn):
    if tmn > 0:
        print(f"{SYM}\nCountdown :- {tmn} seconds to launch the rocket")
        ti.sleep(1)
        countdown(tmn - 1)
    else:
        print("Blast Off 🚀")
        return 

while True:
    global ATM
    ATM += 1

    try:
        num = abs(int(input("Enter the Time You wish to go for rocket countdown here : ")))
    
    except (KeyboardInterrupt , EOFError):
        print("\nAbrupt Illegal Exit is not allowed here")
        o.system('cls' if o.name == 'nt' else 'clear')
        continue
    
    except ValueError:
        print("Non-Integer Values detected Here\nPlease give an integral number\n")
        o.system('cls' if o.name == 'nt' else 'clear')
        continue
    
    else:
        try:
            countdown(num)
        
        except RecursionError:
            print("Recursion Error Occurred\nThe Given Number was too big here")
            o.system('cls' if o.name == 'nt' else 'clear')
            continue

        print("Lets go, another round shall we ?")
        if (_ := input("Enter your choice here (Y/N) :-> ").strip().lower()) == NIL:
            print(f"\nExitting the app thankyou for using me\nApp used for {ATM} times")
            break
    finally:
        print(f" < TIMER APP PROGRAM (G!VEN BY DEV AS AN 3AST3R EGG)> ")

print("The timer | 🄯 RSNPIIT (Ramrup Satpati) IIT Madras | Released under GNU GPLv3 license")