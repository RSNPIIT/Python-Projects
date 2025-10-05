import random
print(r"""
 ____ ___                         ________                       
|    |   \______     ___________  \______ \   ______  _  ______  
|    |   /\____ \   /  _ \_  __ \  |    |  \ /  _ \ \/ \/ /    \ 
|    |  / |  |_> > (  <_> )  | \/  |    `   (  <_> )     /   |  \
|______/  |   __/   \____/|__|    /_______  /\____/ \/\_/|___|  /
          |__|                            \/                  \/ 

""")
score = 0
attmpt = 0
data = [
    {
        'name': 'Vin Diesel',
        'followers': 103000,
        'country': 'United States',
        'occupation': 'Actor'
    },
    {
        'name': 'Shah Rukh Khan',
        'followers': 135000,
        'country': 'India',
        'occupation': 'Actor'
    },
    {
        'name': 'Taylor Swift',
        'followers': 282000,
        'country': 'United States',
        'occupation': 'Singer'
    },
    {
        'name': 'Cristiano Ronaldo',
        'followers': 1000000,
        'country': 'Portugal',
        'occupation': 'Footballer'
    },
    {
        'name': 'Emma Watson',
        'followers': 73000,
        'country': 'United Kingdom',
        'occupation': 'Actor'
    },
    {
        'name': 'Elon Musk',
        'followers': 227000,
        'country': 'United States',
        'occupation': 'Entrepreneur'
    },
    {
        'name': 'Virat Kohli',
        'followers': 274000,
        'country': 'India',
        'occupation': 'Cricketer'
    },
    {
        'name': 'Narendra Modi',
        'followers': 98000,
        'country': 'India',
        'occupation': 'Politician'
    },
    {
        'name': 'Ramrup Satpati (RSNPIIT)',
        'followers': 3500,   
        'country': 'India',
        'occupation': 'Python Programmer'
    }
]
val = random.choice(data)
def correct_format(xal):
    return (f"{xal['name']} a(n) {xal['occupation']} from {xal['country']}.")

def comparator(ch,A,B):
    if ch == 'a':
        if A['followers'] > B['followers']:
            return True
        else:
            return False
    elif ch == 'b':
        if A['followers'] < B['followers']:
            return True
        else:
            return False
    else:
        return None 
is_game_over = False
while not is_game_over:
    attmpt += 1
    account_a = random.choice(data)
    account_b = random.choice([x for x in data if x != account_a])
    print("\n" + "="*60)
    print(f"| Current Score: {score} | Attempt: {attmpt} |")
    print("="*60)
    print(f"\nCompare A : {correct_format(account_a)}")
    print("\n" + "-"*15 + " VERSUS " + "-"*15 + "\n")
    print(f"Compare B : {correct_format(account_b)}")
    print("\n" + "="*60)
    
    # Get user guess
    guess = input("Enter Who Has More Followers? Enter A or B: ").strip().lower()
    val = comparator(guess,account_a,account_b)
    
    print("\n" + "="*60)

    # Check game result
    if val == True:
        print(">>> CHOSEN CORRECTLY! Cheers, You Scored a Point! <<<")
        score += 1
        print(f"So far {score} questions have been answered successfully")
        print("="*60)
        continue
    else:
        print("============================================================")
        score += 0
        print("--------Sadly the Answer is Not Correct-------------")
        print(f"App used for {attmpt} times")
        is_game_over = True
        break