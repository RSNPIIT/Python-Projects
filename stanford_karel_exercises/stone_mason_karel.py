from karel.stanfordkarel import *

"""
File: main.py
--------------------
When you finish writing this file, Karel should have repaired 
each of the columns in the temple
"""

def main():
    """
    You should write your code to make Karel do its task in
    this function. Make sure to delete the 'pass' line before
    starting to write your own code. You should also delete this
    comment and replace it with a better, more descriptive one.
    """
    do_it()

def do_it():
    for _ in range(4):
        turn_left()
        while front_is_clear():
            move()
        rotate()
        while front_is_clear():
            put_beeper()
            move()
        put_beeper()
        turn_left()
        if front_is_clear():
            jump()

def rotate():
    turn_left()
    turn_left()

def jump():
    for _ in range(4):
        move()
    
if __name__ == '__main__':
    main()
