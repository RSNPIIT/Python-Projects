import tkinter as tk
import pyperclip as cl
import ttkbootstrap as tdk
from tkinter import ttk
from tkinter import messagebox as msg

# Mapping Global Dictionary
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
TEXT_FL = 'saver.txt'
MODE = 'a'
sym = '-'*50

# Definition of the Function
def int_to_roman(n):
    res = ''
    for val , si in ROMAN_MAP:
        while n >= val:
            res += si
            n -= val
    cl.copy(res)
    return res

def do_it():
    en2.delete(0 , tk.END)
    try:
        val = int(en1.get())
        if val <= 0:
            msg.showinfo(title = "WARNING 🚨" , message = f"Error -> The Integer Field can't be empty or zero or negative integer")
    except ValueError as v:
        msg.showinfo(title = "WARNING 🚨" , message = f"Error -> Please enter Integer values\n{v}")
        en1.delete(0 , tk.END)
    else:
        sym = int_to_roman(val)
        en2.insert(0 , sym)
    
# Saving Function is here
def save_it():
    try:
        v1 = int(en1.get())
        if v1 <= 0:
            msg.showinfo(title = "WARNING 🚨" , message = f"Error -> The Integer Field can't be empty or zero or negative integer")
    except ValueError as v:
        msg.showinfo(title = "WARNING 🚨" , message = f"Error -> Please enter Integer values\n{v}")
        return
    
    v2 = en2.get()
    if not v1 or not v2:
        msg.showinfo(title = "WARNING 🚨" , message = "Error -> One or more of the processor values empty")
    with open(TEXT_FL , MODE) as f:
        ask = msg.askokcancel(
            title = "NOTICE ℹ️",
            message = "Do you want to really save to local file ?"
        )
        if ask:
            f.write(f"{sym}\nInteger -> {v1} || Roman -> {v2}\n")
            msg.showinfo(title = "NOTICE ℹ️" , message = "Data added to the file")
        else:
            msg.showinfo(title = "NOTICE ℹ️" , message = "Data discarded from adding to file")

    en1.delete(0 , tk.END)
    en2.delete(0 , tk.END)

# Static Variables
BLACK = '#000000'
WHITE = '#FFFFFF'
FONT = ('Courier', 45 , 'bold')
FAINT = ('Courier' , 25, 'bold')
SIDE = 'left'
IMG_FL = 'clock_pic.png'
REL = 'raised'
THEME = 'darkly'

# The Screen of the TKinter object
sc = tdk.Window(themename = THEME)
sc.geometry('1000x1000')
sc.title('Integer to Roman program')
sc.config(padx = 50 , pady = 50 , bg = BLACK)

# Styling Configuration of TTK
st = ttk.Style()
st.configure("j.TLabel" , foreground = WHITE , background = BLACK , font = FONT)
st.configure("k.TLabel" , foreground = WHITE , background = BLACK , font = FAINT)
st.configure("b.TFrame" , background = BLACK)

# Creating the UI
lbl = ttk.Label(master = sc, text = 'Integer to Roman' , style = "j.TLabel")
lbl.pack(pady = 10)

# Canvas Widget with the picture
cv = tk.Canvas(master = sc, width = 400 , height = 400 , relief = REL , bg = BLACK , highlightthickness = 0)
pb = tk.PhotoImage(file = IMG_FL)
cv.image = pb
cv.create_image(200 , 200 , image = pb)
cv.pack(pady = 10)

# Now creating the Widgets in the Scene
fr1 = ttk.Frame(master = sc, style = "b.TFrame")
fr1.pack(pady = 10)

lb1 = ttk.Label(master = fr1 , style = "k.TLabel" , text = "Enter the Indian-Arabic Numeral Here ->")
lb1.pack(padx = 10 , pady = 10 , side = SIDE)

en1 = ttk.Entry(master = fr1 , width = 40)
en1.focus()
en1.pack(padx = 10 , pady = 10 , side = SIDE)

fr2 = ttk.Frame(master = sc , style = "b.TFrame")
fr2.pack(pady = 10)

bu1 = tk.Button(master = fr2 , width = 20 , text = "Convert +" , command = do_it)
bu1.pack(padx = 10 , pady = 10 , side = SIDE)

fr3 = ttk.Frame(master = sc , style = "b.TFrame")
fr3.pack(pady = 10)

lb2 = ttk.Label(master = fr3 , style = "k.TLabel" , text = "Roman Numeral Value ->")
lb2.pack(padx = 10 , pady = 10 , side = SIDE)

en2 = ttk.Entry(master = fr3 , width = 40)
en2.pack(padx = 10 , pady = 10 , side = SIDE)

fr4 = ttk.Frame(master = sc , style = "b.TFrame")
fr4.pack(pady = 10)

lb4 = ttk.Label(master = fr4 , style = "k.TLabel" , text = "Save the Result Here ->")
lb4.pack(padx = 10 , pady = 10 , side = SIDE)

bu2 = tk.Button(master = fr4 , width = 20 , text = "Save+" , command = save_it)
bu2.pack(padx = 10 , pady = 10 , side = SIDE)

# The Root Loop of the GUI
sc.mainloop()