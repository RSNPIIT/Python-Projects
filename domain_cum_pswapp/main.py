#Importing all necessary modules
import tkinter as tk
import random as r
import json as js
import ttkbootstrap as tdk
import pyperclip as cl
from tkinter import ttk
from tkinter import messagebox as msg

#Static Variables
BLACK = '#000000'
WHITE = '#FFFFFF'
FONT = ('Courier' , 25 , 'bold')
FAINT = ('Courier' , 15 , 'bold')
RELIEF = 'raised'
IFIL = 'myimg.png'
SIDE = 'left'
LETTERS = [
    'a','b','c','d','e','f','g','h','i','j','k','l','m',
    'n','o','p','q','r','s','t','u','v','w','x','y','z'
]
NUMBER = ['0','1','2','3','4','5','6','7','8','9']
S_CHAR = ['!','$','^','*','#','&','@','+','/']
FILENAME = 'my_val.json'
THEME = 'darkly'

#Functions
def block_em():
    bu1.config(state = 'disabled')
    bu2.config(state = 'disabled')
    bu3.config(state = 'disabled')
    bu4.config(state = 'disabled')

def restore():
    bu1.config(state = 'normal')
    bu2.config(state = 'normal')
    bu3.config(state = 'normal')
    bu4.config(state = 'normal')

def search_it():
    gd = en1.get()
    if not gd:
        msg.showinfo(title = "WARNING" , message = 'Nothing to Search\nDomain Feild Empty\n')
        return
    else:
        try:
            with open(FILENAME) as s:
                kb = js.load(s)
        except FileNotFoundError as e:
            srt = msg.askokcancel(title = 'WARNING' , message = "File Doesn't Exist\nWanna Create it ?\nClick Ok :- Create\nClick Cancel :- Skip\n")
            if srt:
                with open(FILENAME , 'w') as e:
                    pass
                msg.showinfo(title = 'WARNING' , message = 'File (Re)Created\n')
            else:
                msg.showinfo(title = 'WARNING' , message = 'Operation Aborted by User\n')
        else:
            block_em()
            if gd in kb:
                psw = kb[gd]['password']
                ppl = ''
                for i in range(len(psw)):
                    ppl += '*'
                msg.showinfo(title = 'NOTICE' , message = f'Domain Name Value {gd} is found \n\nThe Information is ->\nDomain Name - {gd}\nPassword is - {ppl} \n[REDACTED FOR SECURITY]')
            else:
                msg.showinfo(title = 'WARNING' , message = f'Web Info of {gd} not found\nThis Domain isnt added\n')
        finally:
            en1.delete(0 , tk.END)
            en2.delete(0 , tk.END)
            restore()

def gen_domain():
    genv = ''
    block_em()
    ltr = r.randint(3,5)
    nbv = r.randint(1,3)
    scv = r.randint(1,3)
    for i in range(ltr):
        genv += r.choice(LETTERS)
    for i in range(nbv):
        genv += r.choice(NUMBER)
    for i in range(scv):
        genv += r.choice(S_CHAR)
    genv = genv.title()
    en1.delete(0 ,tk.END)
    en1.insert(0 , genv)
    restore()

def g_pass():
    val = ''
    block_em()
    lst = []
    lrt = r.randint(4,7)
    nbv = r.randint(2,5)
    scv = r.randint(2,4)
    for i in range(lrt):
        lst.append(r.choice(LETTERS))
    for i in range(nbv):
        lst.append(r.choice(NUMBER))
    for i in range(scv):
        lst.append(r.choice(S_CHAR))
    r.shuffle(lst)
    for i in lst:
        val += i
    cl.copy(val)
    en2.delete(0 , tk.END)
    en2.insert(0 , val)
    restore()

