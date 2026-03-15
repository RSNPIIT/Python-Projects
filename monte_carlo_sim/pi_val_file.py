import random as r
import datetime as dt
import math as m
import time as ti
import os as o

now = dt.datetime.now()
yr = now.year

def get_pizza(attmpts):
    hits = 0

    for _ in range(attmpts):
        x = r.random()
        y = r.random()
        if x**2 + y**2 <= 1:
            hits += 1
    
    pival = round(4 * (hits / attmpts) , 8)
    err = 1 / (attmpts) ** 0.5
    diff = (m.pi - pival)
    return pival , err , diff

try:
    att = abs(int(input("Enter the Number of times you wanna test : ")))

    if att == 0:
        print("\nZero is Not Allowed Here\n")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')
        exit()
except (KeyboardInterrupt , EOFError) as kb:
    print("Exitting ...\nPlease Dont Spam...")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    exit()
except ValueError as v:
    print(f"\nWrong Input Given \n{v}")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear') 
    exit()
else:
    pi_v , er , dif = get_pizza(att)
    pi = round(m.pi , 8)
    print(f"Congratulations\nThe Status :-\nAttempts :-> {att}\nError (calculated as inversely prop to root of the attempts number) :-> {er}\nPi Calculated value :-> {pi_v}\nPi Stored Value is :-> {pi}\nDiffernce from the actual pi (in Python's Math Lib.) is :-> {dif}\n")
finally:
    print(f"\nI thank GitHub for the idea behind the code -- Original code was written in Ruby\nHappy PI Day {yr}")