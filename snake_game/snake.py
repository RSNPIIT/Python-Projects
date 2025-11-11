import turtle as t
m_d = 10
start_pos = [(0,0),(-20,0),(-40,0)]
up,down,left,right = 90,270,180,0

class Snake():
    def __init__(self):
        self.lis = []
        self.make_snake()
        self.head = self.lis[0]

    def make_snake(self):
        for pox in start_pos:
            self.add_position(pox)
            
    def add_position(self,pos):
        timmy = t.Turtle()
        timmy.shape('square')
        timmy.color('white')
        timmy.penup()
        timmy.goto(pos)
        self.lis.append(timmy)

    def axtend(self):
        self.add_position(self.lis[-1].positionw3())

    def move_snake(self):
        for x in range(len(self.lis)-1,0,-1):
            new_x = self.lis[x-1].xcor()
            new_y = self.lis[x-1].ycor()
            self.lis[x].goto(new_x,new_y)
        self.head.forward(m_d)
    
    def up(self):
        if self.head.heading() != down:
            self.head.setheading(90)
            
    def down(self):
        if self.head.heading() != up:
            self.head.setheading(270)

    def left(self):
        if self.head.heading() != right:
            self.head.setheading(180)

    def right(self):
        if self.head.heading() != left:
            self.head.setheading(0)