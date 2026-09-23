import tkinter as tk
import random as r  #Cause R is Python's Friend
from tkinter import messagebox as msg
import pyperclip as cl
FILENAME = 'data.txt'

let = [
    'A','B','C','D','E','F','G','H','I','J','K','L','M',
    'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
    'a','b','c','d','e','f','g','h','i','j','k','l','m',
    'n','o','p','q','r','s','t','u','v','w','x','y','z'
]
#Why let cause its not JS

num = [0,1,2,3,4,5,6,7,8,9]

s_ch = ['#','@','^',"&",'*','(',')','!','~']

# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def generate():
    r_let = r.randint(8,12)
    r_num = r.randint(2,4)
    r_sp = r.randint(2,4)

    psw1 = [r.choice(let) for _ in range(r_let)]
    psw2 = [r.choice(num) for _ in range(r_num)]
    psw3 = [r.choice(s_ch) for _ in range(r_sp)]

    psw = psw1 + psw2 + psw3

    r.shuffle(psw)

    st  = ''.join(str(x) for x in psw)
    e3.delete(0 , tk.END)
    e3.insert(0 , string = st)
    cl.copy(st)

# ---------------------------- SAVE PASSWORD ------------------------------- #
def save():
    w_val = e1.get()
    e_val = e2.get()
    p_val = e3.get()    

    if not(w_val and e_val and p_val):
        msg.showinfo(title = 'WARNING' , message = "Please Don't Leave Any Feilds Empty" )
    else:
        mg = '*' * len(p_val)

        is_ok = msg.askokcancel(title = w_val , message = f'These are the entered data :\nWebsite : {w_val} \nEmail : {e_val} \nPassword : {mg} \nIs it Okay to Save ?')

        if is_ok:

            with open(FILENAME , 'a' ) as r:
                r.write(f'{w_val} | {e_val} | {p_val}\n')
                e1.delete( 0 , tk.END)
                e3.delete( 0 , tk.END)
                msg.showinfo(title = 'Done' , message = 'Data Added to File')
        else:
            msg.showinfo(title = 'Done' , message = 'Data Discareded from Adding to File')

# ---------------------------- UI SETUP ------------------------------- #
sc = tk.Tk()
sc.title('Password Manager')
sc.config(padx = 100 , pady = 100 )

img = tk.PhotoImage(file = 'logo.png')
cv = tk.Canvas(width = 200 , height = 200 )
cv.create_image(100 , 100 , image = img)
cv.grid(column = 1 , row = 0)

l1 = tk.Label(text = 'Website')
l1.grid(column = 0 , row = 1)

e1 = tk.Entry(width = 35)
e1.grid(column = 1 , row = 1 , columnspan = 2)
e1.focus()

l2 = tk.Label(text = 'Email/UserName')
l2.grid(column = 0 , row = 2)

e2 = tk.Entry(width = 35)
e2.grid(column = 1 , row = 2 , columnspan = 2)
e2.insert(0 , string = 'john_doe@gmail.com')

l3 = tk.Label(text = 'Password')
l3.grid(column = 0 , row = 3)

e3 = tk.Entry(width = 20)
e3.grid(column = 1 , row = 3)

bu_0 = tk.Button(text = 'Generate' , width = 10 , command = generate)
bu_0.grid(column = 2 , row = 3)

bu_1 = tk.Button(text = 'ADD' , width = 36 , command = save)
bu_1.grid(column = 1 , row = 4 , columnspan = 2 )
sc.mainloop()