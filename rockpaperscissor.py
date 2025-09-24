import random
print("--- Welcome to Pytho's Game Lab ---")
print("--- Developed by RSNPIIT Under GPL3 Licence ---")
lis = ["Rock","Paper","Scissor"]
user_score = 0
user_streak = 0
comp_score = 0
comp_streak = 0
while True:
    user_choice = input("Enter a choice here : ").strip().lower()
    computer_choice = random.choice(lis).lower()
    
    if user_choice == computer_choice:
        print(f"Your Choice = {user_choice} , Computer Choice is : {computer_choice}\n")
        print("Match Tied , Both at Same Case \n")

    elif user_choice == "rock":
        if computer_choice.lower() == "paper":
            print(f"Your Choice = {user_choice} , Computer Choice is : {computer_choice}\n")
            print("Paper Smashes Rock --- Computer Wins\n")
            comp_score += 1
            comp_streak += 1
            user_streak = 0
        else:
            print(f"Your Choice = {user_choice} , Computer Choice is : {computer_choice}\n")
            print("Rock Smashes Scissor --- You Win\n")
            user_score += 1
            user_streak += 1
            comp_streak = 0

    elif user_choice == "paper":
        if computer_choice == "scissor":
            print(f"Your Choice = {user_choice} , Computer Choice is : {computer_choice}\n")
            print("Scissor Cuts Paper --- Computer Wins\n")
            comp_score += 1
            comp_streak += 1
            user_streak = 0
        else:
            print(f"Your Choice = {user_choice} , Computer Choice is : {computer_choice}\n")
            print("Paper Wraps Rocks --- You win\n")
            user_score += 1
            comp_streak = 0
            user_streak += 1

    elif user_choice == "scissor" or user_choice.strip() == "scissors" :
        if computer_choice == "rock":
            print(f"Your Choice = {user_choice} , Computer Choice is : {computer_choice}\n")
            print("Rock Breaks Scissors --- Computer Wins\n")
            comp_score += 1
            comp_streak += 1
            user_streak = 0
        else:
            print(f"Your Choice = {user_choice} , Computer Choice is : {computer_choice}\n")
            print("Scissor Shreds Paper --- You Win\n")
            user_score += 1
            comp_streak = 0
            user_streak += 1

    elif user_choice == "quit" or user_choice == "exit" :
        print("--Thankyou for playing the Game built by using only the FOSS tools---\n")
        print(f"The score is {comp_score} for Computer and {user_score} for you\n")
        print(f"The current streak is : {comp_streak} for Computer and {user_streak} for You\n")
        if comp_score > user_score :
            print("Computer is Ahead in the ScoreBoard")
        elif comp_score == user_score :
            print("Cant Decide since Both Win tallies are same")
        else:
            print("User is Ahead in the ScoreBoard")
        break

    else:
        print("Your Choice is Wrong , Kindly Enter a Valid Game Value\n")