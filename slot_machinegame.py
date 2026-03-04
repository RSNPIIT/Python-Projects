#Simplified Slot Machine in Python3
import random as r
import time as ti
import os as o

GO_GAIN_VAL = 'Y'
attmpt = 0

def spin_row():
    lis = ['🍌' , '🍒' , '🍑' , '🍠']

    res = []
    for _ in range(3):
        res.append(r.choice(lis))
    return res

def print_row(slot):
    print(" | " .join(slot)) 
    return

def get_payout(slot , thebet):
    if slot[0] == slot[1] == slot[2]:
        if slot[0] == '🍒':
            return thebet * 3
        elif slot[0] == '🍠':
            return thebet * 4
        elif slot[0] == '🍌':
            return thebet * 5
        elif slot[0] == '🍑':
            return thebet * 10
    else:
        return 0

def main():
    bal = 100

    print("="*60)
    print("Welcome to Python Slots Game")
    print("Symbols :- \n🍌 | 🍒 | 🍑 | 🍠")
    print("="*60)

    while bal > 0:
        print(f"Current Balance = ₹{bal}")
        attmpt += 1
        try:
            bet = abs(int(input("Enter your bet here in INR (₹) : ")))
        except (KeyboardInterrupt , EOFError) as kb:
            print("Nope Due to Security reasons you are not allowed to exit illegally\n")
            continue
        except ValueError as v:
            print("\nNon Integer Value Given these are not allowed\n")
            continue
        else:
            if bet == 0:
                print("Zero is Not allowed here \n")
                continue
            elif bet > bal:
                print("The Bet amount is greater than the balance\n")
                continue
            bal -= bet
            row = spin_row()
            print_row(row)
            pay = get_payout(row , bet)
            if pay > 0:
                print(f"\nHoorah You won\nYoure a winner -- You won {pay}")
            else:
                print(f"\nSorry Looks like you lost\n")
            bal += pay
            
            print(f"Final Balance After Round {attmpt} is {bal}")
            go_gain = input("Do You want to go again :--(Y/N) : ").strip().upper()
            if go_gain != GO_GAIN_VAL:
                print("Please do come again")
                ti.sleep(2)
                o.system('cls' if o.system == 'nt' else 'clear')
                exit()
        finally:
            print("🄯 This Software owned by Tux Corp.. under the GNU G.P.L v3 License")

    print("You Have lost you're balance fully\nYoure Broke")

if __name__ == '__main__':
    main()