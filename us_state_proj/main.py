import turtle as t
import pandas as pd

#Screen Setup
sc = t.Screen()
sc.title("U.S. States Game")
img = "blank_states_img.gif"
sc.addshape(img)
t.shape(img)

#Stack overflow Code to return coordinates (from lines 11 to 17 (Feel Free to Tinker with it ))
# def get_mouse_click_coor(x, y):
#     print(x, y)


# t.onscreenclick(get_mouse_click_coor)
# t.mainloop()

#Extracting data and the states out of it and initializing lists
gu = 0
data = pd.read_csv('50_states.csv')
data_ser = data.state.to_list()
ans_st = []
miss = []

#Game Loop
game_over = False

#Game Starts
while not game_over:
    #Taking the User Input
    ans = sc.textinput(f'{gu}/50 States Correct' , 'Enter the name of the State :-').title()

    #Checking if the State has been Guessed
    if ans in ans_st:
        pass

    #Checking if the user forcefully Exits
    elif ans is None or ans.lower().strip() == 'exit' or ans.lower().strip() == 'quit' or ans.lower().strip() == 'e' or ans.lower().strip() == 'q':
        game_over = True
        break

    #Checking new answers not guessed already
    elif ans in data_ser:
        ans_st.append(ans)
        gu += 1
        x = t.Turtle()
        x.hideturtle()
        x.penup()
        st = data[data.state == ans]
        x.goto(st.x.item() , st.y.item())
        x.write(f'{st.state.item()}')

    #Checking Wrong Answers
    elif ans not in data_ser:
        pass

    #Solved the Quiz 
    if gu == 50 or len(ans_st) == 50:
        game_over = True
        y = t.Turtle()
        y.hideturtle()
        y.penup()
        y.home()
        y.color('black')
        y.write('Victory',align = 'center',font = ("Verdana", 24, "bold"))
        break    
    
sc.exitonclick()

#Displaying summary and unanswered states
print("Sample Summary :-\n")

print(f'Final Score : {gu}')
print(f'Percent Accuracy : {round((gu/50)*100 , 2)}%')

for s in data_ser:
    if s not in ans_st:
        miss.append(s)

print(f"You missed {len(miss)} states")
print("Missed States :-\n")
print(miss)

print('Each Element :(Given for Clarity)\n')
for x in miss:
    print(x)
    
#Giving the unanswered state as a CSV Form (Commented here as this is unrequired - Feel Free to Tinker with it)
# pd.DataFrame(miss).to_csv('states_to_learn.csv',index = False)