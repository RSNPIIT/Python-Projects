import time as ti
import os as o
import sys as s

# Static Variables
stud = {}
SEL = 'y'
FILE = 'file.txt'
MODE = 'w'
attmpt = 0

# As we are using the write mode we need to save earlier transaction safely so as to avoid data loss
if o.path.exists(FILE):
    with open(FILE) as f:
        for line in f:
            try:
                parts = line.strip().split('|')
                name = parts[0].split('->')[1].strip()
                mars = int(parts[1].split('->')[1].strip())
                stud[name] = mars
            except Exception as ex:
                continue

# Function to apply DRY - Don't repeat yourself principle
def save_data():
    with open(FILE, 'w') as fl:
        for key, val in stud.items():
            fl.write(f"Student Name -> {key} | Marks -> {val}\n")

while True:
    attmpt += 1
    
    print("------- STUDENT MANAGER APP ----------\nOptions ->")
    print("1. -> Add Students")
    print("2. -> View Students' Marks")
    print("3. -> Delete Passouts")
    print("4. -> Exit the appication")

    try:
        ch = abs(int(input("Enter your choice here :-> ")))
    except (KeyboardInterrupt , EOFError) as e:
        print("\nNot Allowed to do this\nIllegal Exit ignored")
        continue
    except ValueError as v:
        print("Not Allowed at all\nPlease enter Integer Values\n")
        continue
    else:
        if ch == 1:
            name = input("Enter the student's name here : ").strip().title()
            if name not in stud:
                try:
                    mar_st = int(input(f"Enter {name}'s marks here :-> "))

                    if not (0 <= mar_st <= 100):
                        print("Marks must be between 0 and 100\n")
                        continue

                except (KeyboardInterrupt , EOFError) as e:
                    print("\nNot Allowed to do this\nIllegal Exit ignored")
                    continue
                except ValueError as v:
                    print("Not Allowed at all\nPlease enter Integer Values\n")
                    continue
                except OverflowError as ov:
                    print("Wrong Input Please Enter Again\nSuch Long values Are not alowed")
                    continue
                except Exception as ex:
                    print(f"Some Error Occurred here\n{ex}")
                    continue
                else:
                    print(f"Added the student {name} in the database\n")
                    stud[name] = mar_st

            else:
                print(f"\nThe student {name} already exists\n")
                yn = input("Wanna Update the marks (y/n) :-> ").strip().lower()
                if yn == SEL:
                    try:
                        mar_st = int(input(f"Enter {name}'s marks here :-> "))

                        if not (0 <= mar_st <= 100):
                            print("Marks must be between 0 and 100\n")
                            continue
                    except (KeyboardInterrupt , EOFError) as e:
                        print("\nNot Allowed to do this\nIllegal Exit ignored")
                        continue
                    except ValueError as v:
                        print("Not Allowed at all\nPlease enter Integer Values\n")
                        continue
                    except OverflowError as ov:
                        print("Wrong Input Please Enter Again\nSuch Long values Are not alowed")
                        continue
                    except Exception as ex:
                        print(f"Some Error Occurred here\n{ex}")
                        continue
                    else:
                        print(f"Added the student {name} in the database\n")
                        stud[name] = mar_st
                else:
                    print(f"Marks of the student named {name} kept as is\n")
                    
        elif ch == 2:
            name = input("Enter the student's name here : ").strip().title()
            if name in stud:
                mar = stud[name]
                stat = 'Pass' if mar >= 40 else 'Fail'
                print(f"\nThe Marks of the student is :-> {mar}\nThe status is :-> {stat}\n")
            else:
                print(f"\nThe details of {name} is not found in the database\nPlease add him/her first\n")
            
        elif ch == 3:
            name = input("Enter the student's name here : ").strip().title()
            if name in stud:
                lcon = input("Are You Sure (Y/N):-> ").strip().lower()
                if lcon == 'y':
                    print(f"Details of {name} has beem removed\n")
                    del stud[name]
                else:
                    print(f"Details of {name} has been kept as is\n")
            else:
                print(f"The Student {name} doesn't exist please add him/her first then run the same\n")
        
        elif ch == 4:
            print("Saving to file.....\nSaved successfully")
            save_data()
            print(f"Thankyou for using our app\nApp used for {attmpt} time(s)\n")
            break

        else:
            save_data()
            print("Wrong Value Given\nPlease give a plausible and acceptable value\n")
            ti.sleep(1)
            o.system('cls' if o.name == 'nt' else 'clear')
            s.exit()
    
    finally:
        print("-"*50)
        
print("🄯 RSNPIIT (Ramrup Satpati) from IIT Madras | Released under the GNU GPLv3 License")