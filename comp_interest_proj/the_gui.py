import tkinter as tk
import ttkbootstrap as tdk
import pyperclip as cl
from tkinter import ttk
from tkinter import messagebox as msg

#Static Items
BLACK = '#000000'
FONT = ("Courier", 45, "bold")
WHITE = '#FFFFFF'
FILE = 'comp_int.png'
FAINT = ("Courier" , 25 , "bold")
SIDE = 'left'
FILEN = 'savingfile.txt'
MODE = 'a'
THEME = 'darkly'

#Creating the GUI screen
sc = tdk.Window(themename = THEME)
sc.geometry('2500x2500')
sc.title('Compound Interest Calculator')
sc.config(padx = 50 , pady = 50 , bg = BLACK)

#The TTK Styling Object is this
st = ttk.Style()
st.configure("j.TLabel" , foreground = WHITE , background = BLACK , font = FONT)
st.configure("c.TLabel" , foreground = WHITE , background = BLACK , font = FAINT)
st.configure("b.TFrame" , background = BLACK)

#Creating the UI
lbl = ttk.Label(master = sc , text = 'Compound Interest' , style = "j.TLabel")
lbl.pack()

#Canvas Creation in Tkinter for the Images Part
cv = tk.Canvas(master = sc , width = 400 , height = 400 , relief = 'raised')
pb = tk.PhotoImage(file = FILE)
cv.image = pb
cv.create_image(200 , 200 , image = pb)
cv.pack(pady = 10)

#Defining functions for all our Widgets
def calc_it():
    s1 = ent.get().strip()
    s2 = ent2.get().strip()
    s3 = ent3.get().strip()
    s4 = ent4.get().strip()

    if not all([s1, s2, s3, s4]):
        msg.showinfo(title="Warning", message="You have one or more fields blank\n")
        return

    try:
        prn = float(s1)
        rt = float(s2) / 100
        anc = int(s3)
        tim = int(s4)

        if prn < 0 or rt < 0 or anc <= 0 or tim < 0:
            msg.showinfo(title = "Warning" , message = "Negative Values are not allowed\n")
            return

    except (KeyboardInterrupt , EOFError) as kb:
        print(kb)

    except ValueError as v:
        msg.showinfo(title = "Warning" , message = "Non Integral Values are not allowed\n")
        return
    else:
        amt = round(prn * ((1 + rt / anc) ** (anc * tim)) , 3)
        ci = round(amt - prn , 3)
      
        ch = msg.askokcancel(title = "NOT3", message = f"Are You sure you want to save to file\nPrincipal = ₹{prn}\nRate = {rt*100}\nTime (in yrs) = {tim}\nAnnual Num. = {anc}\nC.I. = ₹{ci}\nAmount = ₹{amt}")
        cl.copy(f"Amount : {amt}\nCompound Interest is : {ci}\n")

        if ch:
            lb6.config(text = f"₹ {amt}")
            lb8.config(text = f"₹ {ci}")
            msg.showinfo(title = "DONE" , message = "Shown Here !!!")
        else:
            msg.showinfo(title = "DONE" , message = "Discarded from being Shown !!!")
    finally:
        ent.delete(0 , tk.END)
        ent2.delete(0 , tk.END)
        ent3.delete(0 , tk.END)
        ent4.delete(0 , tk.END)

#Function to save all Items in a text file
def save_it():
    s1 = ent.get().strip()
    s2 = ent2.get().strip()
    s3 = ent3.get().strip()
    s4 = ent4.get().strip()

    if not all([s1, s2, s3, s4]):
        msg.showinfo(title="Warning", message="You have one or more fields blank\n")
        return

    try:
        prn = float(s1)
        rt = float(s2) / 100
        anc = int(s3)
        tim = int(s4)

        if prn < 0 or rt < 0 or anc <= 0 or tim < 0:
            msg.showinfo(title = "Warning" , message = "Negative Values are not allowed\n")
            return

    except (KeyboardInterrupt , EOFError) as kb:
        print(kb)

    except ValueError as v:
        msg.showinfo(title = "Warning" , message = "Non Integral Values are not allowed\n")
        return
    else:
        amt = round(prn * ((1 + rt / anc) ** (anc * tim)) , 3)
        ci = round(amt - prn , 3)
        ch = msg.askokcancel(title = "NOT3", message = f"Are You sure you want to save to file\nPrincipal = ₹{prn}\nRate = {rt*100}\nTime (in yrs) = {tim}\nAnnual Num. = {anc}\nC.I. = ₹{ci}\nAmount = ₹{amt}")
        if ch:
            with open(FILEN , MODE) as f:
                f.write(f"For Principal -> ₹{prn} || Rate -> {rt*100}% || Time -> {tim} year(s) || Number of times -> {anc} time(s) in a year || The C.I is ₹{ci} || The Amt. is ₹{amt}\n")
            msg.showinfo(title = "DONE", message = "Saved to File\n")
        else:
            msg.showinfo(title = "DONE", message = "Discarded from Saving\n")
    finally:
        ent.delete(0 , tk.END)
        ent2.delete(0 , tk.END)
        ent3.delete(0 , tk.END)
        ent4.delete(0 , tk.END)

