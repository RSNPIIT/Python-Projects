import sympy as sp
import string as st
import time as ti
import os as o

# Static Variables
LPNT = 0
HPNT = 100
integrate_goes = False
YUP = 'Y'
NYET = 'N'
ATTMPT = 0

while not integrate_goes:
    ATTMPT += 1
    try:
        if len(ltr := input("Enter the rate of differentiation (ROD) constant here :-> ").strip().lower()) == 1 and ltr in list(st.ascii_lowercase) and ltr in (fnc := input("Enter the function here :-> ").strip().lower()):
            rod = sp.Symbol(ltr)
            expr = sp.sympify(fnc)
            
            indf_integral = sp.integrate(expr , rod)
            def_integral = sp.integrate(
                expr,
                (
                    rod,
                    LPNT,
                    HPNT
                )
            )
            print(f"Function is -> {fnc}\nIndefinite Integration is -> {str(indf_integral) + ' + c'} (where c is any constant belonging to the R real number set)\nDefinite Integral is -> {def_integral}")
        else:
            print("\nError occurred -- Please ensure that the rate of differentatior string is of one letter length and the letter exists in the function\nPlease try again")
            ti.sleep(1)
            o.system('cls' if o.name == 'nt' else 'clear')
            s.exit()

    except (KeyboardInterrupt , EOFError):
        print("\nIllegal Exit Detected .... | Iteration has been skipped")
        continue

    except sp.SympifyError:
        print("\nInvalid function has been given\nPlease give a valid one")
        continue
    
    else:
        print("\nDo you want to use the app again (Y/N)")

        while True:
            try:
                if (ch := input("Enter your choice here :-> ").strip().upper()) == YUP:
                    print("Good Choice mate\nContinuing")
                    ti.sleep(1)
                    o.system('cls' if o.name == 'nt' else 'clear')
                    break

                elif ch == NYET:
                    print(f"Thanyou -- for using our app...\nUsed for {ATTMPT} times")
                    integrate_goes = True
                    ti.sleep(1)
                    o.system('cls' if o.name == 'nt' else 'clear')
                    break
                
                else:
                    print("Wrong Value given...\nPlease Re-Enter here")
                    continue
            
            except (KeyboardInterrupt , EOFError):
                print("\nIllegal Exit B@nn3d.....")
                continue


print("🄯 RSNPIIT (Ramrup Satpati) IIT Madras | Released under the GNU GPL v3 license")    