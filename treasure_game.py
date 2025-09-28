#ReBuilt ReImagined Like Never Before
import random
print(r'''

                       []
                       ||
                       ||
                       ||
                       ||
                       ||
                       ||
                       ||
                       ||
           [:::::::::::||
                       ||
         _._._._       ||
         I.____________||__________/.___
       ..I|""""""""""""  """"""""""``""/
       I I|                           /
      /  ||________........__________/
     |   |         |      |
     |___|         |      |       
                    \____/
''')
print("Day 3 of The UDEMY 100 Days 100 Projects Challenge by Dr. Angela Yu")
print("Welcome to the Adeventure Island Game in Python , Made by Ramrup Satpati (C) Tux Corp (Subset of Linux Foundation albeit on PSF licence) and IITM")
score = 0
while True:
    print("Your Goal is to Find the treasure --- Lets See Soldier whether you're worth it or not")
    print("You are at a crossroad -- Two choices Left or Right Which Path --")
    ch = input("Enter your Choice Fast (L/R) : ").strip().lower()
    if ch == "l":
        print("You find yourself next to a Lake --- Do you wanna Swim (s)or Craft (c) a Makeshift Raft")
        c = input("Make Your Choice Fast : ").strip().lower()
        if c == 's':
            print("You Drowned in the Deep Waters")
            print("Game Over")
            break
        elif c == 'c':
            print("Congratulations You Built a Raft , Now You Sail")
            score += 1
            print(--"The Island is in the midde of the lake , You enter it--")
            print("You Find three doors : Gold (G) , Silver (S) , Ruby (R)")
            dr = input("Make you Door Choice Fast and Quick : ").strip().lower()
            if dr == 'g':
                print("The Room was caught in fire ")
                print("Game Over")
                break
            elif dr == 's' :
                print("Aah Unfortunately it was a trap door full of explosive ")
                print("Game Over")
                break
            elif dr == 'r':
                score += 1
                print("Yaey you successfully located the treasure\n")
                print(f"You Win having done {score} correct options so far\n")
                break
            else :
                print("Wrong Choice --- Timeout --- Your HP Ran out")
                print("Game Over")
                break
        else :
            print("Wrong Choice --- Timeout --- Your HP Ran out")
            print("Game Over")
            break
    elif ch == 'r':
        score += 1
        print("You find an abandoned hut. You enter (cause you are broke and out of options lol).")
        print("---Suddenly a Wild Boar Attacks You! You have to fight---")

        # Boar randomly chooses its move: 'f' = fist, 'k' = kick
        baction = random.choice(['f', 'k'])

        yaction = input("Press (f) for Fist attack or (k) for Kick attack: ").strip().lower()

        # ---------- Boar fight ----------
        if yaction == 'f':
            # Player used fist → always lose
            print("Boar Attacked You Hard")
            print("Boar Wins")
            print("GAME OVER")
            break

        elif yaction == 'k':
            # Kick beats fist, but kick vs kick → boar wins
            if baction == 'f':
                print("Boar Chooses Fist Attack")
                print("You Smashed the Boar Hard")
                print("You Win")
                score += 1

                # ---------- Door choice after victory ----------
                print("Congratulations! You defeated the boar.")
                print("Now you find three doors — choose wisely.")
                cg = input("Choose a Door (R for Red, G for Green, B for Blue): ").strip().lower()

                if cg == 'r':
                    print("You get a slap and find out it was a dream and you overslept.")
                    print("You didn’t lose — yet. GAME OVER")
                    break
                elif cg in ('g', 'b'):
                    print("You located the treasure in an alternate fashion!")
                    score += 1
                    print(f"You Win. So far you made {score} correct choices.")
                    break
                else:
                    print("Timeout or wrong choice.")
                    print("Game Over")
                    break

            else:  # boar also kicks
                print("Both of you kicked, but the boar overpowers you.")
                print("Boar Wins")
                print("GAME OVER")
                break

        else:
            print("Timeout or invalid choice.")
            print("Game Over")
            break

    else:
        print("Wrong Choice --- Timeout --- Your HP Ran out")
        print("Game Over")
        break