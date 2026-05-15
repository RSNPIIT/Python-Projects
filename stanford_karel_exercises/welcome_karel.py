from karel.stanfordkarel import *

# File: shelter.py
# -----------------------------
# The warmup program defines a "main"
# function which should make Karel 
# move to the beeper, pick it up, and
# return home.
def main():
    while front_is_clear():
        move()
    turn_right()
    move()
    turn_left()
    move()
    pick_beeper()
    turn_left()
    turn_left()
    move()
    turn_left()
    turn_left()
    move()
    turn_left()
    turn_left()
    while front_is_clear():
        move()
    turn_left()
    # add your code here
    
def turn_right():
    turn_left()
    turn_left()
    turn_left()
    
# don't edit these next two lines
# they tell python to run your main function
if __name__ == '__main__':
    main()
