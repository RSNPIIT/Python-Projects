print("Beta Version Built By Ramrup (C) IITM")
print("Welcome to my Quiz Game Apk")
print("Enter your Name or Alias to proceed further")
name = input("Enter your Name or Alias : ")
ch = input(f"Hello {name}, nice to meet you , Do you wanna play the quiz game ? (Y/N): ").strip().lower()
score = 0
attmpt = 0
if ch == 'n':
    print(f"Nevertheless {name} We wish you come back again soon , Adios")
    exit()
while True :
    ascore = 0
    astreak = 0
    print("Question 1")
    ans1 = input("What's the Full Form of CPU ? : ").lower()
    if ans1 == 'central processing unit':
        ascore += 1
        score += 1
        astreak += 1
        print("Correct Answer\n")
    else:
        astreak = 0
        print("Incorrect Answer\n")

    print("Question 2")
    ans2 = input("What's the Full Form of GPU ? : ").lower()
    if ans2 == 'graphics processing unit':
        ascore += 1
        score += 1
        astreak += 1
        print("Correct Answer\n")
    else:
        astreak = 0
        print("Incorrect Answer\n")

    print("Question 3")
    ans3 = input("What's the Full Form of RAM ? : ").lower()
    if ans3 == 'random access memory':
        score += 1
        ascore += 1
        astreak += 1
        print("Correct Answer\n")
    else:
        astreak = 0
        print("Incorrect Answer\n")

    print("Question 4")
    ans4 = input("What's the Full Form of ROM ? : ").lower()
    if ans4 == 'read only memory':
        score += 1
        ascore += 1
        astreak += 1
        print("Correct Answer\n")
    else:
        astreak = 0
        print("Incorrect Answer\n")
    attmpt += 1
    temp = astreak

    print(f"Congrats {name} your Score at the end of the Round is {ascore} points ")
    print(f"Congrats {name} You have {astreak} no of streaks of correct answers ")
    print(f"Congrats {name} you Answered {(ascore/4)*100}% questions correctly ")
    if ascore == 4:
        print("Outstanding Effort")
    elif ascore == 3:
        print("Almost There ,Keep Trying")
    elif ascore == 2:
        print("Close but no cigar")
    elif ascore == 1:
        print("Keep Grinding You'll make it in time , I trust you")
    else :
        print("Don't be demotivated , Failure is the stepping stone to success")
    
    print(f"Hey {name} wannna stop or play more ?\n")
    var = input("Enter your choice (Type any key for continuing or N if you wanna quit) : ").strip().lower()
    if var == 'n':
        print(f"Thankyou for playing the quiz and indeed it's a pleasure to meet you {name}")
        print(f"The number of attempts taken are : {attmpt}")
        print(f"The total score accumulated over all rounds are : {score} points")
        print(f"The percentage or average accuracy is {round((score/(attmpt*4))*100, 2)} points")
        print(f"Finally over all rounds you have {temp} number of Correct Answers in a Row")
        break
    else:
        continue