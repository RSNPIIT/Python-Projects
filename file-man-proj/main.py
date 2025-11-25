import os

def create_file(filenam):
    try:
        with open(filenam , 'x') as u:
            print(f'File Name : {filenam} created Successfully\n')

    except FileExistsError:
        print(f'File Name : {filenam} already exists\n')
    
    except Exception as e:
        print('An Error Occurred\n')
        
def view_file():
    fi = os.listdir()

    if not fi:
        print('No Files Found Inside the Said Directory\n')
    else:
        for i in fi:
            print(i)
    
def delete_file(filenam):
    try:
        os.remove(filenam)
        print(f'Filename {filenam} deleted successfully\n')

    except FileNotFoundError:
        print(f"I'm Sorry the File {filenam} Cant be Located \nPlease Check the Spelling and try again\n")

    except Exception as e:
        print('An Error Occurred\n')

def read_file(filenam):
    try:
        with open(filenam) as k:
            cn = k.read()
            print(f"The Content of the File is : {cn}\n")

    except FileNotFoundError:
        print(f"I'm Sorry the File {filenam} Cant be Located \nPlease Check the Spelling and try again\n")

    except Exception as e:
        print('An Error Occurred\n')

def file_edit(filenam):
    try:
        with open(filenam , 'a') as k:
            co = input('Enter Content to add here : ').strip().title()
            k.write(co + '\n')
            print(f'Successfully added content to {filenam}\n')

    except FileNotFoundError:
        print(f"I'm Sorry the File {filenam} Cant be Located \nPlease Check the Spelling and try again\n")

    except Exception as e:
        print('An Error Occurred\n')

def file_clear(filenam):
    try:
        with open(filenam , 'w') as j:
            pass
            print('File Content Erased Successfully\n')

    except FileNotFoundError:
        print(f"I'm Sorry the File {filenam} Cant be Located \nPlease Check the Spelling and try again\n")

    except Exception as e:
        print('An Error Occurred\n')


def main():
    attmpt = 0
    while True:
        attmpt += 1
        print('File Manager App by (🄯)RSNPIIT Corp \n')
        print("Options are :- \n1. Create a file \n2. View all Files \n3. Delete File \n4. Read File \n5. Edit File \n6. Delete Contents \n7. Exit")

        ch = abs(int(input('Enter your Choice Here : ')))
        
        if ch == 1:
            fix = input('Enter the Name of the Filename you wanna Create (Note : Use Proper Extension): ')
            create_file(fix) 
        
        elif ch == 2:
            view_file()

        elif ch == 3:
            fix = input('Enter the Name of the Filename you wanna delete : ').strip()
            if fix != 'main.py':
                delete_file(fix)
            else:
                print('Restricted Access\n')
                continue

        elif ch == 4:
            fix = input('Enter the Name of the Filename you wanna Read : ').strip()
            if fix != 'main.py':
                read_file(fix) 
            else:
                print('Restricted Access\n')
                continue

        elif ch == 5:
            fix = input('Enter the Name of the Filename you wanna edit : ').strip()
            if fix != 'main.py':
                file_edit(fix)
            else:
                print('Restricted Access\n')
                continue

        elif ch == 6:
            fix = input('Enter the File name whose contents you wanna clear : ').strip()
            if fix != 'main.py':
                file_clear(fix)
            else:
                print('Restricted Access\n')
                continue        

        elif ch == 7:
            print('Thank You For Using the App\n')
            print(f'App Used for : {attmpt} times \n')
            break

        else:
            print('Wrong Input Please use numbers from 1 to 7\n')
            continue

main()