def save_it():
    g1 = en1.get()
    g2 = en2.get()
    if not g1 or not g2:
        msg.showinfo(title = 'WARNING' , message = 'Noting to Save\nThe Domain and Password is Empty')
        return
    ji = msg.askokcancel(title = 'NOTICE' , message = 'Are You Sure You want to Save\nClick OK :- To Save\nClick Cancel :- To Go Back\n')
    
    new_val = {
        g1 : {
            'password' : g2
        }
    }
    if ji:
        try:
            with open(FILENAME) as r:
                data = js.load(r)
        except (FileNotFoundError , js.JSONDecodeError):
            data = {}
        
        data.update(new_val)
        block_em()

        with open(FILENAME , 'w') as h:
            js.dump(data , h , indent = 4)

        msg.showinfo(title = 'NOTICE' , message = 'Data SuccessFully Added to File\n')
        en1.delete(0 , tk.END)
        en2.delete(0 , tk.END)
    else:
        msg.showinfo(title = 'NOTICE' , message = 'Data Discarded From Adding\n')
    restore()

#Screen Setup
sc = tdk.Window(themename = THEME)
sc.geometry('800x800')
sc.title('>*M4!П एП> पा4$Щ*Я>')
sc.config(padx = 50 , pady = 50 , bg = BLACK)

#Style Setup]
stl = ttk.Style()
stl.configure("a.TLabel" , foreground = WHITE , background = BLACK , font = FONT)
stl.configure("b.TFrame" , background = BLACK)
stl.configure("c.TLabel" , foreground = WHITE , background = BLACK , font = FAINT)

#Label 1
lb1 = ttk.Label(master = sc , text = ">*M4!П एП> पा4$Щ*Я>\nDOMAIN AND PASSWORD" , style = "a.TLabel")
lb1.pack(pady = 10)

#Canvas Widget with my Image
imh = tk.PhotoImage(file = IFIL)
img_w = imh.width()
img_h = imh.height()

cv = tk.Canvas(master = sc , width = img_w , height = img_h , relief = RELIEF , highlightthickness = 0)
cv.image = imh
cv.create_image(0 , 0 , anchor = 'nw', image = imh)
cv.pack(pady = 10)

#Frame 1 for new Label and Entry
fr1 = ttk.Frame(master = sc , style = 'b.TFrame')
fr1.pack(pady = 10)

lb2 = ttk.Label(master = fr1 , text = "Domain Name" , style = 'c.TLabel')
lb2.pack(padx = 15 , pady = 10 , side = SIDE)

en1 = ttk.Entry(master = fr1 , width = 20)
en1.pack(padx = 15 , pady = 10 , side = SIDE)

bu1 = tk.Button(master = fr1 ,command = gen_domain , width = 20 , text = 'Generate' , fg = BLACK , bg = WHITE , font = FAINT , highlightthickness = 0)
bu1.pack(padx = 15 , pady = 10 , side = SIDE)

#Frame 2 for new Password and Entry
fr2 = ttk.Frame(master = sc , style = 'b.TFrame')
fr2.pack(pady = 10)

lb3 = ttk.Label(master = fr2 , text = 'Password' , style = 'c.TLabel')
lb3.pack(padx = 15 , pady = 10 , side = SIDE)

en2 = ttk.Entry(master = fr2 , width = 20)
en2.focus()
en2.pack(padx = 15 , pady = 10 , side = SIDE)

bu2 = tk.Button(master = fr2 , command = g_pass , width = 20 , text = 'Generate' , fg = BLACK , bg = WHITE , font = FAINT , highlightthickness = 0)
bu2.pack(padx = 15 , pady = 10 , side = SIDE)

#Frame 3
fr3 = ttk.Frame(master = sc , style = 'b.TFrame')
fr3.pack(pady = 10)

lb4 = ttk.Label(master = fr3 , text = 'Search for Password' , style = 'c.TLabel')
lb4.pack(padx = 15 , pady = 10 , side = SIDE)

bu3 = tk.Button(master = fr3 , width = 20 , text = 'Search' ,command = search_it, fg = BLACK , bg = WHITE , font = FAINT)
bu3.pack(padx = 15 , pady = 10 , side = SIDE)

#Frame 4
fr4 = ttk.Frame(master = sc , style = 'b.TFrame')
fr4.pack(pady = 10)

lb5 = ttk.Label(master = fr4 , text = 'Save to File' , style = 'c.TLabel')
lb5.pack(padx = 15 , pady = 10 , side = SIDE)

bu4 = tk.Button(master = fr4 , command = save_it , width = 20 , text = 'Save' , fg = BLACK , bg = WHITE , font = FAINT)
bu4.pack(padx = 15 , pady = 10 , side = SIDE)

sc.mainloop()