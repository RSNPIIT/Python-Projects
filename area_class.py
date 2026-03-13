import turtle as t
import time as ti
import os as o

class Circle():
    def __init__(self , rad):
        self.pi = 3.141
        self.rad = rad
    
    def area(self):
        return self.pi * (self.rad ** 2)
    
    def per(self):
        return 2*self.pi*self.rad

try:
    ra = abs(float(input("Enter the Radius Here :")))
except (KeyboardInterrupt, EOFError):
    print("\nProgram stopped by user or end of input.\nExitting")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    print("\nDone .....\n")
    exit()
except ValueError as v:
    print("\nNon Integral Values Given\n")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    exit()
else:
    myX = Circle(ra)
    print(f"The Area is : {myX.area()} ")
    print(f"The Circumference is : {myX.per()} ")


    print("\nVisualizing the Circle ->\nModule Loading....")
    ti.sleep(1)
    print("\nModule Loaded....\nProceeding....")
    ti.sleep(1)
    print("\nDone")

    sc = t.Screen()
    sc.setup(800 , 800)
    sc.title('Circle Visualizing')
    sc.bgcolor('black')

    timmy = t.Turtle()
    timmy.color("yellow")
    timmy.pensize(3)
    timmy.circle(ra)

    sc.exitonclick()
finally:
    print("This is the Circle")
