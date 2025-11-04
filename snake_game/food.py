import turtle as t
import random

class Food(t.Turtle):
    def __init__(self):
        super().__init__()
        self.shape('circle')
        self.color('blue')
        self.penup()
        self.speed('fastest')
        self.shapesize(0.5,0.5)
        self.goto(random.randint(-280,280),random.randint(-280,280))
        self.refresh()
    
    def refresh(self):
        self.goto(random.randint(-280,280),random.randint(-280,280))
