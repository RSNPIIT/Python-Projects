#--Importing the Said Module--
import turtle as t
import time as ti

#--- Static Variables ---
FONT_STYLE = 'Arial'

#--- Setup the UI---
sc = t.Screen()
sc.title('Timer Prog')
sc.setup(800 , 800)
sc.bgcolor('black')

#--- Setting up the Timer --- (As its a Turtle)
timmy = t.Turtle()
timmy.hideturtle()
timmy.color('white')
timmy.penup()
timmy.home()

#--- Function to change time
def change_my_time(sec):
    for i in range(sec , 0 , -1):
        timmy.clear()
        if i < 10:
            i = f"0{i}"
        timmy.write(f"{i}" , align = "center" , font = (FONT_STYLE , 80 , 'bold'))
        sc.update()
        ti.sleep(1)

    #After Timer Runs Out <-->
    timmy.color('yellow')
    timmy.clear()
    timmy.write("+!П3'S UΦ" , align = "center" , font = (FONT_STYLE , 85 , 'bold'))

print("Telll Me What Time You wanna count \n")
se = abs(int(input("Enter the Countdown Value : ")))
if se != 0:
    change_my_time(se)
else:
    print("Not Allowed")

sc.exitonclick()