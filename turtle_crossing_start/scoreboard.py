import turtle as t
FONT = ("Courier", 24, "normal")
ft = ("Courier", 30, "normal")

class Scoreboard(t.Turtle):
    
    def __init__(self):
        super().__init__()
        self.level = 1
        self.color('black')
        self.hideturtle()
        self.penup()
        self.goto(-350,350)
        self.update_scr()

    def update_scr(self):
        self.clear()
        self.write(f"Level : {self.level}", align = 'left', font = FONT)
    
    def inc_level(self):
        self.level += 1
        self.update_scr()

    def g_over(self):
        self.home()
        self.write("Game Over", align = 'center', font = ft)
