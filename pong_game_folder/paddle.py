import turtle as t

class Paddle(t.Turtle):
    def __init__(self , pos):
        super().__init__()
        self.color('white')
        self.shape('square')
        self.shapesize(5,1)
        self.penup()
        self.goto(pos)

    def go_up(self):
        if self.ycor() < 350:
            self.sety(self.ycor() + 20)

    def go_down(self):
        if self.ycor() > -350:
            self.sety(self.ycor() - 20)