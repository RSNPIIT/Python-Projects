import turtle as t

x = abs(int(input("Enter the Value of how much you're gonna move : ")))

#Screen Setup
sc = t.Screen()
sc.setup(800 , 800)
sc.title('Dotted Line')
sc.bgcolor('black')

#Turtle Setup
timmy = t.Turtle()
timmy.hideturtle()
timmy.color('white')

for _ in range(10):
    timmy.penup()
    if x > 50:
        timmy.forward(x // 2)
    else:
        timmy.forward(x)
    timmy.pendown()
    if x > 50:
        timmy.forward(x // 2)
    else:
        timmy.forward(x)

sc.exitonclick()