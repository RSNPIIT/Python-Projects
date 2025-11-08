import time
from turtle import Screen
from player import Player
from car_manager import CarManager
from scoreboard import Scoreboard

screen = Screen()
screen.setup(800,800)
screen.tracer(0)
screen.title('My Turtle Game')

sk = Scoreboard()
p = Player()
screen.listen()
screen.onkeypress(p.move_forward,'Up')

cr = CarManager()

game_is_on = True
while game_is_on:
    time.sleep(0.1)
    screen.update()
    cr.create_car()
    cr.move_car()

    for c in cr.all_cars:
        if c.distance(p) < 20:
            game_is_on = False
            sk.g_over()

    if p.ycor() >= 370:
        p.is_at_finishline()
        cr.inc_speed()
        sk.inc_level()

screen.exitonclick()