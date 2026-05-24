import time as ti
import sys as s
import os as o

# Static variables 
ROMAN_MAP = [
    (1000, 'M'),
    (900 , 'CM'),
    (500 , 'D'),
    (400 , 'CD'),
    (100 , 'C'),
    (90  , 'XC'),
    (50  , 'L' ),
    (40  , 'XL'),
    (10  , 'X'),
    (9   , 'IX'),
    (5   , 'V'),
    (4   , 'IV'),
    (1   , 'I')
]

# This is the function here
def int_to_roman(n):
    res = ''
    for value , symbol in ROMAN_MAP:
        while n >= value:
            res += symbol
            n -= value
    return res

# Main block of asking the user to do things
try:
    val = abs(int(input("Enter a number here :-> ")))
    if val == 0:
        print("Error -> 0 has no Roman numerals\nPerhaps the romans forgot about this\n")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()
    
    elif val > 8000:
        print("Error -> The higher limit has been reached\nSee I can have large values but the problem is it will take too much time and large CPU consumption\n")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()

    else:
        pass

except (KeyboardInterrupt , EOFError) as kb:
    print("\nExitting ...\nPlease dont spam")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()
except ValueError as v:
    print(f"Error -> {v}\nNon Integer values given ...")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()
except OverflowError as ov:
    print(f"Error -> {ov}\nToo Big of a value given ...")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()
else:
    r_val = int_to_roman(val)
    print(f"The Roman Number is :-> {r_val}")
finally:
    print("🄯 RSNPIIT (Ramrup Satpati) | Released under the GNU GPLv3 license")