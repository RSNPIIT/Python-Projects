import tkinter as tk
from tkinter import ttk

#TTK Widgets
lbl = ttk.Label(master = win , text = 'NOTEPAD').pack()

#Widgets
win = tk.Tk() #A Window to Place Everything in
win.title('Window and Widgets')
win.geometry('700x700') #This has values in height x width format

#Text Widgets
tex = tk.Text(master = win)
tex.pack()

#Update the GUI
win.mainloop()