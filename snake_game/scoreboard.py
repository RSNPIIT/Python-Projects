import turtle as t
class Scoreboard(t.Turtle):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.color('white')
        self.hideturtle()
        self.penup()
        self.goto(0,270)
        self.write(f"Score = {self.score}", align = 'center' , font = ('Courier',10,'bold'))
    
    def update_score(self):
        self.score += 1
        self.clear()
        self.write(f"Score = {self.score}", align = 'center', font = ('Courier',10,'bold'))
    
    def break_game(self):
        self.goto(0,0)
        self.write(f"Game Over", align = 'center' , font = ('Courier',15,'bold'))