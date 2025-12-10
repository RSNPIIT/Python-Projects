import turtle as t
import random as r

#Setting the Mode to 255 in order to take tuples
t.colormode(255)

#Screen Setup
sc = t.Screen()
sc.setup(800 , 800)
sc.title('Spirograph')
sc.bgcolor('black')

#Turtle Setup
timmy = t.Turtle()
timmy.hideturtle()
timmy.home()
timmy.width(5)
timmy.speed('fast')

#Rgb Color
def regb():
    re = r.randint(0 , 255)
    gr = r.randint(0 , 255)
    bl = r.randint(0 , 255)
    return (re , gr , bl)

#Spirograph
side = 5
for _ in range(360 // side):
    timmy.color(regb())
    timmy.circle(100)
    timmy.setheading(timmy.heading() + 10)

sc.exitonclick()