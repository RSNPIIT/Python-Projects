import time as ti
import os as o
import platform as pt

# Static Elements
ATTMPT = 0
FILE = 'transaction_saver.txt'
MODE = 'a'

def process_payment(bal, amt, lim=10000):
    if amt <= 0:
        return (False, 'Invalid Amount')
    elif amt > lim:
        return (False, 'Exceeds Limit Amount')
    elif amt > bal:
        return (False, 'Insufficient Funds')
    else:
        rem = bal - amt
        return (True, rem)

def analyzer(succ, msg):
    if succ:
        print(f"Transaction Successful\nNew Balance is -> {msg}")
    else:
        print(f"Transaction Failed\nError Message is -> {msg}")

while True:
    ATTMPT += 1
    try:
        bl = abs(int(input("Enter the Balance here : ")))
        am = int(input("Enter the Amount here : "))

    except (KeyboardInterrupt, EOFError) as kb:
        print("\nPlease Don't Spam\nSkipping this Iteration\n")
        ti.sleep(1)
        continue

    except ValueError as v:
        print("\nError Occurred\nNon Integral Values are not allowed\n")
        ti.sleep(1)
        continue

    else:
        res = process_payment(bl, am)
        analyzer(*res)

        ch = input("Do you wanna go again? (Y/N) :-> ").strip().lower()
        if ch == 'n':
            print(f"Thankyou for using our app\nPlease come again\nApp used for {ATTMPT} times")
            ti.sleep(1)
            o.system('cls' if pt.system() == 'Windows' else 'clear')
            break
        else:
            continue

    finally:
        try:
            with open(FILE , MODE) as f:
                f.write(f'Balance -> {bl} | Amount -> {am} | Result -> {res}\n')
        except:
            pass

print("🄯 RSNPIIT - (Ramrup Satpati)\nReleased under the GNU GPLv3 License\n")