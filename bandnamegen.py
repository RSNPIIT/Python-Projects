print("UDEMY COURSE BY ANGELA YU DAY 1")
print("Band Name Generator with Ramrupian Twist")
n = 0
while True:
    name = input("Enter your name here : ")
    pet = input("Enter the name of your pet here : ")
    bname = name + " " + pet
    print(f"Your Band name could be : {bname}")
    n += 1
    print("--Type any key to continue or quit if you wanna stop--")
    ch = input("Enter your choice here : ").strip().lower()
    if ch == 'quit':
        print("Exiting the Bang Generator Apk")
        print(f"The Number of possible names generated are : {n}")
        break