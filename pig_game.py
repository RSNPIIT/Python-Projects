import random as r
import time as ti

def roll_dice():
    min_v = 1
    max_v = 6
    roll = r.randint(min_v ,max_v)
    return roll

try:
    plrs = abs(int(input("Enter the Number of Players Here (1-4): ")))
except KeyboardInterrupt as kb:
    print("\nExiting Nicely...")
    ti.sleep(1)
    print("\nDone,...")
    exit()
except ValueError as v:
    print("\nNon Integral Values Given")
    exit()

if not 1<= plrs <= 4:
    print("\nInvalid Thing\nMust be between 1 & 4")
    exit()

max_v = 50
plr_scores = [0 for _ in range(plrs)]

while max(plr_scores) < max_v:
    for i in range(plrs):
        scr = 0

        print(f"Player {i+1}'s Chance\n")
        while True:
            r1 = input("Do You Wanna Roll (y/n) : ").strip().lower()
            if r1 != 'y':
                print("\nTurn Done\n")
                break
            
            val = roll_dice()

            if val == 1:
                scr = 0
                print("\nYou Rolled a 1\nScore Nullified at 0\nTurn Over\n")
                break
            else:
                scr += val
                print(f"You Rolled a {val}")
            
            print(f"Turn Score : {scr}\n")


        plr_scores[i] += scr
        
        if plr_scores[i] >= max_v:
            print(f"Player {i+1} hits the max upper limit {max_v} and wins so game has to end yo !!\n")
            break

        print(f"Cumulative Score of the Player {i+1} is {plr_scores[i]}\n")
    
    if max(plr_scores) > max_v:
        break

max_val = max(plr_scores)
win_idx = plr_scores.index(max_val)

print(f"Player {win_idx + 1} wins with a score of {max_val}\n")