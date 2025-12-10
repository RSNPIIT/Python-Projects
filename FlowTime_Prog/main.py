import tkinter as tk

#Color Variables
PINK = "#e2979c"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 52
BREAK_MIN = 17
reps = 0
tex = '✓'
tim = None

#Resetting the Timer
def reset_timer():
    global tim , reps
    if tim is not None:
        sc.after_cancel(tim)
        cv.itemconfig(tx , text = '00 : 00' , font = (FONT_NAME , 35 , 'bold'))
        l1.config(text = 'Timer', bg = YELLOW , font = (FONT_NAME , 50 , 'bold') , highlightthickness = 0)
        mk.config(text = '' , fg = PINK , bg = YELLOW , font = (FONT_NAME , 35 , 'bold') , highlightthickness = 0)
        reps = 0
    else:
        print("\nErroe Cant Reset Before Starting\n")

#Starting the Timer
def start_timer():
    global reps
    reps += 1
    work_t = WORK_MIN * 60
    brake_t = BREAK_MIN * 60
    if reps % 2 != 0:
        count_down(work_t)
        l1.config(text = 'Work Time' , bg = YELLOW , font = (FONT_NAME , 50 , 'bold') , highlightthickness = 0)
    else:
        count_down(brake_t)
        l1.config(text = 'Break Time' , bg = YELLOW , font = (FONT_NAME , 50 , 'bold') , highlightthickness = 0)

#Count_Down Function
def count_down(count):
    w_min = count // 60
    w_sec = count % 60   
    
    if count > 0:
        global tim
        tim = sc.after(1000 , count_down , count - 1)
        if w_sec < 10:
            w_sec = f'0{w_sec}'

        if w_min < 10:
            w_min = f'0{w_min}'
        cv.itemconfig(tx , text = f'{w_min} : {w_sec}')

    else:
        start_timer()
        mt = ''
        for i in range(reps//2 + 1):
            mt += tex
        mk.config(text = mt , fg = PINK , bg = YELLOW , font = (FONT_NAME , 35 , 'bold') , highlightthickness = 0)
        
#UI Setup
sc = tk.Tk()
sc.title('Flexible Timer')
sc.config(padx = 100, pady = 100, bg = YELLOW)

l1 = tk.Label(text = 'Timer' , bg = YELLOW , font = (FONT_NAME , 50 , 'bold') , highlightthickness = 0)
l1.grid(column = 1, row = 0)

cv = tk.Canvas(width = 300 , height = 300 , bg = YELLOW , highlightthickness = 0)
img = tk.PhotoImage(file = 'tomato.png')
cv.create_image(150 , 150 , image = img)
tx = cv.create_text(150 , 150 , text = "00 : 00" , fill = 'white' , font = (FONT_NAME , 35 , 'bold'))
cv.grid(column = 1, row = 1)

bu_1 = tk.Button(text = 'Start' , command = start_timer , font = (FONT_NAME , 35 , 'bold') , highlightthickness = 0)
bu_1.grid(column = 0, row = 2)

bu_2 = tk.Button(text = 'Reset' , command = reset_timer , font = (FONT_NAME , 35 , 'bold') , highlightthickness = 0)
bu_2.grid(column = 2, row = 2)

mk = tk.Label(text = '' , fg = PINK , bg = YELLOW , font = (FONT_NAME , 35 , 'bold'))
mk.grid(column = 1, row = 3)

sc.mainloop()
