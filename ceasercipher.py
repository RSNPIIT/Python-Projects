print('''
 ▗▄▄▖▗▄▄▄▖ ▗▄▖  ▗▄▄▖▗▄▄▄▖▗▄▄▖          ▗▄▄▖▗▄▄▄▖▗▄▄▖ ▗▖ ▗▖▗▄▄▄▖▗▄▄▖ 
▐▌   ▐▌   ▐▌ ▐▌▐▌   ▐▌   ▐▌ ▐▌        ▐▌     █  ▐▌ ▐▌▐▌ ▐▌▐▌   ▐▌ ▐▌
▐▌   ▐▛▀▀▘▐▛▀▜▌ ▝▀▚▖▐▛▀▀▘▐▛▀▚▖        ▐▌     █  ▐▛▀▘ ▐▛▀▜▌▐▛▀▀▘▐▛▀▚▖
▝▚▄▄▖▐▙▄▄▖▐▌ ▐▌▗▄▄▞▘▐▙▄▄▖▐▌ ▐▌        ▝▚▄▄▖▗▄█▄▖▐▌   ▐▌ ▐▌▐▙▄▄▖▐▌ ▐▌
                                                            
''')
print("UDEMY DAY 8 Python Project Given by @Angela Yu")
print("Welcome to Ramrup's Ceaser Cypher Project ")
def encoder(word,num):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    xq = ""
    for char in word:
        if char not in alphabet:  
            xq += char
        else:
            x = alphabet.index(char)
            sum_val = (x + num) 
            sum_val %= len(alphabet)
            xq += alphabet[sum_val]
    print(f"The Encoded Value is: {xq}")
def decoder(word,num):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    xq = ""
    for char in word:
        if char not in alphabet:  
            xq += char
        else:
            x = alphabet.index(char)
            sum_val = (x - num) 
            sum_val %= len(alphabet)
            xq += alphabet[sum_val]
    print(f"The Decoded Value is: {xq}")
attmpts = 0
while True:
    print("\n1.For Encoding\n2.For Decoding\n3.To Exit")
    choice = abs(int(input("Enter Your Choice Here : ")))
    if choice == 1:
        word = input("Enter Your Message Here : ").title()
        attmpts += 1
        num = abs(int(input("Enter the Value By What You wanna Shift To Encode the Message : ")))
        encoder(word,num)
    elif choice == 2:
        word = input("Enter Your Message Here : ").title()
        attmpts += 1
        num = abs(int(input("Enter the Value By which You Wanna Shift (or Rarther DeShift) to Decode the message : ")))
        decoder(word,num)
    elif choice == 3:
        print(f"It was fun having you , You've used this app for {attmpts} times")
        break
    else:
        print("Wrong Choice , Please Choose Something Else")
        continue