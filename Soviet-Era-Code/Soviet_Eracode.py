import tkinter as tk
from tkinter import messagebox as msg
import pandas as pd
import pyperclip as cl

FILENAME = 'safekeep.txt'
data = pd.read_csv('sovietcode.csv')
FONT_NAME = "Courier"

dice = {row.letter : row.value for index , row in data.iterrows()}

def copy_it():
    cj = e3.get()
    if not cj:
        msg.showinfo(title = "WARNING" , message = "Nothing to Copy")
    else:
        da = msg.askokcancel(title = "NOTICE" , message = f"Do You Wanna Copy this :\nCoded => {cj}\n")
        if da:
            cl.copy(cj)
            msg.showinfo(title = 'NOTICE' , message = 'Copied Successfully')
        else:
            msg.showinfo(title = 'NOTICE' , message = "Data Discarded Successfully")

def add_it():
    with open(FILENAME , 'a') as r:
        y1 = e2.get()
        y2 = e3.get()

        if not(y2 and y1):
            msg.showinfo(title = 'WARNING' , message = 'Nothing to add please add something')
        
        else:
            g = msg.askokcancel(title = 'NOTICE' , message = f"Do you Wanna Add :\nText = {y1} \nCode = {y2}")
            if g:
                r.write(f" Text => {y1} \nCode => {y2}\n")
                msg.showinfo(title = 'NOTICE' , message = "Data Added to File")
            else:
                msg.showinfo(title = 'NOTICE' , message = "Data Discarded From Adding to File")
        
def clear_it():
    de = msg.askokcancel(title = 'WARNING' , message = 'Are You Sure \nThis will wipe away your data\n')
    if de:
        try:
            with open(FILENAME) as r:
                read_val = r.readlines()
                if len(read_val) == 0:
                    msg.showinfo(title = 'NOTICE' , message = 'NOTING TO CLEAR\n')
                    return
                    
                else:
                    with open(FILENAME , 'w') as j:
                        pass
        
        except FileNotFoundError:
            with open(FILENAME , 'w') as r:
                msg.showinfo(title = 'NOTICE' ,message = 'File Was Absent so it has been (Re)Created')

        else:
            msg.showinfo(title = 'NOTE' , message = 'DATABASE CLEARED\n')

    else:
        msg.showinfo(title = 'NOTE' , message = 'DATABASE RETAINED\n')


def do_it():
    u_in = e2.get().strip().upper()
    if not u_in:
        msg.showinfo(title = 'WARNING' , message = "The Message Field can't be Empty")
    else:
        fstr = ''
        for i in u_in:
            if i not in dice:
                fstr += i
                fstr += ' '
            else:
                flis = [dice[i]]
                for j in flis:
                    fstr += j
                    fstr += ' '

        e3.delete(0 , tk.END)
        e3.insert(0 , string = fstr.title())
    
#UI Setup
sc = tk.Tk()
sc.title('Soviet Phonetic Alphabet')
sc.config(padx = 30 , pady = 30 , bg = 'red')

l1 = tk.Label(text = 'USSR Code' , font = (FONT_NAME,35,'bold') , width = 35 , bg = 'red' , highlightthickness = 0)
l1.grid(column = 1, row = 0)

cv = tk.Canvas(width = 400 , height = 400 , bg = 'red' , highlightthickness = 0)
img = tk.PhotoImage(file = 'CCCP_small.png')
cv.create_image(200 , 200 ,image = img)
cv.grid(column = 1 , row = 1)

l2 = tk.Label(text = 'Your Message' , font = (FONT_NAME,35,'bold') , width = 35 , bg = 'red' , highlightthickness = 0)
l2.grid(column = 0, row = 3)

e2 = tk.Entry(width = 35)
e2.insert(0, string = 'John Doe')
e2.grid(column = 1, row = 3)

l3 = tk.Label(text = 'Coded Message' , font = (FONT_NAME,35,'bold') , width = 35 , bg = 'red' , highlightthickness = 0)
l3.grid(column = 0, row = 4)

e3 = tk.Entry(width = 35)
e3.grid(column = 1, row = 4)

bu1 = tk.Button(text = 'Convert' , font = (FONT_NAME , 35 , 'bold') , command = do_it)
bu1.grid(column = 1, row = 5)

bu2 = tk.Button(text = 'Add to ClipBoard' , font = (FONT_NAME , 35 , 'bold') , command = copy_it)
bu2.grid(column = 1 , row = 6)

bu3 = tk.Button(text = 'Save to File' , font = (FONT_NAME , 35 , 'bold') , command = add_it)
bu3.grid(column = 1 , row = 7)

bu4 = tk.Button(text = 'Delete File' , font = (FONT_NAME , 35 , 'bold') , command = clear_it)
bu4.grid(column = 1 , row = 8)

sc.mainloop()