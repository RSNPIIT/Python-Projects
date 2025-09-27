print("---Welcome to Tux Corp Contact Book App ---")
print("===> Made by Ramrup Satpati In Bharat <===")
contact = {}
while True:
    print("Enter your Choice As to what you're gonna do as per the options given ")
    print("1. Create New Contact\n2. View Contact\n3. Update New Contact\n4. Delete Contact\n5. Search Contact\n6. Count Contact List\n7. Exit")
    ch = abs(int(input("Enter your Choice as per the above menu options : ")))
    if ch == 1:
        print("So You Wanna Add a New Contact\n")
        con = input("Enter the Contact Name here : ").strip().lower()
        num = abs(int(input(f"Enter the Contact Number of {con} here : ")))
        if len(str(num)) == 10:
            contact[con] = num
            print(f"The Contact {con}'s Number has been saved successfully ")
        else:
            print(f"The Contact {con}'s Number cannot be added because the phone number has digits unequal to 10")
    elif ch == 2:
        print("So You Wanna View a Contact \n")
        con = input("Enter the Contact Name you wish to view here : ").strip().lower()
        if con in contact:
            print("💡Ahh Yes The Contact Number Exists")
            print(f"The Contact Number of {con} is : {contact[con]}")
        else :
            print(f"No Such Contact Exists as of {con}")
    elif ch == 3:
        print("So You Wanna Update a Contact \n")
        con = input("Enter the Contact you wish to Update Here : ").strip().lower()
        if con in contact :
            old_num = contact[con]
            new_num = abs(int(input("Enter the New Contact Number Here : ")))
            if len(str(new_num)) == 10:
                contact[con] = new_num
                print(f"The Conatct Number of {con} has been successfully Changed")
            else:
                print("The Length of the New Contact Number is not 10 -- Updatation Failed--")
                print(f"The Contact Number of {con} remains {old_num} , as it is ")
        else:
            print("No Such Contact Found in the App")
    elif ch == 4:
        print("So You Wanna Delete a Contact \n")
        if len(contact) == 0:
            print("LogBook Empty can't Delete")
        else:
            con = input("Enter the Contact Name Here : ").strip().lower()
            if con in contact :
                del contact[con]
                print(f"Contact {con} has been deleted successfully")
            else:
                print(f"Contact {con} doesnt exist in the Log , Deletion Prevented")
    elif ch == 5:
        print("So You Wanna Search a Contact \n")
        con = input("Enter the Contact Name Here : ").strip().lower()
        if con in contact:
            print("The Contact Exists in the App")
        else :
            print("No Such Contact Exists")
    elif ch == 6:
        print("So You Wanna Count the Contact List \n")
        if len(contact) == 0:
            print("You Havent Added any Contacts Yet")
        else:
            print(f"The Number of Contacts in the app is : {len(contact)}")
    elif ch ==  7:
        print("Thankyou for using our App , It will be very helpful for us if you kindly leave a constructive Review regarding the same \n")
        print("--Exiting --- Adios")
        break
    else:
        print(f"Kindly Make a choice from 1 to 7 as per requirement , This Choice {ch} is wrong")
        continue