import random as r
import time as ti
import sys as s
import os as o
import platform as pt

try:
    n = abs(int(input("Enter the number of sentences you wanna suggest of entering : ")))

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
        print("I am sorry buddy\nNobody can give so many documents but good try\n")
        ti.sleep(1)
        o.system('cls' if pt.system() == 'Windows' else 'clear')
        s.exit()

except (KeyboardInterrupt , EOFError) as kb:
    print("\nExitting Please Dont Spam ......\n")
    ti.sleep(1)
    o.system('cls' if pt.system() == 'Windows' else 'clear')
    s.exit()

except ValueError as v:
    print(f"This Value of {n} is not allowed please enter a Numeric Value\nPlease Re-Enter\n")
    ti.sleep(1)
    o.system('cls' if pt.system() == 'Windows' else 'clear')
    s.exit()

except OverflowError as ov:
    print("Due to wrong input some error occurred\n")
    ti.sleep(1)
    o.system('cls' if pt.system() == 'Windows' else 'clear')
    s.exit()    

else:
    fv = r.randint(2 , n) if n >= 2 else 1 
    print(f"\nThe Algorithm has decided the Final Value of number(s) of sentences as {fv}")

    all_d = []
    for i in range(1 , fv + 1):
        doc = input(f"Enter the value of document number {i} : ").lower().strip().split()
        all_d.append(doc)
    
    all_w = {}
    fin_wrd = set()

    for doc in all_d:
        fin_wrd.update(doc)

    for x in fin_wrd:
        all_w[x] = set()
    
    for doc_n , doc in enumerate(all_d , start = 1):
        for w in doc:
            all_w[w].add(doc_n)

    print("\nThe search !nd3x is built successfully\n")
    print(all_w)

    # Now Basically we take user input
    qre = input("\nPlease Search for some Word ----\n").strip().lower()
    if qre in all_w:
        print(f"The word {qre.title()} found in the documents with the status quo as :- {all_w[qre]}\n")
    else:
        print(f"The word {qre.title()} doesnt exist\nWord not found")

finally:
    print("\nReverse Search by 🄯 RSNPIIT (Ramrup Satpati) IIT Madras\nReleased under GNU GPLv3 License")