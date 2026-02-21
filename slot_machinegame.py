import random as r

MAX_LINE = 3
MAX_BET = 100
MIN_BET = 1

ROWS = 3
COLS = 3
SYM_CNT = {
    'A': 5,
    'B': 4,
    'C': 3,
    'D': 2
}
SYM_VAL = {
    'A': 5,  
    'B': 4,
    'C': 3,
    'D': 2    
}

def ch_wini(columns , lines , bet, values):
    win = 0
    win_l = []
    for li in range(lines):
        sym = columns[0][li]
        for coln in columns:
            symb_to_check = coln[li]
            if sym != symb_to_check:
                break
        else:
            win += values[sym] * bet
            win_l.append(li + 1)
    
    return win , win_l

def slot_machine(rows , cols , sym):
    all_sym = []

    for syb, sc in sym.items():
        for _ in range(sc):
            all_sym.append(syb)
    
    colm = []
    for _ in range(cols):
        col = []
        curr_sym = all_sym[:]
        for _ in range(rows):
            value = r.choice(curr_sym)
            curr_sym.remove(value)
            col.append(value)
    
        colm.append(col)
    
    return colm

def pr_slotmach(colss):
    for row in range(len(colss[0])):
        for i ,coln in enumerate(colss):
            if i != len(colss) - 1:
                print(coln[row], end = ' | ')
            else:
                print(coln[row])

def deposit():
    while True:
        try:
            amt = abs(int(input("Enter the Deposit Amount in ₹ : ")))
        except (KeyboardInterrupt , EOFError):
            print("No Spamming\nExiting Gracefully\n")
            continue
        except ValueError as v:
            print(f"\nNon Integer Values Given")
            continue
        if amt == 0:
            print("0 is not allowed here")
            continue
        else:
            break
    return amt

def get_line_num():
    while True:
        try:
            lines = abs(int(input(f"Enter the Number of Lines to bet on 1 to {MAX_LINE} : ")))
        except (KeyboardInterrupt , EOFError):
            print("No Spamming\nExiting Gracefully\n")
            continue
        except ValueError as v:
            print("\nNon Integer Values Given")
            continue
        if not (1 <= lines <= MAX_LINE):
            print("Not Allowed\nValue Not in Range")
            continue
        else:
            break
    return lines    

def better_getter():
    while True:
        try:
            bett = abs(int(input(f"Enter your Bet in range {MIN_BET} to {MAX_BET} in ₹ : ")))
        except (KeyboardInterrupt , EOFError):
            print("No Spamming\nExiting Gracefully\n")
            continue
        except ValueError as v:
            print("\nNon Integer Values Given")
            continue
        if not (MIN_BET <= bett <= MAX_BET):
            print("Not Allowed\nValue Not in Range")
            continue
        else:
            break
    return bett 

def main():
    bal = deposit()

    while True:
        print(f"\nCurrent Balance: ₹{bal}")

        line = get_line_num()
        bet = better_getter()
        val = bet * line

        if val > bal:
            print("Insufficient balance.")
            continue

        bal -= val

        slot = slot_machine(ROWS , COLS , SYM_CNT)
        pr_slotmach(slot)

        winni, winni_l = ch_wini(slot , line , bet , SYM_VAL)

        bal += winni

        print(f"You won ₹{winni}")
        print("You win on lines :", *winni_l)

        if bal <= 0:
            print("Game Over. You're broke.")
            break

main()