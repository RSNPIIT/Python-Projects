import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
import pyperclip as cl
import ttkbootstrap as tdk

BLACK = '#000000'
WHITE = '#FFFFFF'
FONT = ("Courier", 25, "bold")
FAINT = ("Courier", 15, "bold")
FILE = 'ceaser.png'
SIDE = 'left'
LETTERS = [
    'a','b','c','d','e','f','g','h','i','j',
    'k','l','m','n','o','p','q','r','s','t',
    'u','v','w','x','y','z'
]
THEME = 'darkly'
FILENAME = 'saved_usecases.txt'

#UI Setup
sc = tdk.Window(themename = THEME)
sc.geometry('1000x1000')
sc.title('Ↄ34ЭЯ Ↄ!Ф3Г')
sc.config(padx = 50 , pady = 50 , bg = BLACK)

#Rendering the Styling Over Here
st = ttk.Style()
st.configure("c.TLabel", foreground = WHITE, background = BLACK , font = FONT)  
st.configure("j.TLabel", foreground = WHITE, background = BLACK , font = FAINT) 
st.configure("k.TButton", font = FAINT , padding = 10 )
st.configure("b.TFrame" , background = BLACK)

#Layout Setup in TTK
la = ttk.Label(master = sc , text = 'Ↄ34ЭЯ Ↄ!Ф3Г\nCEASER CIFER' , style = "c.TLabel")
la.pack(pady = 10)

#Canvas in Tk
cv = tk.Canvas(master = sc , width = 400 , height = 400 , relief = 'raised')
pb = tk.PhotoImage(file = FILE)
cv.image = pb
cv.create_image(200 , 200 , image = pb)
cv.pack(pady = 10)

#Functions
def disable_em_all():
    bu1.config(state = 'disabled')
    bu2.config(state = 'disabled')    
    bu3.config(state = 'disabled')

def restore():
    bu1.config(state = 'normal')
    bu2.config(state = 'normal')
    bu3.config(state = 'normal')
    
def do_it():
    new_word = ''
    val = ei.get().strip().lower()
    jb = eo.get().strip()
    
    if not val or not jb:
        msg.showinfo(title = 'WARNING' , message = "Can't Leave anything Empty")  
        return
    try:
        jb = abs(int(jb))
    except ValueError as e:
        msg.showinfo(title = 'WARNING' , message = 'Only Integer Values Allowed')
        return
    else:
        disable_em_all()
        for i in val:
            if i not in LETTERS:
                new_word += i
            else:
                ib = LETTERS.index(i)
                nib = ib + jb
                nib %= len(LETTERS)
                jnv = LETTERS[nib]
                new_word += jnv
        new_word = new_word.title()
        el.delete(0 ,tk.END)
        el.insert(0 , string = new_word)
        cl.copy(new_word)
    restore()

def dont_it():
    new_word = ''
    val = ei.get().strip().lower()
    ik = eo.get().strip()
    if not ik or not val:
        msg.showinfo(title = 'WARNING' , message = "Can't Leave Anything Empty")
        return
    try:
        ik = abs(int(ik))
    except ValueError as e:
        msg.showinfo(title = 'WARNING' , message = 'Only Integer values Allowed')
        return
    else:
        disable_em_all()
        for i in val:
            if i not in LETTERS:
                new_word += i
            else:
                ib = LETTERS.index(i)
                nib = ib - ik
                nib %= len(LETTERS)
                nval = LETTERS[nib]
                new_word += nval
        nval = nval.title()
        el.delete(0,tk.END)
        el.insert(0 , nval)
        cl.copy(new_word)
    restore()

def save_it():
    val1 = ei.get().strip().title()
    val2 = eo.get().strip()
    val3 = el.get().strip().title()
    if not val1 or not val3 or not val2:
        msg.showinfo(title = 'WARNING' , message = "Can't Save To files with empty values\nPlease add values")
        return
    else:
        try:
            val2 = abs(int(val2))
        except ValueError as v:
            msg.showinfo(title = "WARNING" , message = "Non Integral values Detected\nPlease Add Integral values Only")
            return
        else:
            disable_em_all()
            ch = msg.askokcancel(title = 'NOTE' , message = "Are You Sure You Wanna Save to File ?")
            if ch:
                with open(FILENAME , 'a') as fl:
                    fl.write(f"Original text :- {val1} | Shifted Index :- {val2} | Coded text :- {val3}")
                msg.showinfo(title = "SUCCESS" , message = "Data Added to FilePath")
            else:
                msg.showinfo(title = "NOTICE" , message = "Operation Aborted\nUser Said No")
    restore()

#Frame 1 (Label Frame)
fr1 = ttk.Frame(master = sc , style = "b.TFrame")
fr1.pack(pady = 10)

lb = ttk.Label(master = fr1 , text = 'Enter Your Text Here' , style = "j.TLabel")
lb.pack(pady = 10 , side = SIDE , padx = 15)

ei = ttk.Entry(master = fr1 , width = 40)
ei.insert(0, string = 'John Doe')
ei.pack(pady = 10 , side = SIDE)

#Frame 2 (Entry Frame)
fr2 = ttk.Label(master = sc ,style = "b.TFrame")
fr2.pack(pady = 10)

lc = ttk.Label(master = fr2 , text = 'Enter the En(De)cryption Index' , style = "j.TLabel")
lc.pack(pady = 10 , padx = 15 , side = SIDE)

eo = ttk.Entry(master = fr2 , width = 40)
eo.focus()
eo.pack(pady = 10 , padx = 15 , side = SIDE)

#Frame 3 (Button Frame)
fr3 = tk.Frame(master = sc , bg = BLACK)
fr3.pack(pady = 10)

bu1 = tk.Button(master = fr3 , width = 20 ,text = 'Encrypt' , fg = BLACK , bg = WHITE  ,command = do_it)
bu1.pack(padx = 15 ,side = SIDE , pady = 10)

bu2 = tk.Button(master = fr3 ,text = 'Decrypt'  , width = 20 , fg = BLACK , bg = WHITE  ,command = dont_it)
bu2.pack(side = SIDE , pady = 10 , padx = 15)

#Frame 4 (Displaying the Final Value)
fr4 = ttk.Frame(master = sc , style = "b.TFrame")
fr4.pack(pady = 10)

lbl = ttk.Label(master = fr4 , text = "Final En(De)Crypted Text Here" , style = "j.TLabel")
lbl.pack(padx = 15 , pady = 10 , side = SIDE)

el = ttk.Entry(master = fr4 , width = 40)
el.pack(padx = 15 , pady = 10 , side = SIDE)

#Frame 5 (Copying into a text file)
fr5 = ttk.Frame(master = sc , style = "b.TFrame")
fr5.pack(pady = 10)

lbj = ttk.Label(master = fr5 , text = "Click Here to Save to File" , style = "j.TLabel")
lbj.pack(padx = 15 , pady = 10 , side = SIDE)

bu3 = tk.Button(master = fr5 , text = 'File\nSave' , fg = BLACK , bg = WHITE , command = save_it)
bu3.pack(padx = 15 , pady = 10 , side = SIDE)

#Ensure that the loop continues
sc.mainloop()