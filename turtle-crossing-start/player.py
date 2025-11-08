import turtle as t
pos = (0, -380)
y_d = 10
fnish = 370


class Player(t.Turtle):
    
    def  __init__(self):
        super().__init__()
        self.shape('turtle')
        self.penup()
        self.goto(pos)
        self.setheading(90)

    def move_forward(self):
        if self.ycor() < fnish:
            self.forward(y_d)

    def is_at_finishline(self):
        self.goto(pos)