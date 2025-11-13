import random

e_w = ['cat','sun','map','box','dog']
m_w = ['apple','river','chair','plant','sound']
h_w = ['victory','balance','kingdom','quantum','journey']

def game(lst):
    word = random.choice(lst)
    attmpt = 0
    hnt = ''
    g_l = []

    for _ in range(len(word)):
        hnt += '_'
        hnt += ' '

    print(f"Your Word is : {hnt} \nCLUE : It's a {len(word)} lettered word\n")
    lives = 6
    
    game_is_on = True
    while game_is_on:
        attmpt += 1
        print(f"\nSo Let's Start the Game - \nWARNING :You have {lives} lives left\n")

        guess = input("Enter a letter here : ").strip().lower()
        dis = ''

        if guess in g_l:
            print('You already have Guessed this Letter \nNo Lives Lost')
            continue
        
        elif guess not in g_l and guess in word:
            g_l.append(guess)

        if guess not in word:
            lives -= 1
            print(f'You Lose one Life \nYou have {lives} lives left \n')
            if lives == 0:
                game_is_on = False
                print(f"Aah I'm Sorry You Run out of Lives \nThe Word was {word} all along \nGAME OVER")
                break
            
        for ch in word:
            if ch in g_l:
                dis += ch
                dis += ' '
            
            else:
                dis += '_'
                dis += ' '
        
        print('Current Status of the Game is :\n')
        print(f'{dis} \n')

        if '_' not in dis:
            game_is_on = False
            print(f'You Guessed The Word Successfully \nTotal {attmpt} attempts taken\n')
            break

        else:
            continue

def main():
    print('Welcomr to the Word Guessing Game by Ramrup Satpati (RSNPIIT)\n')

    print("RULES :- It's Simple A word will be Given and You have to Guess it in 6 attempts Othetrwise You'll Fail \nYou Have 3 Variying Difficulty Choices :- Easy \\ Medium \\ Hard \n")
    ch = input('Make Your Choice :- Enter E for Easy ,M for Medium and H (or D) for Hard : ').strip().lower()

    if ch == 'e':
        game(e_w)
    
    elif ch == 'm':
        game(m_w)
    
    elif ch == 'h' or ch == 'd':
        game(h_w)
    
    else:
        print("Wrong Choice \n")
        print('Redirecting to Medium \n')
        print('Redirect Successful \n')
        game(m_w)

main()