#Pong Game by @RSNPIIT (Ramrup Satpati from IITM)

import turtle as t
# import os

#Screen
sc = t.Screen()
sc.bgcolor("black")
sc.title("My Pong Game")
sc.setup(800,800)
sc.tracer(0)
sc.update()

#Bat1 
p1 = t.Turtle()
p1.color('white')
p1.penup()
p1.shape('square')
p1.shapesize(5,1)
p1.goto(-370,0)

#Bat2
p2 = t.Turtle()
p2.color('white')
p2.penup()
p2.shape('square')
p2.shapesize(5,1)
p2.goto(370,0)

#Ball
b = t.Turtle()
b.color('white')
b.penup()
b.shape('square')
b.goto(0,0)
b.dx = 0.75
b.dy = -0.75

#Score
s1 = 0
s2 = 0

#Sounding Var
# bounce = "~/Music/bounce.wav"

#Scoring Pen
pen = t.Turtle()
pen.color('white')
pen.penup()
pen.hideturtle()
pen.goto(0,370)
pen.write(f"Player A : {s1} Player B : {s2}",align="center",font=('Courier',12,'bold'))

#A will Go Up
def a_up():
    y = p1.ycor()
    if y < 350:
        y += 20
    else:
        pass
    p1.sety(y)

#A will Go Down
def a_dn():
    y = p1.ycor()
    if y > -350:
        y -= 20
    else:
        pass
    p1.sety(y)

#B will Go Up
def b_up():
    y = p2.ycor()
    if y < 350:
        y += 20
    else:
        pass
    p2.sety(y)

#B will Go Down
def b_dn():
    y = p2.ycor()
    if y > -350:
        y -= 20
    else:
        pass
    p2.sety(y)

#Pressing Keys
sc.listen()
sc.onkeypress(a_up,'w')
sc.onkeypress(a_dn,'s')
sc.onkeypress(b_up,"Up")
sc.onkeypress(b_dn,"Down")

#Main Game Loop
game_on = True
while game_on:
    sc.update()

    #Ball Moves
    b.setx(b.xcor() + b.dx)
    b.sety(b.ycor() + b.dy)

    #Ball's Border Checking and Bouncing Off
    if b.ycor() > 390:
        b.sety(390)
        b.dy *= -1
        #os.system(f"aplay {bounce}&")
    
    if b.ycor() < -390:
        b.sety(-390)
        b.dy *= -1
        #os.system(f"aplay {bounce}&")

    if b.xcor() > 390:
        b.goto(0,0)
        b.dx *= -1
        s1 += 1
        pen.clear()
        pen.write(f"Player A : {s1} Player B : {s2}",align="center",font=('Courier',12,'bold'))
    
    if b.xcor() < -390:
        b.goto(0,0)
        b.dx *= -1
        s2 += 1
        pen.clear()
        pen.write(f"Player A : {s1} Player B : {s2}",align="center",font=('Courier',12,'bold'))

    #Ball's Bouncing from Bat (1 and 2)
    if (b.dx > 0 and b.xcor() > 340) and ((b.ycor() < (p2.ycor() + 50)) and (b.ycor() > (p2.ycor() - 50))):
        b.setx(340)  
        b.dx *= -1
    if (b.dx < 0 and b.xcor() < -340) and ((b.ycor() < (p1.ycor() + 50)) and (b.ycor() > (p1.ycor() - 50))):
        b.setx(-340) 
        b.dx *= -1

    if s1 == 10 and s2 != 10:
        pen.clear()
        pen.home()
        game_on = False
        diff = s1 - s2
        pen.write(f"Player A Wins by {diff} point(s) ",align="center",font=('Courier',24,'bold'))

    elif s2 == 10 and s1 != 10:
        pen.clear()
        pen.home()
        game_on = False
        diff = s2 - s1
        pen.write(f"Player B Wins by {diff} point(s) ",align="center",font=('Courier',24,'normal'))
    

sc.exitonclick()