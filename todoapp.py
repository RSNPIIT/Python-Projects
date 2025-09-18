#Menu Driven Programs Revision
def todo():
    tasks = []
    print("--Welcome to Python Task Manager App--")
    print("--App Created by (C)Pytho Corp which is a subsidiary of Tux App Corp.---")
    num = abs(int(input("Enter the number of Tasks you wanna complete :")))
    for i in range(1,num + 1):
        task = input(f"Enter task {i} here : ")
        tasks.append(task.strip().lower())
    print("The Tasks List has been Created Successfully")
    while True:
        print("--Select your Choice As to what you're gonna do--")
        print("1 . Add any task\n2 . Delete any task\n3 . Display the current tasks\n4 . Exit the app")
        choice = abs(int(input("Enter the task here : ")))
        if choice == 1:
            new_task = input("Enter New Task Here : ")
            if new_task.strip().lower() in tasks :
                print(f"The task {new_task.strip()} already exists . Please enter some other task ")
            else:
                tasks.append(new_task.strip().lower())
                print(f"The Task {new_task.strip()} has been added to your app")
        elif choice == 2:
            del_task = input("Enter the task you wanna delete : ")
            if del_task.strip().lower() in tasks:
                tasks.remove(del_task.strip().lower())
                print(f"The task {del_task.strip()} has been deleted")
            else:
                print(f"The task {del_task} doesn't exist in the list . Please add it first ")
        elif choice == 3:
            print("The Current status of the app is :",tasks)
        elif choice == 4:
            print("--Exiting the App Please come back later --")
            break
        else:
            print(" Wrong Choice \n Operation Terminated \n Choose any number from  1 to 4")
#Function Execution Here
todo()