import tkinter as tk
from tkinter import messagebox as msg
import pandas as pd

#Importing the Pandas DataFrame
data = pd.read_csv('natocode.csv')
print(f"The Sample DatFrame is :-\n{data}\n")

vl = {value.letter : value.code for index,value in data.iterrows()}
print(f"The Dictionary form of the same is :-\n{vl}\n")

lis = [vl[i] for i in vl]
print(f"The List Form is :-\n{lis}\n")

#Static Variables
FONT_NAME = 'Verdana'
BLUE = "#0000FF"
LBLUE = '#ADD8E6'

#Command
def do_it():
    mg = ''
    ji = e1.get().strip().upper()
    for i in ji:
        if i not in vl:
            mg += i
            mg += ' '
        else:
            mg += vl[i]
            mg += ' '
    oi = msg.askokcancel(title = 'Confirmation' , message = f'Do You Wanna Code this message : {ji.title()}\n')
    if oi:
        msg.showinfo(title = 'NOTICE' , message = 'Message Decoded')
        # e1.delete(0 , tk.END)
        e2.delete(0 , tk.END)
        e2.insert(0 , string = f'{mg}')
    else:
        msg.showinfo(title = 'NOTICE' , message = 'Message Discarded')

#Add to a text File
def add_text():
    y = e1.get()
    z = e2.get()
    bh = '*' * len(z)

    if not(y and z):
        msg.showinfo(title = 'WARNING' , message = 'Please Enter Something to Add to text')
    else:
        op = msg.askokcancel(title = 'NOTICE' , message = f'Are You Sure You Wanna Add these to File \nMessage :- {y}\nCode :- {bh}\n')
        if op:
            with open('add_text.txt' , 'a') as r:
                r.write(f"Message :- {y} | Code :- {z}")
            msg.showinfo(title = 'NOTICE' , message = "Data Added to file")
        else:
            msg.showinfo(title = 'NOTICE' , message = "Data Discarded from Adding to File")

#Delee the text file
def delete_text():
    ou = msg.askokcancel(title = 'WARNING' , message = "Do You want to delete the text ? ")
    if ou:
        try:
            with open('add_text.txt' , 'r') as j:
                re = j.readlines()
                if len(re) == 0:
                    msg.showinfo(title = "WARNING" , message = "There's Nothing to Delete")
                else:
                    with open('add_text.txt' , 'w') as x:
                        pass
                    msg.showinfo(title = "NOTICE" , message = "Data Deleted from File")
        
        except FileNotFoundError:
            with open('add_text.txt' , 'w') as j:
                pass
            msg.showinfo(title = 'NOTICE' , message = "File Absent so it has been Recreated\n")
    else:
        msg.showinfo(title = "WARNING" , message = "Data Refrained from Deleting")

#UI Setup
sc = tk.Tk()
sc.title('NATO Code')
sc.config(padx = 100 , pady = 100 , bg = BLUE)

my_l = tk.Label(text = 'NATO - Code' , font = (FONT_NAME , 35 , 'bold'))
my_l.grid(column = 1 , row = 0)

cv = tk.Canvas(width = 200 , height = 200 , bg = LBLUE , highlightthickness = 0)
img = tk.PhotoImage(file = 'download.png')
cv.create_image(100 , 100 , image = img)
cv.grid(column = 1 , row = 1)

e1 = tk.Entry(width = 20)
e1.insert(0 , string = "John Doe" )
e1.grid(column = 1 , row = 2)

e2 = tk.Entry(width = 20)
e2.grid(column = 1 , row = 4)

bu = tk.Button(text = "Code" , width = 10 , font = (FONT_NAME , 35 , 'bold') , command = do_it)
bu.grid(column = 1 , row = 3)

bu1 = tk.Button(text = "Add to TXT File" , width = 20 , font = (FONT_NAME , 10 , 'bold') , command = add_text)
bu1.grid(column = 1 , row = 5)

bu2 = tk.Button(text = "Delete from TXT file" , width = 20 , font = (FONT_NAME , 10 , 'bold') , command = delete_text)
bu2.grid(column = 1 , row = 6)

sc.mainloop()