#Adding the frames for the Labels and Buttons
fr1 = ttk.Frame(master = sc ,style = "b.TFrame")
fr1.pack(pady = 10)

lb2 = ttk.Label(master = fr1, style = "c.TLabel" , text = "Enter the Principal Here ->")
lb2.pack(padx = 10 , pady = 10 , side = SIDE)

ent = ttk.Entry(master = fr1 , width = 40 )
ent.focus()
ent.pack(padx = 10 , pady = 10 , side = SIDE)

fr2 = ttk.Frame(master = sc , style = "b.TFrame")
fr2.pack(pady = 10)

lb3 = ttk.Label(master = fr2, style = "c.TLabel" , text = "Enter the Annual Rate Here ->")
lb3.pack(padx = 10 , pady = 10 , side = SIDE)

ent2 = ttk.Entry(master = fr2 , width = 40)
ent2.pack(padx = 10 , pady = 10 , side = SIDE)

fr3 = ttk.Frame(master = sc , style = "b.TFrame")
fr3.pack(pady = 10)

lb3 = ttk.Label(master = fr3 , style = "c.TLabel" , text = "Enter the Number of times annually calc. -> ")
lb3.pack(padx = 10 , pady = 10 , side = SIDE)

ent3 = ttk.Entry(master = fr3 , width = 40)
ent3.pack(padx = 10 , pady = 10 , side = SIDE)

fr4 = ttk.Frame(master = sc , style = "b.TFrame")
fr4.pack(pady = 10)

lb4 = ttk.Label(master = fr4 , style = "c.TLabel" , text = "Enter the Number of Years here ->")
lb4.pack(padx = 10 , pady = 10 , side = SIDE)

ent4 = ttk.Entry(master = fr4 , width = 40)
ent4.pack(padx = 10 , pady = 10 , side = SIDE)

#making buttons with Tk as Tk here is easier to customize
fr7  = ttk.Frame(master = sc , style = "b.TFrame")
fr7.pack(pady = 10)

bu = tk.Button(master = fr7 , width = 20 , text = "Calculate+" , command = calc_it)
bu.pack(padx = 10 ,pady = 10 ,side = SIDE)

bu2 = tk.Button(master = fr7 , width = 20 , text = "Save+" , command = save_it)
bu2.pack(padx = 10 , pady = 10 , side = SIDE)

#Displaying the Result
fr5 = ttk.Frame(master = sc , style = "b.TFrame")
fr5.pack(pady = 10)

lb5 = ttk.Label(master = fr5 , style = "c.TLabel" , text = "The Amount is :->")
lb5.pack(padx = 10 , pady = 10 , side = SIDE)

lb6 = ttk.Label(master = fr5 , style = "c.TLabel" , text = "₹ 0")
lb6.pack(padx = 10 , pady = 10 , side = SIDE)

fr6 = ttk.Frame(master = sc , style = "b.TFrame")
fr6.pack(pady = 10)

lb7 = ttk.Label(master = fr6 , style = "c.TLabel" , text = "The C.I. is :->")
lb7.pack(padx = 10 , pady = 10 , side = SIDE)

lb8 = ttk.Label(master = fr6 , style = "c.TLabel" , text = "₹ 0")
lb8.pack(padx = 10 , pady = 10 , side = SIDE)

#Mainloop to keep the GUI Running
sc.mainloop()