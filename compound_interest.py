import time as ti
go_on = True

while go_on:
    try:
        princ = float(input("Enter the Principal Amount Here in ₹ : "))
        rate = float(input("Enter the Rate here in % : ")) / 100 
        tim = float(input("Enter the Time here (in years) : "))
        n_time = int(input("Enter the Number of times in a year the interest is calculated : "))
        
        if princ <= 0 or rate <= 0 or tim <= 0 or n_time <= 0:
            print("\nZero or Negative Numerals are not allowed here \n\n\nPlease ReEnter")
            continue

    except (KeyboardInterrupt , EOFError):
        print("This cant be Exitted\nError")
        continue
    except ValueError as v:
        print("Non Numeric Values Given here\nWRONG --------")
        continue
    else:
        amt = round(princ * ((1 + (rate / n_time)) ** (n_time * tim)) , 3)
        comp = round(amt - princ , 3)
        mon = int(tim * 12)

        print(f"\nDetails :-\nPrincipal -> ₹{princ}\nInterest -> ₹{comp}\nAmount -> ₹{amt}\nRate -> {rate * 100}%\nTime -> {mon} months\nComponded -> {n_time} time(s) in a year\n")

        try:
            tyi = input("Enter Wheter You Wanna Coninue (y) or Quit (n) : ").strip().lower()
        except (KeyboardInterrupt , EOFError) as e:
            print("\nWrong Do You Not have any shame....\nCould Have Just typed a n")
            go_on = False
            break
        else:
            if not tyi:
                print("Null Value is not allowed\n")
            elif tyi in ['y','yes','yup','yo','ya']:
                print("Sure Thang\nLets Go On.....")
                continue
            elif tyi in ['n','no','na','nope','nyet']:
                print("\nThankyou for Playing Tux Calc...")
                go_on = False
                break
            else:
                print("The Value is Wrong.....\nRedirecting to a Yes")
                ti.sleep(1)
                print("\nRedirection Successful")
                continue
    finally:
        print("\nCopyLeft -> KTuxCalc Made by Tux Corp....\n")
