import tkinter as tk
import random as r
import pandas as pd

BACKGROUND_COLOR = "#B1DDC6"
FONT_COLOR = 'Arial'
print('\n')
data = pd.read_csv('data/french_words.csv')
print("The DataFrame is :\n")
print(data)
print('\n')
val = {value.French : value.English for index , value in data.iterrows()}

print("The Dictionary type Value is :\n")
print(val)
lis = [x for x in val]

print('\n')
print("The List type Val is :\n")
print(lis)

a_cr = None
a_en = None
print("\n")

def is_known():
    global a_cr
    lis.remove(a_cr)
    del val[a_cr]

    dt = pd.DataFrame(list(val.items()), columns=["French", "English"])
    dt.to_csv('data/words_to_know.csv', index=False)
    
    next_cad()

def next_cad():
    # print(f'\n{a_cr}\n')
    global a_cr , a_en , timer
    sc.after_cancel(timer)
    a_cr = r.choice(lis)
    a_en = val[a_cr]
    cv.itemconfig(t_c , text = 'French' , fill = 'black')
    cv.itemconfig(m_c , text = f'{a_cr}' , fill = 'black')
    cv.itemconfig(front , image = c_f)
    timer = sc.after(3000 , func = flip_it)    

def flip_it():
    cv.itemconfig(t_c , text = 'English' , fill = 'white')
    cv.itemconfig(m_c , text = f'{a_en}' , fill = 'white')
    cv.itemconfig(front , image = c_b)

#UI
sc = tk.Tk()
sc.title('Flash App')
sc.config(padx = 50 , pady = 50 , bg = BACKGROUND_COLOR)
timer = sc.after(3000 , func = flip_it)

cv = tk.Canvas(width = 800 , height = 526)
c_f = tk.PhotoImage(file = 'images/card_front.png')
c_b = tk.PhotoImage(file = 'images/card_back.png')

cv.config(bg = BACKGROUND_COLOR , highlightthickness = 0)
front = cv.create_image(400 , 263 , image = c_f)
# back = cv.create_image(400 , 263 , image = c_b)
t_c = cv.create_text(400 , 150 , text = "Title" , font = (FONT_COLOR , 40 , 'italic'))
m_c = cv.create_text(400 , 263 , text = "Sample" , font = (FONT_COLOR , 40 , 'bold'))
cv.grid(column = 0 , row = 0 , columnspan = 2)


wr = tk.PhotoImage(file = "images/wrong.png")
bu = tk.Button(image = wr , highlightthickness = 0 , command = next_cad)
bu.grid(column = 0 , row = 1)

co = tk.PhotoImage(file = "images/right.png")
bu2 = tk.Button(image = co , highlightthickness = 0 , command = is_known)
bu2.grid(column = 1 , row = 1)

next_cad()
sc.mainloop()