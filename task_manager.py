import os as o
import time as ti

class Task:
    def __init__(self , title):
        self.title = title
        self.complete = False

    def mark_completed(self):
        self.complete = True

    def __str__(self):
        status = "Done" if self.complete else "Pending"
        return f"{self.title} | {status}"

class TaskMan:
    def __init__(self):
        self.tasks = []

    def add_task(self , title):
        task = Task(title)
        self.tasks.append(task)
        print(f"Task Added successfully\n")
    
    def view_task(self):
        if not self.tasks:
            print("No Tasks Found\n")
            return
        print("Your Tasks:\n")
        for idx , tasks in enumerate(self.tasks):
            print(f"{idx} -> {tasks}")
    
    def complete(self , task_number):
        if 1 <= task_number <= len(self.tasks):
            self.tasks[task_number - 1].mark_completed()
            print("Task Marked as complete\n")
        else:
            print("Invalid task number\n")
    
    def delete(self , task_number):
        if 1 <= task_number <= len(self.tasks):
            removed_tas = self.tasks.pop(task_number - 1)
            print(f"Removed the Task {removed_tas.title} successfully !")
        else:
            print("Invalid task number\n")


def main():
    ATTMPT = 0

    man = TaskMan()
    while True:
        ATTMPT += 1
        print("-----Mini OOPS Task Man------")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Complete Task")
        print("4. Delete Task")
        print("5. Exit")

        try:
            ch = abs(int(input("Enter the Choice Here :-> ")))

        except (KeyboardInterrupt , EOFError) as kb:
            print("\nNot Allowed to perform this by user\n")
            continue
        
        except ValueError as v: 
            print("Error\nNon Integer Values are given\nPlease re-enter\n")
            continue
        
        except OverflowError as ov:
            print("Error\nOverFlow Error due to Interpreter occurred\nPlease re-run\n")
            ti.sleep(1)
            o.system('cls' if o.name == 'nt' else 'clear')

        except Exception as e:
            print(f"Some other Exception Occurred\n{e}\nPlease Re-Enter")
            continue
        
        else:
            if ch == 1:
                title = input("Enter Task Title Here :-> ").strip().lower()
                man.add_task(title)
            
            elif ch == 2:
                man.view_task()
            
            elif ch == 3:
                man.view_task()
                try:
                    tn = abs(int(input("Enter the Task Number You wish to complete :-> ")))
                
                except (KeyboardInterrupt , EOFError) as kb:
                    print("\nNot Allowed to perform this by user\n")
                    continue
        
                except ValueError as v: 
                    print("Error\nNon Integer Values are given\nPlease re-enter\n")
                    continue

                except Exception as ex:
                    print(f"Some other Exception Occurred\n{e}\nPlease Re-Enter")
                    continue
                
                else:
                    man.complete(tn)
            
            elif ch == 4:
                man.view_task()
                try:
                    tn = abs(int(input("Enter the Task Number You wish to delete :-> ")))
                
                except (KeyboardInterrupt , EOFError) as kb:
                    print("Not Allowed to perform this by user\n")
                    continue
        
                except ValueError as v: 
                    print("Error\nNon Integer Values are given\nPlease re-enter\n")
                    continue

                except Exception as ex:
                    print(f"Some other Exception Occurred\n{e}\nPlease Re-Enter")
                    continue
                
                else:
                    man.delete(tn)

            elif ch == 5:
                print(f"Exiting Program\nApp Used For {ATTMPT} times\nPlease come back again\n")
                break

            else:
                print("\nThe Choice is invalid and broken\nI request you to please enter the choice again\n")

    print("🄯 RSNPIIT (Ramrup Satpati) IIT Madras\nReleased under the GNU GPLv3 License")

if __name__ == "__main__": 
    main()