import random as r
import time as ti
import sys as s
import os as o
import platform as pt

# Static Variables
attmpt = 0

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
    while True:
        qtin = False
        attmpt += 1
        try:
            qre = input("\nPlease Search for some Word or (q to quit) :- ").strip().lower()

            if qre == 'q':
                qtin = True
                print(f"Thankyou Ciao\nPlease come again won't you ?\nYou used the app for {attmpt} times")
                break

        except (KeyboardInterrupt , EOFError) as kb:
            print("\nNot Allowed -- I wont Let you exit\nFollow the rules enter q please\n")
            pass
        except Exception as e:
            print(f"Some Error occurred\n{e}")
            pass
        else:       
            if qre in all_w:
                print(f"The word {qre.title()} found in the documents with the status quo as :- {all_w[qre]}\n")
            else:
                print(f"The word {qre.title()} doesnt exist\nWord not found")
        finally:
            if not qtin:
                print("Please Enter....another cause why not......\n")

finally:
    print("\nReverse Search by 🄯 RSNPIIT (Ramrup Satpati) IIT Madras\nReleased under GNU GPLv3 License")