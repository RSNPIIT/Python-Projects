import random
print(r"""
                                                   
., ,        ]                .m                 
]\ [. . .mm ]m,  m,  ,m     .` `. .  m,  m,  m, 
]],[] ] ]]] ]`T ]`]  P `    ] .,] ] ]`] ] ' ] ' 
] [[] ] ]]] ] ] ]""  [      ]  [] ] ]""  "\  "\ 
] ]['mT ]]] ]bP 'b/  [       \m`'mT 'b/ 'm/ 'm/ 

""")
print("Welcome to Ramrup's Number Guessing Game")
attmpt = 0

def compare(num,val):
        if num > val:
            print("Too High")
        elif num < val:
            print("Too Low")
        else:
            print(f"Yaey You Got it , The number is {val}")

game_play = True

while game_play:
    attmpt += 1
    if attmpt % 2 == 0 and attmpt % 6 != 0:
        print("Приветствую, друзья")
    elif attmpt % 3 == 0:
        print("안녕 친구들")
    else:
        print("नमस्ते दोस्तों")
    game_over = False
    value = random.choice(range(1, 101))
    lives = 0
    diff = input("Enter the Difficulty You wanna Play (Easy / Hard) : ").strip().lower()
    if diff == 'easy':
        lives += 10
    elif diff == 'hard':
        lives += 5
    else:
        print("Wrong Choice --- Redirecting to Easy \nRedirect Successful")
        lives += 10

    while not game_over:
        print("\n" + "="*30)
        print(f"-------------You have {lives} chances to guess the Correct answer-----------\n")
        print("HINT : The Numbers Are From 1 to 100 So You Have exactly 1/100 ~ 0.01 Probability of Choosing the Correct Number")
        guess = int(input("Enter Your Guessed Number Here : "))
        compare(guess,value)
        if guess != value:
            lives -= 1
            if lives > 0:
                print(f"Oops You Lose one Life , Dont Worry You Have {lives} attempts remaining")
            else:
                print("*"*30)
                print(f"------Oops looks like you ran outta lives------\n-------The Number was : {value} all this time ----------")
                print(f"---------All this time the number was {value}---------")
                game_over = True
                break
        else:
            print("Yaey You Won the Game , Congratulations Keep it Up")
            game_over = True
            break
    
    user_choice = input("Do You Wanna Play Again (Any Letter key/N) : ").strip().lower()
    if user_choice == 'n':
        print("कोई बात नहीं वापस जरूर आना। \nअभी बार केवल तरक्की की वार")
        print(f"So far You have Used the App for {attmpt} time(s) ,\nDo Come Back")
        game_play = False
        break
    else:
        print("="*30)
        continue
