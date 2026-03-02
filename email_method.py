import time as ti
SEP = "@"

while True:
    try:
        email = input("Enter Your Email Here : ").strip()
        ind = email.index(SEP)
        print("Valid Email Given ...")
    except (KeyboardInterrupt , EOFError) as kb:
        print("Ha Ha I wont Let you Escape\nEnter again......")
        continue
    except ValueError as v:
        print(f'\nNeed an @ something in Email Value\n{email} has no {SEP}')
        continue

    
    uname = email[:ind].title()
    dom = email[ind:]

    print(f"Your Username is {uname} and Domain is {dom}")

    print("Wanna Play again ")
    try:
        kv = input("Click Y or N :-> ").strip().lower()
    except (KeyboardInterrupt , EOFError) as kb:
        print("\nNot Allowed Here")
    except Exception as ex:
        print(ex)
        break
    else:
        if kv == 'y':
            print("Lets Go ....")
            continue
        elif kv == 'n':
            print("Goodbye ......")
            break
        else:
            print("\nNot Allowed Value ......")
            print("\nRedirecting to a y...")
            ti.sleep(1)
            print("\nRedirection Successfull.....")
    finally:
        print("\nCopyLeft Tux and Pytho Corp..")