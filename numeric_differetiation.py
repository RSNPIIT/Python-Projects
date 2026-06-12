import sympy as sp
import string as st
import time as ti
import os as o
import sys as s

# Static Varibles
lcase = list(st.ascii_lowercase)

try:
    if len(ltr := input("Enter the rate of differentiation (rod) symbol here :-> ").strip().lower()) == 1 and ltr in lcase and ltr in (fnc := input("Enter the function here :-> ").strip().lower()):
        rod = sp.Symbol(ltr)
        expr = sp.sympify(fnc)
        derv = sp.diff(
            expr,
            rod
        )

        print(f"Original Function is -> {fnc}\nDerivative Function is -> {derv}")
    
    else:
        print("\nWrong input ensure that the symbol doesnt exceed length 1 and the symbol is in function\nPlease R3Enter")

except (KeyboardInterrupt , EOFError):
    print("\nExitting... <Pl3ase do n*t sp@m here>")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()

except sp.SympifyError as ers:
    print("\nWrong function input please give a proper function here")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()
    
finally:
    print("🄯 RSNPIIT (Ramrup Satpati) IIT Madras | Released under the GNU GPL v3 license")