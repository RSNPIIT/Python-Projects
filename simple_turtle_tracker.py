import time as ti
import turtle as t
import os as o

#Static Variables
STYLE = ('Courier',35, 'bold')
POS = 'center'

#Clearing the Set Screen
def clear_all():
    o.system('cls' if o.system == 'nt' else 'clear')    

#Main Turtle Func..
def time_goes(x):
    while x >= 0:
        sc.update()
        timmy.home()
        timmy.pendown()
        mint = x // 60
        sec = x % 60
        if mint < 10:
            mint = f'0{mint}'
        if sec < 10:
            sec = f'0{sec}'
        timmy.clear()
        timmy.write(f"---> {mint} : {sec} <---",font = STYLE , align = POS )
        ti.sleep(1)
        x -= 1
    sc.exitonclick()
    clear_all()

#User Input Function..
def user_inp():
    try:
        wrkt = abs(int(input("Enter the Working Time Here(in mins) : ")))*60
        brkt = abs(int(input("Enter the Break Time Here(in mins) : ")))*60
        ses = abs(int(input("Enter the Number of Sessions Here : ")))
    except KeyboardInterruptError as ke:
        print("Exiting Nicely --")
        exit()
    except ValueError as v:
        print("Wrong Value Entered Please Enter a Numeric Value ")
        exit()
    if wrkt == 0 or brkt == 0 or ses == 0:
        print("Not Allowed\nThe Value Must be Greater than 0")
        exit()
    elif brkt > wrkt:
        print("Break Time Cant Be Greater than Work Time")
        exit()
    for i in range(1,ses + 1):
        print(f"Session {i}")
        print("Working Time ->")
        time_goes(wrkt)
        print("Break Time ->")
        time_goes(brkt)
    
#Setting Up the Screen and Turtle Object    
sc = t.Screen()
sc.title("TIMER")
sc.setup(800 , 800)
sc.bgcolor('black')
sc.tracer(0)

timmy = t.Turtle()
timmy.color('white')
timmy.hideturtle()
timmy.penup()
timmy.width(10)
user_inp()