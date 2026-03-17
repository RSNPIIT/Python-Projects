import tkinter as tk
import pandas as pd
import time as ti
import os as o
import sys as s
import pyperclip as cl
import datetime as dt
import requests as rq
import ttkbootstrap as tdk
from tkinter import ttk
from tkinter import messagebox as msg

#Static Variables
BLACK = '#000000'
WHITE = '#FFFFFF'
FONT = ("Courier", 45, "bold")
FAINT = ("Courier", 25, "bold") 
SIDE = 'left'
RELIEF = 'raised'
PICFILE = 'cpicval.png'
FILENAM = 'datafile.csv'
THEMEN = 'darkly'
FILEKM = 'saver.txt'
MODER = 'a'

#Secret Variables
API_KEY =  o.environ.get("EXCHANGE_API_KEY")

if not API_KEY:
    print(f"API Key Doesn't Exist \nPlease Make one ---- from Exchange rate.com\n")
    ti.sleep(1)
    print("Exitting ...")
    o.system('cls' if o.name == 'nt' else 'clear')
    print("Exit..Successful")
    s.exit()

#Reading the CSV file to get the Currency the API Supports
dat = pd.read_csv(FILENAM)
the_l = dat.Code.to_list()

#Getting the set date in DD-MM-YYYY format
now = dt.datetime.now()
da = now.day
mh = now.month
yr = now.year

if da < 10:
    da = f'0{da}'
if mh < 10:
    mh = f'0{mh}'
foe = f'{da}-{mh}-{yr}'

#The Function to Calculate the Given Value
def calc_it():
    val1 = en1.get().strip().upper()
    val2 = en2.get().strip().upper()

    if not val1 or not val2:
        msg.showinfo(title = "WARNING" , message = "Null and Empty Values are not allowed in one or both feilds\n")
        if val1 is None and val2 is not None:
            en2.delete(0 , tk.END)
        elif val2 is None and val1 is not None:
            en1.delete(0 , tk.END)
        return
    elif (val1 not in the_l) or (val2 not in the_l):
        msg.showinfo(title = "WARNING" , message = f"As of {foe}\nThese Given Currency formats are not yet supported\nPlease try again later")
        en1.delete(0 , tk.END)
        en2.delete(0 , tk.END)
        return

    try:
        tnum = float(en3.get())
        if not tnum:
            msg.showinfo(title = "WARNING" , message = "You cant leave this feild blank\nPlease Give Something..|")
        elif tnum < 0:
            msg.showinfo(title = "WARNING" , message = "Currency cant be a negative number\nPlease Give Correct Values\n")
            en3.delete(0 , tk.END)
        elif tnum == 0:
            msg.showinfo(title = "NOTICE" , message = "Although Technically a Zero may be given and it WILL work\nYet we do not allow 0 as a value\nThe reason is a zero would automatically give you a zero of second currency\nThis would waste API calls so...\n")
            en3.delete(0 , tk.END)

    except ValueError as v:
        msg.showinfo(title = "WARNING" , message = "Non Numeric Values given\nPlease Correct it")
        en3.delete(0 , tk.END)
    else:
        URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{val1}'
        res = rq.get(url = URL)
        res.raise_for_status()
        
        what_needed = res.json()
        the_r = what_needed['conversion_rates'][val2]
        the_fin = the_r * tnum
        the_fin = round(the_fin , 3)
        cl.copy(the_fin)
        en4.delete(0 , tk.END)
        en4.insert(0 , f'{the_fin}')

