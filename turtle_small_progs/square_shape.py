#Drawing A Square
import turtle as t

#User Will determine How Much the Turtle will move
x = abs(int(input("Enter the Value as to how much the Turtle will move : ")))
UP = 90

#Setting Up the Screen
sc = t.Screen()
sc.title("Turtle Moves")
sc.setup( 800 , 800 )

#Setting up our moving turtle
timmy = t.Turtle()
timmy.hideturtle()
timmy.color('coral')

for _ in range(4):
    timmy.forward(x)
    timmy.right(UP)

sc.exitonclick()