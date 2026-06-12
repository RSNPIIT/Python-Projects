import sympy as sp
import string as st
import time as ti
import os as o
import sys as s

# Static Variables
LPNT = 0
HPNT = 100

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
    print("\nExitting ... <PL3ASE D* NOT SPAM PL3ASE>")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()

except sp.SympifyError:
    print("\nInvalid function has been given\nPlease give a valid one")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()

finally:
    print("🄯 RSNPIIT (Ramrup Satpati) IIT Madras | Released under the GNU GPL v3 license")    