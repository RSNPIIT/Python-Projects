import random as r
import time as ti

STIME = 1
attmpt = 0

def roll_dice():
    this_n = r.randint(1,6)
    return this_n

while True:
    attmpt += 1
    print("\nTrust Your Luck\nRoll The Dice If You Dare")
    # ye_val = input("Enter Your Choice : [PLAY] [QUIT] :").strip().lower()
    print("\nLets See What You Got\n")
    ti.sleep(STIME)
    k = roll_dice()
    print(f"\nThe Number is : {k}")
    if k == 6:
        print("Whoa Look at You You Just hit a 6")
    elif  k == 6:
        print("Well ! Its one of the high scores ")
    
    print("CHOOSE YOU WANNA CONTINUE OR QUIT\n1.-Continue \n2. -Exit")
    try:
        ch = abs(int(input("Enter your Said Choice : ")))
    except ValueError as v:
        print("Error\nWrong Datatype Given \nPlease Give A Numeral Input")
        break
        exit()
    else:
        if ch == 1:
            continue
        elif ch == 2:
            print(f"\nWell Good Day To You This App Attempted For {attmpt} times")
            break
        else:
            print("\nWrong Value Given")