#The Function to save the Notational Value and Exchange Rate Here
def save_it():
    try:
        val1 = en1.get().strip().upper()
        val2 = en2.get().strip().upper()
        val3 = round(float(en3.get()) , 3)
        val4 = round(float(en4.get()) , 3)
        
        if not val1 or not val2 or not val3 or not val4:
            msg.showinfo(title = "WARNING", message = "This Function Cant take the Empty Inputs\nPlease Enter again...\n")
            return
        
        elif (val1 not in the_l) or (val2 not in the_l):
            msg.showinfo(title = "WARNING" , message = f"As of {foe} the Given method isnt available in the API\n")
            return
    except ValueError as v:
        msg.showinfo(title = "WARNING" , message = "This Has been assigned erronous values\nNon-Negative & Non-Zero Numbers are the only acceptable value\n")
        return
    else:
        confi = msg.askokcancel(title = 'NOTICE' , message = "Do You Wanna Save the Data to the file\n")
        if confi:
            with open(FILEKM , MODER) as f:
                f.write(f'Base Currency :- {val1} || Quote Currency :- {val2} || Notational Value :- {val3} || Exchange Rate :- {val4}\n')
            msg.showinfo(title = "SUCCESS+" , message = "Added to the File \nIn Case the File wasnt Initialized it is (R3)Created\n")
        else:
            msg.showinfo(title = "DONE" , message = "The Data has been discarded from adding to the text file\n")
            return
    finally:
        en1.delete(0 , tk.END)
        en2.delete(0 , tk.END)
        en3.delete(0 , tk.END)
        en4.delete(0 , tk.END)
        
#Creating the UI of the Screen
sc = tdk.Window(themename = THEMEN)
sc.geometry('1000x1000')
sc.title("₡U₹₹3П₡У APP")
sc.config(padx = 50 , pady = 50 , bg = BLACK)

#Themed TKinter Styling Variables
st = ttk.Style()
st.configure("j.TLabel" , foreground = WHITE , background = BLACK , font = FONT)
st.configure("k.TLabel" , foreground = WHITE , background = BLACK , font = FAINT)
st.configure("b.TFrame" , background = BLACK)

#The Top Introductive Label Similar to a HTML h2 tag
lbl = ttk.Label(master = sc , text = "Конвертер валют" , style = "j.TLabel")
lbl.pack(pady = 10)

#The TKinter Canvas Object to Create the heading image
cv = tk.Canvas(height = 400 , width = 400 , relief = RELIEF)
pb = tk.PhotoImage(file = PICFILE)
cv.image = pb
cv.create_image(200 , 200 , image = pb)
cv.pack(pady = 10)

#The TTK Frame Object to Create the Labels , Entries and Buttons
fr1 = ttk.Frame(master = sc , style = "b.TFrame")
fr1.pack(pady = 10)

lbl = ttk.Label(master = fr1 , style = "k.TLabel" , text = "Enter the Base Currency Here")
lbl.pack(side = SIDE , padx = 10 , pady = 10)

en1 = ttk.Entry(master = fr1 , width = 40)
en1.focus()
en1.pack(side = SIDE , padx = 10 , pady = 10)

# The TTK Frame to take currency 2
fr2 = ttk.Frame(master = sc , style = "b.TFrame")
fr2.pack(pady = 10)

lbk = ttk.Label(master = fr2 , style = "k.TLabel" , text = "Enter the Quote Currency Here")
lbk.pack(padx = 10 , side = SIDE , pady = 10)

en2 = ttk.Entry(master = fr2 , width = 40)
en2.pack(side = SIDE , padx = 10 , pady = 10)

# The TTK Frame to take the number of amount in currency 1
fr3 = ttk.Frame(master = sc , style = "b.TFrame")
fr3.pack(pady = 10)

lbj = ttk.Label(master = fr3 , style = "k.TLabel" , text = "Enter the Notational value Here")
lbj.pack(pady = 10 , padx = 10 , side = SIDE)

en3 = ttk.Entry(master = fr3, width = 40)
en3.pack(padx = 10 , pady = 10 , side = SIDE)

#The Button to calculate the same
bu3 = tk.Button(master = sc , width = 20 , text = "Calculate+" , command = calc_it)
bu3.pack(pady = 10)

#The Final Frame where we display the result
fr4 = ttk.Frame(master = sc , style = "b.TFrame")
fr4.pack(pady = 10)

lbd = ttk.Label(text = f"As of {foe} I.S.T. the Exchange Rate is ->" , style = "k.TLabel" , master = fr4)
lbd.pack(pady = 10 , padx = 10 , side = SIDE)

en4 = ttk.Entry(master = fr4 , width = 40)
en4.pack(padx = 10 , pady = 10 , side = SIDE)

#The Last Button to Save the amounts to a txt file format
bu4 = tk.Button(master = sc , width = 20 , text = "Save+" , command = save_it)
bu4.pack(pady = 10)  

try:
    sc.mainloop()
except (KeyboardInterrupt , EOFError):
    print("Exitting--Please Dont Span\n")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()