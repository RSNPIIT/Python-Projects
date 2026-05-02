import json as js
import os as o
import time as ti
import sys as s

# Static Variables
FILE = 'value.json'
attmpt = 0
SYM = '-'*15

# Loading the data from the file from an earlier itera
if o.path.exists(FILE):
    try:
        with open(FILE) as f:
            lib = js.load(f)

    except (js.JSONDecodeError, ValueError) as jl:
        lib = {}
        
else:
    lib = {}

# Saver Funtion
def save_it(th):
    with open(FILE , 'w') as f:
        js.dump(th , f , indent = 4)

# Menu driven code
while True:
    print("-"*50)
    attmpt += 1
    print(f"{SYM} Library Management Program {SYM}")
    print("1. -> Add Books by ISBN (Update if already added)")
    print("2. -> Search Book by ISBN")
    print("3. -> Remove the book (Issued to Student)")
    print("4. -> Exit the app")

    try:
        ch = abs(int(input("Enter the Choice here : ")))

    except (KeyboardInterrupt , EOFError) as kb:
        print("\nError :-> Illegal exit unsupported")
        continue

    except ValueError as v:
        print("\nError :-> Non integer value unsupported")
        continue

    except OverflowError as ov:
        print("\nError :-> Super long value unsupported")
        continue

    except Exception as ex:
        print(f"\nError :-> {ex}")
        continue

    else:
        if ch == 1:
            try:
                isbn = input("Enter the ISBN number here : ").strip().title()

            except (KeyboardInterrupt , EOFError) as kb:
                print("\nError :-> Illegal exit unsupported")
                continue
            
            else:
                if isbn not in lib:
                    name = input("Enter the Name of the book here :").strip().title()
                    lib[isbn] = name
                    print(f"Details of the book with ISBN number {isbn} has been added successfully")
                else:
                    print(f"The Book with isbn number {isbn} already exists\n")
                    ji = input("Do You wanna update the same (Y/N) :-> ").strip().lower()

                    if ji == 'y':
                        nn = input("ENter the updated name of the book here :-> ").strip().title()
                        lib[isbn] = nn
                        print(f"Details of Book number {isbn} has been updated")

                    else:
                        print(f"Details of Book number {isbn} has been kept untouched")
                save_it(lib)

        elif ch == 2:
            try:
                isbn = input("Enter the ISBN number here : ").strip().title()

            except (KeyboardInterrupt , EOFError) as kb:
                print("\nError :-> Illegal exit unsupported")
                continue
            
            else:
                if isbn in lib:
                    book = lib[isbn]
                    print(f"The Corresponding Book is :-> {book}")
                else:
                    print(f"Details of book corresponding to ISBN {isbn} not found\n")
        
        elif ch ==3:
            try:
                isbn = input("Enter the ISBN number here : ").strip().title()

            except (KeyboardInterrupt , EOFError) as kb:
                print("\nError :-> Illegal exit unsupported")
                continue
            
            else:
                if isbn in lib:
                    print(f"The Details of ISBN {isbn} have been found")
                    cong = input("Are you sure you wanna delete (Y/N) :-> ").strip().lower()
                    if cong == 'y':
                        print(f"The Details of book number {isbn} has been deleted\n")
                        del lib[isbn]

                        save_it(lib)
                    else:
                        print(f"The details of book number {isbn} is kept as is\n")
                else:
                    print(f"The details of Book number {isbn} not found\n")

        elif ch == 4:
            print(f"Thankyou for using our app\nPlease return again soon\nApp used for {attmpt} times\n")
            break
        
        else:
            print("Wrong Input\nCode Breakage here")
            ti.sleep(1)
            o.system('cls' if o.name == 'nt' else 'clear')            
            s.exit()
    finally:
        print('-'*50)
        print(f"{SYM} ITERATION :-> {attmpt + 1} {SYM}")

print("🄯 RSNPIIT (Ramrup Satpati) IIT Madras | Released under the GNU GPLv3 License")