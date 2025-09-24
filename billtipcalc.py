print("Day 2 of Udemy 100 days Python Projects Bootcamp")
print("Doing the said projects with minor twists by Ramrup Satpati (C) IITM ")
count = 0
while True :
    bill = abs(float(input("Enter the Bill Amount Here : ")))
    tip = abs(float(input("Enter the amount numerically how much tip you wanna give (in % by default) : ")))
    people = abs(int(input("Enter the number of people you're gonna split with : ")))
    amt_person = round((bill + bill * (0.01*tip))/people , 2)
    print(f"Your amount payable per person is : {amt_person}\n")
    count += 1
    print("--Type any key to continue or a N to quit--")
    choice = input("Enter your Choice here (Do You wanna continue (Y/N)) : ").strip().lower()
    if choice == 'n':
        print(f"So far {count} bills have been generated successfully")
        print("Thankyou for Using the Tip Generator App")
        break
