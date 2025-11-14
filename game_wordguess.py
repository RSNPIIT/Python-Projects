import random

easy_word = ['apple','train','tiger','money','india']
medium_word = ['python','monkey','planet','bottle','laptop']
hard_word = ['elephant','diamond','umbrella','computer','mountain']

print("Welcome to the Word Guess Game -- With a twist\n")
print("Enter Your Level :- \nEasy(E)\nMedium(M)\nHard(H or D)\n")
ch = input('Enter Your Level Here : ').strip().lower()

if ch == 'e':
    print('Your Choice : Easy')
    sel =random.choice(easy_word)

elif ch == 'm':
    print('Your Choice : Medium')
    sel =random.choice(medium_word)

elif ch == 'h' or ch == 'd':
    print('Your Choice : Hard \\ Difficult')
    sel =random.choice(hard_word)

else:
    print('Wrong Choice \nDefaulting to Easy\n')
    print('Defaulting Successful\n')
    sel = random.choice(easy_word)

attmpt = 0
game_on = True

while game_on:
    dis = ''
    attmpt += 1
    print('Lets Go\n')
    print('Guess the Word\n')
    gue = input('Make Your Guess Here : ').strip().lower()
    if gue == sel:
        game_on = False
        print(f'Correct : You have  guessed the word in {attmpt} attempts\n')
        break

        
    for el in range(len(sel)):
        if el < len(gue) and gue[el] == sel[el]:
            dis += gue[el]
            dis += ' '
        else:
            dis += '_'
            dis += ' '
    
    print(f'Hint : {dis}\n')

print('Game Over\n')
