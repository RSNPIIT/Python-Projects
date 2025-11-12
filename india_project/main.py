import turtle as t
import pandas as pd

sc = t.Screen()
sc.title('Indian States Quiz Game')

img = 'ind_map.gif'
sc.addshape(img)
t.shape(img)

gu = 0

data = pd.read_csv('india_states.csv')
d_l = data.state.to_list()
# print(d_l)
ans_st = []
miss = []

game_on = True
while game_on:
    val = sc.textinput(f'{gu}/28 States Correct','Enter the name of the state : ').title()
    x_in = val.strip().lower()
    
    if val is None:
        game_on = False
        break
    
    elif val in ans_st:
        pass
    
    elif x_in in ['exit','quit','e','q']:
        game_on = False
        break
    
    elif val in d_l:
        gu += 1
        ans_st.append(val)
        timmy = t.Turtle()
        timmy.hideturtle()
        timmy.penup()
        st = data[data.state == val]
        timmy.goto(st.x.item() , st.y.item())
        timmy.write(f'{st.state.item()}')

    elif val not in d_l:
        pass
    
    if gu == 28 or len(ans_st) == 28:
        game_on = False
        x = t.Turtle()
        x.hideturtle()
        x.penup()
        x.home()
        x.write('Victory',align = 'center',font = ("Verdana", 24, "bold"))


print('Score Summary :-\n')
print(f'You have identified {gu} states correctly')
print(f'Your accuracy is : {round((gu/28)*100,2)}%')

for z in d_l:
    if z not in ans_st:
        miss.append(z)

print(f'You missed {len(miss)} states')
print(f'The states you missed are : {miss}')

#For clarity
print('The missed states are as follows :\n')
for i in miss:
    print(i)

#Added as an csv
# pd.DataFrame(miss).to_csv('missed_imp_state.csv' , index = False)
sc.exitonclick()