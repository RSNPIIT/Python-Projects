import turtle as t

#Setup the Screen
sc = t.Screen()
sc.setup( 800 , 800)
sc.bgcolor('black')
sc.title('Shapes Revision')

#Setup the moving turtle
timmy = t.Turtle()
timmy.color('white')
timmy.hideturtle()
timmy.home()

#Make the Shapes
def draw_shape(siz):
    ang = 360 // siz
    for _ in range(siz):
        timmy.forward(100)
        timmy.right(ang)
        
#All Shapes 
for size in range(3 , 11):
    draw_shape(size)

sc.exitonclick()