import tkinter as tk

#--- Static Variables ---
LBLUE = '#ADD8E6'
RED = '#FF0000'
BLK = '#000000'
FONT_NAME = 'Verdana'
WHT = '#FFFFFF'
tim = None

val = abs(int(input("Enter the Countdown Value : ")))

#--- T!M3R Setup ---
def set_time():
    count_dn(val)

def count_dn(cnt):
    if cnt < 10:
        cnt = f'0{cnt}'
    if cnt > 0:
        global tim
        tim = sc.after( 1000 , count_dn , cnt - 1)
    else:
        st1.config(text = "Time's Up")
    cv.itemconfig( tx , text = f"{cnt}")

#--- UI Setup ---
sc = tk.Tk()
sc.config(padx = 100 , pady = 100 , bg = LBLUE)

my_l = tk.Label(text = '+!П3Я ΦЯ*GЯ4П' , font = (FONT_NAME , 35 , 'bold'))
my_l.grid(column = 1 , row = 0)

cv = tk.Canvas(width = 200 , height = 200 , bg = RED , highlightthickness = 0 )
tx = cv.create_text(100 , 100 , text = "+!П3Я" , fill = BLK , font = (FONT_NAME , 35 , 'bold'))
cv.grid(column = 1 , row = 1)

bu = tk.Button(text = '3+Я+ +!П3Я' ,font = (FONT_NAME , 35 , 'bold') ,bg = BLK , fg = WHT , highlightthickness = 0 , command = set_time)
bu.grid(column = 1 , row = 2)

st1 = tk.Label(text = '' , font = (FONT_NAME , 35 , 'bold'))
st1.grid(column = 1 , row = 3)

sc.mainloop()