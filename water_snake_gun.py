import random as r
import time as ti

#Static Variables
CH_L = ['snake','water','gun']
ATTMPT = 0
HUM_SCORE = 0
COMP_SCORE = 0
HUM_STREAK = 0
COMP_STREAK = 0

def comp_plays():
    comp_choice = r.choice(CH_L)
    return comp_choice

def hum_plays():
    global ATTMPT, HUM_SCORE, COMP_SCORE, HUM_STREAK, COMP_STREAK
    print(f"Round {ATTMPT + 1} is Live :-")
    print('---Welcome Candidate---\n---You Have 3 options - Snake Water & Gun---')
    while True:
        try:
            ch = input("Enter Your Choice Here : ").strip().lower()
        except KeyboardInterrupt as E:
            print("\nExiting Nicely ...")
            exit()

        ATTMPT += 1
        if ch not in CH_L:
            print("Wrong Value\nPlease Enter Correct Value")
            continue
        print("--- Computer Turn ---")
        get_cpv =comp_plays()
        print(f"\nThe Computer Chose {get_cpv}")
        check_it(ch ,get_cpv)

        print(f"Current Score :\nHUMAN -> {HUM_SCORE}\nCOMPUTER -> {COMP_SCORE}")
        if HUM_SCORE > COMP_SCORE:
            print("Human's At Lead")
        elif HUM_SCORE == COMP_SCORE:
            print("Both are at Same Level in Scoreboard")
        else:
            print("Computer's At Lead")
        print("Press <Any Key> to Continue and N to Exit")
        try:
            ex_c = input("Enter the Next Steps Here :").strip().lower()
        except KeyboardInterrupt as k:
            print("Nope Ctrl + C wont help you rules must be followed")
            pass
        if ex_c == 'n':
            print(f"Played For {ATTMPT} attempts With Current Human Streak {HUM_STREAK} and Current Computer Streak {COMP_STREAK}")
            print("Exiting ...")
            ti.sleep(1)
            break

        else:
            print("\nNext Round --LOADING")
            ti.sleep(1)
            continue
            
def check_it(x ,y):
    global HUM_SCORE, COMP_SCORE, HUM_STREAK, COMP_STREAK
    if x == 'snake' and y == 'water':
        print("Snake Drinks Water\nHuman Wins")
        HUM_SCORE += 1
        HUM_STREAK += 1
        COMP_STREAK = 0
    elif x == 'snake' and y == 'gun':
        print("Gun Shoots Snake\nComputer Wins")
        COMP_SCORE += 1
        COMP_STREAK += 1
        HUM_STREAK = 0
    elif x == 'water' and y == 'snake':
        print("Snake Drinks Water\nComputer Wins")
        COMP_SCORE += 1
        COMP_STREAK += 1
        HUM_STREAK = 0
    elif x == 'water' and y == 'gun':
        print("Water Corrodes Gun\nHuman Wins")
        HUM_SCORE += 1
        HUM_STREAK += 1
        COMP_STREAK = 0
    elif x == 'gun' and y == 'water':
        print("Water Corrodes Gun\nComputer Wins")
        COMP_SCORE += 1
        COMP_STREAK += 1
        HUM_STREAK = 0
    elif x == 'gun' and y == 'snake':
        print("Gun Shoots Snake\nHuman Wins")
        HUM_SCORE += 1
        HUM_STREAK += 1
        COMP_STREAK = 0
    elif x == y or y == x:
        print("Nothing Happened\nIts A Draw...")
        HUM_SCORE += 0
        HUM_STREAK += 0
        COMP_SCORE += 0
        COMP_STREAK += 0
    else:
        print("No Choices Left")

if __name__ == '__main__':
    hum_plays()