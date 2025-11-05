#include<stdio.h>
import turtle as t
import time
import random

delay = 0.1

#scores
score = 0
up,down,left,right = 90,270,180,0

#screen
sc = t.Screen()
sc.title('My Snake Game')
sc.bgcolor('yellow')
sc.setup(800,800)
sc.tracer(0)

#snake head
head = t.Turtle()
head.color('black')
head.penup()
head.shape('square')
head.goto(0,0)

#Snake Food
food = t.Turtle()
food.speed(0)
food.shape('circle')
food.color('blue')
food.penup()
food.goto(random.randint(-360,360),random.randint(-360,360))

#list of snake elements
s_l = []

#scoreboards
sk = t.Turtle()
sk.shape('square')
sk.color('black')
sk.penup()
sk.hideturtle()
sk.goto(0,370)
sk.write(f"Score : {score}",align="center",font=('Courier',12,'bold'))

#Movement
def go_up():
    if head.heading() != down:
        head.setheading(90)
            
def go_down():
    if head.heading() != up:
        head.setheading(270)

def go_left():
    if head.heading() != right:
        head.setheading(180)

def go_right():
    if head.heading() != left:
        head.setheading(0)

def move():
    if head.heading() == up:
        y = head.ycor()
        head.sety(y + 20)

    if head.heading() == down:
        y = head.ycor()
        head.sety(y - 20)
    
    if head.heading() == right:
        x = head.xcor()
        head.setx(x + 20)
    
    if head.heading() == left:
        x = head.xcor()
        head.setx(x - 20)

#Key Bindings
sc.listen()
sc.onkey(go_up,'Up')
sc.onkey(go_down,'Down')
sc.onkey(go_left,'Left')
sc.onkey(go_right,'Right')

#Main Game Loop
game_over = False
while not game_over:
    time.sleep(delay)
    sc.update()
    # move()  

    #Collision with the border
    if abs(head.xcor()) > 390 or  abs(head.ycor()) > 390:
        game_over = True
        sk.clear()
        sk.home()
        sk.write(f"Game Over \nYour Score is {score}",align="center",font=('Courier',24,'bold'))
        delay = 0.1
        break

    #Food Eating and Growing in SIze
    if head.distance(food) < 20:
        food.goto(random.randint(-360,360),random.randint(-360,360))

        #Growing in Size
        new_seg = t.Turtle()
        new_seg.shape('square')
        new_seg.color('black')
        new_seg.penup()
        s_l.append(new_seg)

        #Scoreboard Update
        score += 10
        sk.clear()
        delay -= 0.01
        sk.goto(0,370)
        sk.write(f"Score : {score}",align="center",font=('Courier',12,'bold'))


    #Synchronizing the Elements together
    for i in range(len(s_l)-1,0,-1):
        x = s_l[i-1].xcor()
        y = s_l[i-1].ycor()
        s_l[i].goto(x,y)

    #Move the element(0) to the head's position
    if len(s_l) > 0:
        s_l[0].goto(head.xcor(),head.ycor())

    move()

    #Checking body collision
    for x in s_l:
        if x.distance(head) <= 10:
            game_over = True
            time.sleep(1)
            sk.clear()
            delay = max(0.03, delay - 0.01)
            sk.home()
            sk.write(f"Game Over \nYour Score is {score}",align="center",font=('Courier',24,'bold'))
            
sc.exitonclick()