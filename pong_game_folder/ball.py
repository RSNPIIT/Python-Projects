import turtle as t

class Ball(t.Turtle):
    def __init__(self):
        super().__init__()
        self.color('white')
        self.shape('circle')
        self.penup()
        self.dx = 10
        self.dy = 10
        self.delay = max(self.delay * 0.9, 0.02)

    def move(self):
        self.goto(self.xcor() + self.dx , self.ycor() + self.dy)

    def bounce_x(self):
        self.dx *= -1
        
    def bounce_y(self):
        self.dy *= -1