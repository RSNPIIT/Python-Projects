import colorgram as co
import time as ti
import sys as s
import os as o
import platform as pl

# Static Variables
FILE = 'tux.jpg'
PLATF = pl.system()
try:
    a = int(input("Enter the Number of Colours You Wanna Extract : "))
    
    if not a:
        print("Null Values are not allowed over here\nLike Null Colours ...\nPlease Re-Enter")
        ti.sleep(1)
        o.system('cls' if PLATF == 'Windows' else 'clear')
        s.exit()
    elif a <= 0:
        print("NOTE :- Only the Positive Nonzero Numbers are allowed\nI mean just think if I told you that you need to extract -5 colours\nWont make sense would it ?\nPlease (RE)Enter\n")
        ti.sleep(1)
        o.system('cls' if PLATF == 'Windows' else 'clear')
        s.exit()
    elif a >= 50:
        print("See If You Give Large Values Several Problems will happen\nIt will lead to system slowing down and throttling\nThus for safety reasons the maximum limit is 49 colors..\nPlease re-enter...\n")
        ti.sleep(1)
        o.system('cls' if PLATF == 'Windows' else 'clear')
        s.exit()
    else:
        pass
except (KeyboardInterrupt , EOFError) as e:
    print("\nExitting the Program\nPlease Dont Spam.....")
    ti.sleep(1)
    o.system('cls' if PLATF == 'Windows' else 'clear')
    s.exit()
except ValueError as v:
    print("The Non Integer Values are not allowed\nUnable to proceed ...")
    ti.sleep(1)
    o.system('cls' if PLATF == 'Windows' else 'clear')
    s.exit()
except Exception as ex:
    print(f"Some Exception Occurred\n{e}")
    ti.sleep(1)
    o.system('cls' if PLATF == 'Windows' else 'clear')
    s.exit()
else:
    clr = co.extract('tux.jpg' , a)

    lis = [(c.rgb.r , c.rgb.g , c.rgb.b) for c in clr]
    print(f"\nThe Colours in Tux are :- \n{lis}")
finally:
    print(f"{PLATF} Rocks....\nMade by 🄯 RSNPIIT - aka Ramrup Satpati from IIT Madras\nThis Project as all other orojects in this repository are under the GNU General Public License Version 3 or Later (GNU GPLv3)\nMade with 🩷 in Linux and 🐍 Python\nThankyou")