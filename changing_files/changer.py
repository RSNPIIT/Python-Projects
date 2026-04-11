import os as o
import time as ti
import platform as pt
import sys as s

# Static Variables
LIS = [f for f in o.listdir() if o.path.isfile(f) and not f.endswith(('.py', '.ipynb'))]
SYM = '-'*50
itn = 1

if not LIS:
    print("Python Found that the directory is empty with no non pythonic files so ...\nSkipping the iterations\nPlease come back after populating the same\n")
    ti.sleep(1)
    o.system('cls' if pt.system() == 'windows' else 'clear')
    s.exit()

for l in LIS:
    print(f"\n{SYM}\nITERATION -> {itn}\nThe File's Name is ->  {l}\n")
    try:
        var = input("\nDo You wanna Rename this (Y/N) : ").strip().lower()
        if var == 'y':
            fname = input("Enter the new name of the file here  : ").strip()
            fext = input("Enter the new extension of the file here : ").strip().lower()

            if not fext.startswith('.'):
                print(f"The Extension {fext} Doesnt Start with a Dot Separator\nAuto-Adding one")
                fext = '.' + fext
                print(f"The Extension now becomes {fext}")                

            if len(fext[1 :]) > 6:
                print(f"Such Long Extensions are not Allowed here\nSkipped the Iteration {itn}\n")
                continue

            if " " in fname:
                print(f"See my friend while you could make the name with whitespaces but programming languages discourage these practices\nWhy ?\nYou ask you cant run python3 _ _.py or gcc _ _.c you can use '' the behaviour of which is not guaranteed\nSkipping Iteration {itn}")
                continue

            final_name = f'{fname}{fext}'

            if final_name in list(o.listdir()):
                print(f"----Skipping this Iteration (aka File Numbered {itn}) to prevent conflicts---")
                continue

            try:
                print(f"\nRenaming the file :-> {l} to {final_name}\n")
                ti.sleep(1)
                o.rename(l , final_name)
                
                ti.sleep(1)
                print(f"STATUS -> ITERATION {itn}\n{SYM}\nFile name {l} and successfully renamed to {fname}\n{SYM}")

            except Exception as e:
                print(f"Error Occurred\nIt is this ->{e}")
                continue
            
        elif var == 'n' :
            print("\nFile Rename Failed\nOperation aborted by user\n")
            continue
        else:
            print("\nFile Rename Failed\nOperation aborted by user\n")
            continue                

    except (KeyboardInterrupt , EOFError) as kb:
        print(f"\nSkipping This Iteration\nCurrently on the File Number {itn}")
        continue
    
    finally:
        itn += 1

print("Made with 🩶 In Python\nCreated by 🄯 RSNPIIT (Ramrup Satpati) from IIT Madras\nReleased under the GNU GPLv3 License")