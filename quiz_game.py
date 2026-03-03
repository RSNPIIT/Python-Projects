import time as ti
import os as o

questions = (
    "How Many Elements in the Periodic Table ? " , 
    "Which animal lays the largest eggs ? " , 
    "What's the Most Abundant Gas in the Earth's Atmosphere ? " ,
    "How many bones are there in the human body ? ",
    "What's the hottest planet in the solar system ? "
)

options = (
    ("A = 116" , "B = 118" , "C = 119" , "D = 120") , 
    ("A = Ostrich" , "B = Bald Eagle" , "C = Chimera" , "D = Arctic Tern") , 
    ("A = Hydrogen" , "B = Nitrogen" , "C = Carbon Dioxide" , "D = Oxygen") , 
    ("A = 201" , "B = 202" , "C = 207" , "D = 206"),
    ("A = Mercury" , "B = Jupiter" , "C = Venus" , "D = Mars")
    )

answers = ("B" , "A" , "B" , "D" , "C")
guesses = []
score = 0
q_num = 0

print("Welcome to Ramrup's Quiz Game ----- \nCopyleft Tux Corp ")
for q in questions:
    print("="*60)
    print(f'{q}')
    for opt in options[q_num]:
        print(f'{opt}')
    print("="*60)
    try:
        gues = input("Enter A/B/C/D here :- ").strip().upper()
    except (KeyboardInterrupt , EOFError) as kb:
        print("\nSkipping ......\n")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')
        exit()
    guesses.append(gues)
    if gues == answers[q_num]:
        score += 1
        print("Yup Its Correct --Great")
    else:
        print(f"Aah Unfortunately its Wrong\n{answers[q_num]} is the correct answer")
    
    q_num += 1

acc = round((score / len(answers)) * 100 , 3)
print(f"Summary -> \nScore -> {score} // {len(answers)} \nAccuracy -> {acc}%\n")
if score >= 3:
    print("\nWohoo youre a star.......")
elif score == 0:
    print("\nDont be (D3)M*+!v@t3d \nL3+s Go again after a through revision")