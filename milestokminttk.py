import tkinter as tk
# from tkinter import ttk
import ttkbootstrap as ttk

#Static Elements
FONT = 'Calibri 24 bold'
SIDE = 'left'
THEME = 'darkly'

#Function to Convert the Miles to Kilometres
def do_it():
    try:
        val = round(entry_int.get() * 1.61 , 3)
    except tk.TclError:
        ou_str.set("Enter a Number Please")
        entry_int.set(0)
    else:
        ou_str.set(val)

#UI Setup
sc = ttk.Window(themename = THEME)
sc.title('Miles to Kilometres in ttk')
sc.geometry('400x200')

#Elements (Using TTK)
t_lab = ttk.Label(master = sc , text = 'Miles to Kilometres' , font = FONT)
t_lab.pack()

#Input Field
cv = ttk.Frame(master = sc) #cv for Canvas in Tk but in TTK they call it Frame
entry_int = tk.IntVar()
inp = ttk.Entry(master = cv , textvariable = entry_int)
bu = ttk.Button(master = cv , text = 'Convert' , command = do_it )
inp.focus()
inp.pack(side = SIDE , padx = 10)
bu.pack(side = SIDE)
cv.pack(pady = 10)

#Output Feild
ou_str = tk.StringVar()
ou = ttk.Label(master = sc , text = 'Output' ,font = FONT , textvariable = ou_str)
ou.pack(pady = 10)

#Running Iteratively
sc.mainloop()