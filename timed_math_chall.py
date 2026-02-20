import random as r
import time as ti

OPE = ['+','-','//','*']
wr = 0

def gen_ex():
    val1 = str(r.randint(3,11))
    opr = r.choice(OPE)
    val2 = str(r.randint(3,11))

    expr = f'{val1} {opr} {val2}'
    ans = eval(expr)
    return expr , ans

try:
    TOT_PR = abs(int(input("Enter How Many Problems You wanna Solve : ")))
except (KeyboardInterrupt , EOFError):
    print("\nExiting....")
    exit()
except ValueError as v:
    print('\nNon Integer Values Given')
    exit()

input("Press Enter to start (Recommended for timed power users) ->> ")

stt_t = ti.time()

print('_'*60)
for i in range(TOT_PR):
    print(f"ROUND {i+1}")
    ex ,an = gen_ex()
    while True:
        try:
            guess = int(input(f"Problem {i+1} -> {ex} : "))
        except (KeyboardInterrupt ,EOFError):
            print('\nNo You Cant Escape By a Ctrl/Cmd C or D\nTry Again')
            continue
        except ValueError as v:
            print("\nHow Can a Math Answer be a String\nTry Again")
            continue
        else:
            guess = str(guess)
            if str(an) == guess:
                print("\nCorrect --- Moving to Next Round")
                break
            else:
                wr += 1
                print('\nIncorrect --- Repeating unless you Make it correct')
                continue     

print('_'*60)

end_t = ti.time()
t_tken = end_t - stt_t

print(f'\nGreat Work\nFinished in {round(t_tken ,2)} seconds with {wr} mistakes')

if wr < 3:
    print("\nAwesome --- You are a math Genius")
print('\nGAME OVER')