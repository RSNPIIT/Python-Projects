import os as o
import time as ti

# Enter a name and extension
fname = input("Enter the Name of the File Here (For all files) : ").strip()
fext = input("Enter the Name of Extension of the File Here : ").strip().lower()

if not fext.startswith('.'):
    print("The File Doesnt Start with a Dot Separator so we add one")
    fext = '.' + fext

if len(fext[1 :]) >= 6:
    print("I will not allow you to have an extension of such large characters")
    exit()

elif " " in fname:
    print("Enter a valid filename without spaces please")
    exit()

count = 1

for file in list(o.listdir()):
    if o.path.isdir(file):
        print("Skipping the Directory Part")
        continue
    elif file.endswith('.py'):
        continue
    else:
        final_name = f'{fname}_{count}{fext}'
        try:
            base, _ = o.path.splitext(file)

            print(f"Renaming the file :-> {base} to {final_name}\n")
            o.rename(file , final_name)
            
            ti.sleep(1)
            print(f"STATUS -> ITERATION {count}\n'-'*50\nFile name {base} and successfully renamed to {fname}\n'-'*50")
            count += 1
        except Exception as e:
            print(f"Error Occurred\nIt is this -> {e}")
            continue