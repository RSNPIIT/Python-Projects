import turtle as t 
import random
c = ["red", "orange", "yellow", "green", "blue", "purple"]
STARTING_MOVE_DISTANCE = 5
MOVE_INCREMENT = 10


class CarManager:
    
    def __init__(self):
        self.all_cars = []
        self.c_speed = STARTING_MOVE_DISTANCE

    def create_car(self):
        chnce = random.randint(1,6)
        if chnce == 1:
            new_car = t.Turtle('square')
            new_car.shapesize(1,2)
            new_car.penup()
            new_car.color(random.choice(c)) 
            g_y = random.randint(-350,350)
            new_car.goto(300,g_y)
            self.all_cars.append(new_car)

    def move_car(self):
        for x in self.all_cars:
            x.backward(self.c_speed)

    def inc_speed(self):
        self.c_speed += MOVE_INCREMENT

    