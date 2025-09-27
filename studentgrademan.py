print("==> Welcome to Tux (C) Corp LMS Simplified Portal Sollutions <===")
print("Pre Given A Database and CRUD operations are to be performed")
student = {}
while True:
    print("You have the list of the Students in the Database what are you gonna do :\nAdd\nUpdate\nDelete\nDisplay")
    ch = input("Enter Your Choice as per the options Stated Above or Type 'exit' or 'quit' to exit the app : ").strip().lower()
    if ch == "add" :
        print(f"So you wanna add an entry to the database\n")
        name = input("Enter the name of the student : ").strip().lower()
        if name not in student:
            mar = abs(int(input("Enter the student's marks here : ")))
            student[name] = mar
            print(f"The Student {name} successfully added to the database with marks {mar}")
        else:
            print("The Student already exists in the Database , Adding to the Database Failed\n")
    elif ch == "update":
        print("So you wanna update the marks of the student in the database\n")
        name = input("Enter the name of the student : ").strip().lower()
        if name in student:
            mar = student[name]
            nmar = abs(int(input("Enter the student's new marks here : ")))
            student[name] = nmar
            print(f"The Student {name}'s marks has been successfully changed to {nmar} from {mar}")
        else:
            print("The Student Doesnt Exist in the Database , Updating Operation Failed\n")
    elif ch == "delete":
        print("So you wanna delete the student from the database\n")
        name = input("Enter the name of the student to be deleted : ").strip().lower()
        if name in student:
            del student[name]
            print(f"The Student {name} has been deleted from the database")
        else:
            print("No Such Student Exists in the Database ,Delete Operation Failed\n")
    elif ch == "display":
        if len(student) == 0:
            print("No such student exist in the Database As of Now")
        print(f"The Current Working Status of the Database is : {student}")
    elif ch == "exit" or ch == "quit" or ch == "e" or ch == "q":
        print("Congratulations the Database has been built perfectly so far")
        count = len(student)
        noun = "student" if count == 1 else "students"
        print(f"So far {count} {noun} are present in the Database")
        print("Exiting the App , Adios\n")
        break
    else:
        print("Your Choice is Wrong , Try Again")