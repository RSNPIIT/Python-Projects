import turtle as t

#Asking as to how big each shape's gonna be
x = abs(int(input("Enter the Size of each shape : ")))

if x <= 100 and x >= 20:
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

    #All Shapes 
    for size in range(3 , 11):
        draw_shape(size)

elif x < 20:
    print("\nToo Small \nCan't Make - This will be invisibe")
else:
    print("\nToo Big \nCan't Make this this will go out of bounds")
    
#Make the Shapes
def draw_shape(siz):
    ang = 360 // siz
    for _ in range(siz):
        timmy.forward(100)
        timmy.right(ang)
        
sc.exitonclick()