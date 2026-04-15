import time as ti
import platform as pt
import sys as s
import os as o
import subprocess as sb
from cryptography.fernet import Fernet as frn

# Static and Secret Variables
FILE = 'thekey.key'
TARG = 'file1.txt'
MODE = 'rb'
AMODE = 'wb'
SECRET_P = o.getenv("SECRET_P")
THI = ('.py' ,'.ipynb')
LIS = [f for f in o.listdir() if o.path.isfile(f) and not f.endswith(THI)]

if not SECRET_P:
    print("You Dont have the necessary permission here\nPlease add one Secret Phrase ")
    ti.sleep(1)
    o.system('cls' if  pt.system() == 'windows' else 'clear')
    s.exit()

if not LIS:
    print("Python Found out that there is no target sample file in the Directory\nPlease make some using touch command\n")
    ti.sleep(1)
    o.system('cls' if  pt.system() == 'windows' else 'clear')
    s.exit()

elif FILE not in LIS:
    print(f"The File {FILE} not found\nPlease Run and generate one using Encrption Encrypt.py\n")
    ti.sleep(1)
    o.system('cls' if  pt.system() == 'windows' else 'clear')
    s.exit()

with open(TARG , MODE) as f:
    samp = f.read(1)
    if samp != b'g':
        print(f"Wait The File is in Plain Site View\nThat means Encrypt.Py has not run yet\n")
        print("Running Encrypt.py\n")
        ti.sleep(1)
        try:
            jkl = sb.run(
                ['python3' , 'encrypt.py'],
                capture_output = True,
                text = True,
                check = True
            )
        except Exception as e:
            ti.sleep(1)
            o.system('cls' if  pt.system() == 'windows' else 'clear')
            s.exit()
        else:
            print(jkl.stdout)

with open(FILE , MODE) as k:
    key = k.read()

for file in LIS:
    if file == FILE:
        continue
    
    with open(file , MODE) as fl:
        rfl = fl.read()
    try:
        dec_con = frn(key).decrypt(rfl)

        with open(file , AMODE) as z:
            z.write(dec_con)

        print(f"Status\nDecrypted the file {file} successsfully\n")
    except Exception as e:
        print(f"Skipping File -> {file}\nIt is Due to error {e}")