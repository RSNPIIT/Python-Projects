import tkinter as tk

# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
reps = 0
tex = '✓'
tim = None
# ---------------------------- TIMER RESET ------------------------------- # 
def reset_timer():
    sc.after_cancel(tim)
    cv.itemconfig(ti , text = "00:00")
    t_l.config(text = 'Timer')
    c_m.config(text = '')
    global reps
    reps = 0

# ---------------------------- TIMER MECHANISM ------------------------------- # 
def start_timer():
    global reps
    reps += 1

    #Times all'll go
    work_sec = WORK_MIN * 60
    shrt_brk_sec = SHORT_BREAK_MIN * 60
    long_brk_sec = LONG_BREAK_MIN * 60

    if reps % 2 != 0:
        t_l.config(text = 'Work Time' , fg = PINK , font = (FONT_NAME , 50 , 'bold'))
        countdown(work_sec)
    elif reps % 8 == 0:
        t_l.config(text = 'Long Break Time' , fg = RED , font = (FONT_NAME , 50 , 'bold'))
        countdown(long_brk_sec)
    else:
        t_l.config(text = 'Short Break Time' , fg = RED , font = (FONT_NAME , 50 , 'bold'))
        countdown(shrt_brk_sec)

# ---------------------------- COUNTDOWN MECHANISM ------------------------------- # 
def countdown(cnt):
    cnt_min = cnt // 60
    cnt_sec = cnt % 60
    if cnt_sec < 10:
        cnt_sec = f'0{cnt_sec}'
    cv.itemconfig(ti , text = f'{cnt_min} : {cnt_sec}')
    if cnt > 0:
        global tim
        tim = sc.after(1000 , countdown , cnt -1)
    else:
        start_timer()
        marks = ""
        work_ses = reps // 2
        for _ in range(work_ses):
            marks += tex
            c_m.config(text = marks)


# ---------------------------- UI SETUP ------------------------------- #
sc = tk.Tk()
sc.title('Pomodoro')
sc.config(padx = 45, pady = 45, bg = YELLOW)

cv = tk.Canvas(width = 250 , height = 250 , bg = YELLOW , highlightthickness = 0)

t_l = tk.Label(text = 'Timer' , bg = YELLOW , font = (FONT_NAME , 50 , 'bold') , highlightthickness = 0)
t_l.grid(column = 1 , row = 0)

img = tk.PhotoImage(file = 'tomato.png')
cv.create_image(120 , 120 ,image = img )
ti = cv.create_text(120 , 130 , text = '00:00', fill = 'white' , font = (FONT_NAME , 35 , 'bold'))
cv.grid(column = 1, row = 1)

bu_1 = tk.Button(text = 'START' , command = start_timer , highlightthickness = 0 )
bu_1.grid(column = 0 , row = 2)

bu_2 = tk.Button(text = 'RESET' , command = reset_timer , highlightthickness = 0)
bu_2.grid(column = 2 , row = 2)

c_m = tk.Label(bg = YELLOW)
c_m.grid(column = 1, row = 3)

sc.mainloop()