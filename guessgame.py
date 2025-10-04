import random
print("Welcome to Ramrup's Number Guessing Game")
print("How the Game works is : You Enter a Range Upto Which My Program Will Randomly Generate a Number , And then You enter the maximum number of attempts")
print("Note -- You enter the maximum number of attempts , then my program will randomly give you how many attempts you actually get ")
times = 0
flag = True
while flag:
    ra = abs(int(input("Enter the Upper Limit of Random number generation : ")))
    num = random.randint(1,ra)
    x = abs(int(input("Enter the Maximum Limit of Attempts (Should be greater than 2) : ")))
    n = random.randint(2,x)
    print(f"You get {n} attempts this time , Good Luck")
    correct = False
    times += 1
    i = 1
    while i <= n:
        attmt = int(input(f"Enter Your {i}th Guess Here : "))
        i += 1
        if attmt == num:
            print(f"Congratulations You Guessed the Number in {i} tries")
            correct = True
            break
        else:
            print("No Sadly that's Not it , Please Re Enter")
            continue
    if correct == False:
        print("Umm Well it looks like , You Exhausted all your lives")
        print(f"< The Number was {num} all this time , Understood >")
        print("Wanna Rematch --- Note , the Numbers and the Guesses will change ")
        ch = input("Enter Your Choice Here (Any Key for Yes and a N for a No): ").strip().lower()
        if ch == 'n':
            print(f"So far this has been attempted by you for {times} times")
            flag = False
        else:
            continue
    elif correct == True:
        print("Well You're A Pro At It , Great ")
        print("Thank You Please Visit Again Soon")
        break
    