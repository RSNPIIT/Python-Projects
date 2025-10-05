import random
print(r"""
 _   _                                         
| | | |                                        
| |_| | __ _ _ __   __ _ _ __ ___   __ _ _ __  
|  _  |/ _` | '_ \ / _` | '_ ` _ \ / _` | '_ \ 
| | | | (_| | | | | (_| | | | | | | (_| | | | |
\_| |_/\__,_|_| |_|\__, |_| |_| |_|\__,_|_| |_|
                    __/ |                      
                   |___/                       
""")
word_list = ["Elephant", "Capsuley", "Overcome", "Driftwood",
         "Bravados", "Landlord", "Overkill", "Junction",
         "Pastoral", "Velocity"]
stages = [
    """
  +---+
  |   |
      |
      |
      |
      |
=========
""",
    """
  +---+
  |   |
  O   |
      |
      |
      |
=========
""",
    """
  +---+
  |   |
  O   |
  |   |
      |
      |
=========
""",
    """
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========
""",
    """
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========
""",
    """
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========
""",
    """
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========
"""
]
word = random.choice(word_list).strip().lower()
correct_l = []
guessed_l = []
d = ""
for _ in range(len(word)):
    d += '_'
print(f"*********Your Word is : {d}***************\n**********HINT : IT IS AN 8 LETTERED WORD*********")
lives = 6
game_over = False
while not game_over:
    print(f"*************{lives}/6 LIVES***********")
    guess = input("Enter Your Guessed Letter Here : ").strip().lower()
    if guess in guessed_l:
        print(f"⚠️ You already guessed the letter '{guess}'. Try a new one! (No life lost)")
        print(stages[6-lives])
        continue # Skip the rest of the loop and ask for new input
    guessed_l.append(guess)
    
    display = ""

    for letter in word:
        if guess == letter:
            display += letter
            correct_l.append(letter)
        elif letter in correct_l:
            display += letter    
        else:
            display += '_'
    print(display)
    
    if guess not in word:
        lives -= 1
        print(f"Aah , You Lose One Life , You have {lives} left")
        if lives == 0:
            game_over = True
            print(f"***************** IT WAS {word} ALL THIS TIME / YOU LOSE *****************")
            print("Sorry You Lose , You Ran Out of Lives")
    elif '_' not in display:
        game_over = True
        print("You Win")
    elif guess in correct_l:
        lives -= 0
        #print("You have Already Guessed the Word , Guess Anything Else")
    print(stages[6-lives])