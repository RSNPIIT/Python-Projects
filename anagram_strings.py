import time as ti
import os as o
import sys as s

# Variables
try:
    w1 = input("Enter the first word here :-> ").strip().lower()
    w2 = input("Enter the second word here :-> ").strip().lower()

except (KeyboardInterrupt , EOFError) as kb:
    print("\nExitting....")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()

else:
    sw1 = sorted(w1)
    sw2 = sorted(w2)

    if sw1 == sw2:
        print("Da these strings are anagram ones\n")
    else:
        print("Nyet these strings are not anagram ones\n")