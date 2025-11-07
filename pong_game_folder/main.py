import turtle as t
from paddle import Paddle
from ball import Ball
from score import Score
import time as ti

sc = t.Screen()
sc.setup(800,800)
sc.bgcolor('black')
sc.title('My Pong Game')
sc.tracer(0)

p1 = Paddle((-370,0))
p2 = Paddle((370,0))
b = Ball()

sc.listen()
sc.onkeypress(p1.go_up,'Up')
sc.onkeypress(p1.go_down,'Down')
sc.onkeypress(p2.go_up,'w')
sc.onkeypress(p2.go_down,'s')

sk = Score()
game_over = False
while not game_over:
    ti.sleep(b.delay)
    sc.update()
    b.move()

    if abs(b.ycor()) > 380:
        b.bounce_y()

    if b.xcor() < -350 and ((p1.ycor() - 50) < b.ycor() < (p1.ycor() + 50)): 
        b.setx(-350)
        b.bounce_x() 
    
    if b.xcor() > 350 and ((p2.ycor() - 50) < b.ycor() < (p2.ycor() + 50)): 
        b.setx(350)
        b.bounce_x()

    if b.xcor() > 380:
        sk.l_update_score()
        b.goto(0,0)

    if b.xcor() < -380:
        sk.r_update_score()
        b.goto(0,0)

    if sk.s1 == 10 and sk.s2 != 10:
        game_over = True
        sk.a_game_over()
    
    elif sk.s2 == 10 and sk.s1 != 10:
        game_over = True
        sk.b_game_over()

sc.exitonclick()