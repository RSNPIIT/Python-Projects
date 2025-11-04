import turtle as t
import time as ti
from snake import Snake
from food import Food
from scoreboard import Scoreboard

sc = t.Screen()
sc.bgcolor('black')
sc.setup(600,600)
sc.title('My Snake Game')
sc.tracer(0)
my_sn = Snake()
foo = Food()
scr = Scoreboard()

sc.listen()

sc.onkey(my_sn.up,"Up")
sc.onkey(my_sn.down,"Down")
sc.onkey(my_sn.left,"Left")
sc.onkey(my_sn.right,"Right")

is_on = True
while is_on:
    sc.update()
    ti.sleep(0.1)
    my_sn.move_snake()

    #Detecting Collision with the Food
    if my_sn.head.distance(foo) < 15:
        foo.refresh()
        my_sn.axtend()
        scr.update_score()

    #Detecting Collision with the Wall (Assuming the walls are ar 590*590 and not 600 for clarity)
    if my_sn.head.xcor() > 290 or my_sn.head.ycor() > 290 or my_sn.head.xcor() < -290 or my_sn.head.ycor() < -290:
        is_on = False
        scr.break_game()

    #Colliding with the Tail
    for seg in my_sn.lis[1:]:
        if my_sn.head.distance(seg) < 10:
            is_on = False
            scr.break_game()


sc.exitonclick()