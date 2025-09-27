import random
num = 0
lis_letters = [
    'a','b','c','d','e','f','g','h','i','j','k','l','m',
    'n','o','p','q','r','s','t','u','v','w','x','y','z',
    'A','B','C','D','E','F','G','H','I','J','K','L','M',
    'N','O','P','Q','R','S','T','U','V','W','X','Y','Z'
]
lis_numbers =['0','1','2','3','4','5','6','7','8','9']
lis_symbols =['@','_','&','#','^','%','*']
while True:
    b = abs(int(input("Enter the number of letters you want in your password : ")))
    c = abs(int(input("Enter the number of numbers (quite a tongue twister aint it) you want in your password : ")))
    d = abs(int(input("Enter the number of symbols you want in your password : ")))
    num += 1
    letter_num = random.randint(1,b)
    number_num = random.randint(1,c)
    symbol_num = random.randint(1,d)
    password_lis = []
    for i in range(1,letter_num + 1):
        password_lis.append(random.choice(lis_letters))
    for j in range(1,number_num + 1):
        password_lis.append(random.choice(lis_numbers))
    for k in range(1,symbol_num + 1):
        password_lis.append(random.choice(lis_symbols))
    random.shuffle(password_lis)
    password = ""
    for x in password_lis:
        password += x
    print(f"The Password is : {password}")
    print("Do you wanna continue ? (Y/N)")
    ch = input("Enter any key (letter or number) to continue or type N to quit : ").strip().lower()
    if ch == 'n':
        print(f"Total {num} number of Passwords Generated so far ")
        break
    else:
        continue
