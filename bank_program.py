import time as ti
import os as o

bal = 0
attmpt = 0
bank_goes = True

def deposit():
    global bal

    try:
        amt = float(input("Enter the Deposit Amount here (in ₹) : "))
    except (KeyboardInterrupt , EOFError) as kb:
        print("\nNot Allowed to Skip for Security purposes")
        return
    except ValueError as v:
        print("Non Negative Values Given Here\nThese arent allowed")
        return
    if amt <= 0:
        print("Negative and Zero is not Allowed\nThe Amount must be a +ve Decimal Number")
        return
    else:
        bal += amt
        print(f"Amount of ₹{round(amt ,3)} successfully deposited")
        return

def withdraw():
    global bal

    try:
        amt = float(input("Enter the Withdrawal Amount here (in ₹) : "))
    except (KeyboardInterrupt , EOFError) as kb:
        print("\nNot Allowed to Skip for Security purposes")
        return
    except ValueError as v:
        print("Non Negative Values Given Here\nThese arent allowed")
        return
    if amt <= 0:
        print("Negative and Zero is not Allowed\nThe Amount must be a +ve Decimal Number")
        return
    elif amt > bal:
        print(f"You dont have ₹{amt} in your account\nTransaction Failed")
        return
    else:
        bal -= amt
        print(f"Amount of ₹{round(amt ,3)} successfully withdrawn")
        return

def get_bal():
    global bal
    print(f"Your Balance is :-> ₹{bal}")
    return

print("Welcome User -> Get Started\nThe Rule is Quite Simple")
while bank_goes:
    attmpt += 1
    print("="*60)
    print("Press the Following as per what you may need\n1 = Check Balance\n2 = Deposit Money\n3 = Withdraw Money\n4 = Exit the Bank")
    try:
        val = abs(int(input("Enter the Required Input Here : ")))
    except (KeyboardInterrupt , EOFError) as kb:
        print("\nFor Security Purposes Skipping is Illegal\n")
        continue
    except ValueError as v:
        print("Non Decimal Values Given.....\nGive again")
        continue
    else:
        if val == 1:
            get_bal()
        elif val == 2:
            deposit()
        elif val == 3:
            withdraw()
        elif val == 4:
            print(f"Thankyou for using 🄯Tux Banking Sollutions\nThis Banking Sowtware is in a Copyleft license under GNU GPL General Public License Ver.3 \nApp Used for {attmpt} times....\nPlease Come Again")
            bank_goes = False
            break
        else:
            print("Wrong Value\nPerhaps You have given a mistaken key\nPlease Go Again")
            continue
    finally:
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')