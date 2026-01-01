import turtle as t
import random as r
import time as ti
t.colormode(255)

#Color Functions
def regb():
    re = r.randint(0,255)
    gr = r.randint(0,255)
    bl = r.randint(0,255)
    return (re,gr,bl)

#Static Variables
WHITE = '#FFFFFF'
WID = 10
DIR = [0,90,180,270]
FONT = 'Times New Roman'
ALIG = 'center'
SPEED = 'fast'

#UI Setup
sc = t.Screen()
sc.setup(600,600)
ans_case = sc.textinput("Who Do You Think Will Win ?" , "Enter Your Opinion").strip().lower()
sc.bgcolor(WHITE)
sc.title('The Two Turtle Walk')

#Setting Up the First Turtle (Tim)
tim = t.Turtle()
tim.hideturtle()
tim.shape('turtle')
tim.speed(SPEED)
tim.penup()
tim.width(WID)
tim.goto(0,-30)
tim.pendown()

#Setting Up the Second Turtle (Timmy)
timmy = t.Turtle()
timmy.hideturtle()
timmy.shape('turtle')
timmy.penup()
timmy.width(WID)
timmy.goto(0,30)
timmy.pendown()
timmy.speed(SPEED)

#Losing condition Function
def not_lost(p):
    if abs(p.xcor()) >= 290 or abs(p.ycor()) >= 290:
        return False
    else:
        return True

#Running till someone does an error or Out of bounds
while not_lost(tim) and not_lost(timmy):
    RCLR = regb()
    CDIR = r.choice(DIR)
    tim.color(RCLR)
    tim.forward(30)
    tim.setheading(CDIR)

    UCLR = regb()
    LDIR = r.choice(DIR)
    timmy.color(UCLR)
    timmy.forward(30)
    timmy.setheading(LDIR)

#Declaring our Winner
if not_lost(timmy):
    t.clear()
    skr = t.Turtle()
    skr.hideturtle()
    skr.penup()
    skr.home()
    skr.write('Timmy Wins !!' , align = ALIG , font = (FONT ,35 ,'bold'))
    ti.sleep(1)

    if ans_case == 'timmy':
        skr.clear()
        skr.write('Correct Guess\nTimmy Wins' , align = ALIG , font = (FONT ,35 ,'bold'))
   
    else:
        skr.clear()
        skr.write('Wrong Guess\nTimmy is the Winner' , align = ALIG , font = (FONT ,35 ,'bold'))

else:
    t.clear()
    skr = t.Turtle()
    skr.hideturtle()
    skr.penup()
    skr.home()
    skr.write('Tim Wins !!' , align = ALIG , font = (FONT ,35 ,'bold'))
    ti.sleep(1)

    if ans_case == 'tim':
        skr.clear()
        skr.write('Correct Guess\nTim Wins' , align = ALIG , font = (FONT ,35 ,'bold'))

    else:
        skr.clear()
        skr.write('Wrong Guess\nTim is the Winner' , align = ALIG , font = (FONT ,35 ,'bold'))  

sc.exitonclick()