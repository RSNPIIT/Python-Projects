print('Welcome to Tic Tac Toe\n')

xstate = [0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0]
ostate = [0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0]
turn = 1

def sums(a,b,c):
    return a + b + c

def printboard():
    ZERO = 'X' if xstate[0] else  ('O' if ostate[0] else 0)
    ONE = 'X' if xstate[1] else  ('O' if ostate[1] else 1)
    TWO = 'X' if xstate[2] else  ('O' if ostate[2] else 2)
    THREE = 'X' if xstate[3] else  ('O' if ostate[3] else 3)
    FOUR = 'X' if xstate[4] else  ('O' if ostate[4] else 4)
    FIVE = 'X' if xstate[5] else  ('O' if ostate[5] else 5)
    SIX = 'X' if xstate[6] else  ('O' if ostate[6] else 6)
    SEVEN = 'X' if xstate[7] else  ('O' if ostate[7] else 7)
    EIGHT = 'X' if xstate[8] else  ('O' if ostate[8] else 8)
    print(f" {ZERO} |  {ONE} | {TWO}")
    print(f"-- | -- | --")
    print(f" {THREE} |  {FOUR} | {FIVE}")
    print(f"-- | -- | --")
    print(f" {SIX} |  {SEVEN} | {EIGHT}")

def checkwin(xs , ot): 
    wins = [[0,1,2] , [3,4,5] , [6,7,8] , [0,3,6] , [1,4,7] , [2,5,8] , [0,4,8] , [2,4,6]]
    for w in wins:
        if sums(xs[w[0]] , xs[w[1]] , xs[w[2]]) == 3:
            print("X Wins\n")
            print('GAME OVER\n')
            return True

        if sums(ot[w[0]] , ot[w[1]] , ot[w[2]])  == 3:
            print("O Wins\n")
            print("GAME OVER")
            return False

    return False

while True:
    printboard()
    print('\n')

    if turn == 1:
        print("X's Turn :-\n")

        try:
            val = abs(int(input("Enter a Value Here :- ")))

        except ValueError:
            print('Please Enter a Number in Range (0,8) all included\n')
            continue

        else:
            if val not in range(9):
                print(f"Please Enter a Number Between 0 and 8, {val} is Out of Bounds\n")
                continue
            
            if xstate[val] == 1 or ostate[val] == 1:
                print("Your Opponent Has already chosen this Choose Something Else\n")
                continue       
            
            elif val in range(9):
                xstate[val] = 1
                turn -= 1

            else:
                print("Please Enter a Value Between 0 and 8\n")
                continue

    else:
        print("Y's Turn :-\n")

        try:
            ral = abs(int(input("Enter a Value Here :-")))
        
        except ValueError:
            print('Please Enter a Number in range (0,8) all included\n')
            continue

        else:

            if ral not in range(9):
                print(f"Please Enter a Number Between 0 and 8, {ral} is Out of Bounds\n")
                continue

            if xstate[ral] == 1 or ostate[ral] == 1:
                print("Your Opponent Has Already Chosen This Choose Something Else\n")
                continue

            elif ral in range(9):
                ostate[ral] = 1
                turn += 1

            else:
                print("Please Enter a Value Between 0 and 8\n")
                continue 

    if checkwin(xstate , ostate):
        break

    if xstate.count(1) + ostate.count(1) == 9:
        print("GAME DRAW\nGAME OVER\n")
        break