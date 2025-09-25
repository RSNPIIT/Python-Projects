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
print("Your Goal is to Find the treasure --- Lets See Soldier whether you're worth it or not")
print("You are at a crossroad -- Two choices Left or Right Which Path --")
ch = input("Enter your Choice Fast : ").strip().lower()
if ch == "left":
    print("You find yourself next to a Lake --- Do you wanna Swim (s)or Craft (c) a Makeshift Raft")
    c = input("Make Your Choice Fast : ").strip().lower()
    if c == 's':
        print("You Drowned in the Deep Waters")
        print("Game Over")
        exit()
    elif c == 'c':
        print("Congratulations You Built a Raft , Now You Sail")
        print(--"The Island is in the midde of the lake , You enter it--")
        print("You Find three doors : Gold (G) , Silver (S) , Ruby (R)")
        dr = input("Make you Door Choice Fast and Quick : ").strip().lower()
        if dr == 'g':
            print("The Room was caught in fire ")
            print("Game Over")
            exit()
        elif dr == 's' :
            print("Aah Unfortunately it was a trap door full of explosive ")
            print("Game Over")
            exit()
        elif dr == 'r':
            print("Yaey you successfully located the treasure\n")
            print("You Win\n")
            exit()
        else :
            print("Wrong Choice --- Timeout --- Your HP Ran out")
            print("Game Over")
            exit()
    else :
        print("Wrong Choice --- Timeout --- Your HP Ran out")
        print("Game Over")
        exit()
elif ch == 'r':
    print("You find an abandoned hut with a strange concoction")
    print("Do you drink the concoction or not (Y/N)")
    cf = input("Enter the Choice Here : ").strip().lower()
    if cf == 'y':
        print("You get a slap from your mom ,Did you not know never drink or eat strange things , It was all a dream")
        print("Game Techically Not Over but You Lost")
        exit()
    elif cf == 'n':
        print("Your HP ran out")
        print("Game Over")
        exit()
    else:
        print("Wrong Choice --- Timeout --- Your HP Ran out")
        print("Game Over")
        exit()
else:
    print("Wrong Choice --- Timeout --- Your HP Ran out")
    print("Game Over")
    exit()