import turtle as t
import random

sc = t.Screen()
u_bet = sc.textinput("Make your Bet ?","Which turtle will win the Race (Enter the Color here)? : ")
colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple']
y_pos = [-90,-60,-30,0,30,60]
all_turtles = []

is_race_on = False

for i in range(6):
    timmy = t.Turtle()
    timmy.shape('turtle')
    timmy.color(colors[i])
    timmy.penup()
    timmy.goto(-300,y_pos[i])
    all_turtles.append(timmy)

if u_bet:
    is_race_on = True

while is_race_on:
    for tux in all_turtles:
        if tux.xcor() > 300:
            is_race_on = False
            win_clr = tux.pencolor()
            if win_clr == u_bet:
                print(f"Correct , The Winning Turtle is : {win_clr.title()} turtle")
            else:
                print(f"Aah I'm sorry , The Winning Turtle is {win_clr.title()}")
            break
        r_d = random.randint(1,10)
        tux.forward(r_d)    
        
sc.exitonclick()