import os as o
import json as js
import tkinter as tk
import pyperclip as cl
from tkinter import ttk , messagebox as msg

# Static Variables
BLACK = '#000000'
WHITE = '#FFFFFF'
FONT = ("Courier", 45 , "bold")
FAINT = ("Courier", 25 , "bold")
FILE = 'pic_rl.png'
FIEL = 'value.json'
SIDE = 'left'

# The Function to Add into the JSON FIle is this one
def get_hold(fle):
    if o.path.exists(fle):
        try:
            with open(fle) as f:
                lib = js.load(f)
        
        except (js.JSONDecodeError , ValueError) as vl:
            lib = {}
    else:
        lib = {}
    return lib

def srch_it():
    jlb = get_hold(FIEL)
    s1 = ent.get().strip()

    if not s1:
        msg.showinfo(title = "WARNING 🚨", message = "The ISBN Field is empty")

    elif s1 not in jlb:
        msg.showinfo(title = "WARNING 🚨", message = "The Book corresponding to the ISBN number is not found")
    
    else:
        en1.delete(0 ,tk.END)
        bk = jlb[s1]
        en1.insert(0 , bk)
        cl.copy(bk)
    return

def update_wrt(something , some_othr):
    with open(some_othr , 'w') as f:
        js.dump(something , f , indent = 4)

def add_one():
    jlb = get_hold(FIEL)
    s1 = ent.get().strip()
    b1 = en1.get().strip()

    if not s1 or not b1:
        msg.showinfo(title = "WARNING 🚨", message = "The ISBN Field and/or the book fields is/are empty")
    
    else:
        spc = msg.askokcancel(title = "ALERT ℹ️", message = f"Are You sure You want to add to JSON File ?\nISBN Num. -> {s1}\nBook Name -> {b1}\n")
        if spc:
            jlb[s1] = b1
            update_wrt(jlb , FIEL)
            msg.showinfo(title = "SUCCESS ✔️", message = "Added the said data to file")
        else:
            msg.showinfo(title = "WRONG ❌", message = "Data discareded from adding to file")
        ent.delete(0 , tk.END)
        en1.delete(0 , tk.END)   
    return

# Tkinter Core Pluggins here
sc = tk.Tk()
sc.geometry('2500x2500')
sc.title('Library Analysis')
sc.config(padx = 50, pady = 50, bg = BLACK)

st = ttk.Style()
st.configure("j.TLabel" , foreground = WHITE , background = BLACK , font = FONT)
st.configure("k.TLabel" , foreground = WHITE , background = BLACK , font = FAINT)
st.configure("b.TFrame" , background = BLACK)

lbl = ttk.Label(master = sc, text = "Library Analysis", style = "j.TLabel")
lbl.pack(pady = 10)

cv = tk.Canvas(master = sc, width = 400 , height = 400 , relief = 'raised')
im = tk.PhotoImage(file = FILE)
cv.image = im
cv.create_image(200 ,200 , image = im)
cv.pack(pady = 10)

fr1 = ttk.Frame(master = sc, style = "b.TFrame")
fr1.pack(pady = 10)

lbl = ttk.Label(master = fr1, style = "k.TLabel", text = "Enter the ISBN Number Here :-> ")
lbl.pack(padx = 10, pady = 10 , side = SIDE)

ent = ttk.Entry(master = fr1, width = 40)
ent.focus()
ent.pack(padx = 10, pady = 10, side = SIDE)

bu = tk.Button(master = fr1, width = 20 , text = "Search 🔍" , command = srch_it)
bu.pack(padx = 10, pady = 10, side = SIDE)

fr2 = ttk.Frame(master = sc, style = "b.TFrame")
fr2.pack(pady = 10)

lb2 = ttk.Label(master = fr2, style = "k.TLabel" , text = "Enter the Book Here :-> ")
lb2.pack(pady = 10, padx = 10 , side = SIDE)

en1 = ttk.Entry(master = fr2 , width = 40)
en1.pack(padx = 10, pady = 10, side = SIDE)

fr3 = ttk.Frame(master = sc, style = "b.TFrame")
fr3.pack(pady = 10)

bu2 = tk.Button(master = fr3 , width = 20 , text = "Add ➕", command = add_one)
bu2.pack(pady = 10)

# The Command to make the GUI auto refresh
sc.mainloop()