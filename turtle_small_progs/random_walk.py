import turtle as t
import random as r

#Lists
# colors = ['yellow' , 'blue' , 'red' , 'green' , 'white', 'lime' , 'coral' , 'grey']
dirn = [0 , 90 , 180 , 270 ]

t.colormode(255)
#Setting up the Screen
sc = t.Screen()
sc.bgcolor('black')
sc.setup( 800 , 800 )

#Turtle Setup
timmy = t.Turtle()
timmy.hideturtle()

#RGB Random Color Function
def rgb_p():
    re = r.randint(0 , 255)
    gr = r.randint(0 , 255)
    bl = r.randint(0 , 255)
    return (re , gr , bl)

for _ in range(100):
    timmy.color(rgb_p())
    timmy.width(15)
    timmy.forward(30)
    timmy.setheading(r.choice(dirn))

sc.exitonclick()