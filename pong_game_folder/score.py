import turtle as t

class Score(t.Turtle):

    def __init__(self):
        super().__init__()
        self.color('white')
        self.score = 0
        self.s1 = 0
        self.s2 = 0
        self.hideturtle()
        self.penup()
        self.goto(0,370)
        self.write(f"Player 1 : {self.s1} Player 2 : {self.s2}", align = 'center' , font = ('Courier',10,'bold'))
    
    def l_update_score(self):
        self.s1 += 1
        self.clear()
        self.write(f"Player 1 : {self.s1} Player 2 : {self.s2}", align = 'center' , font = ('Courier',10,'bold'))

    def r_updare_score(self):
        self.s2 += 1
        self.clear()
        self.write(f"Player 1 : {self.s1} Player 2 : {self.s2}", align = 'center' , font = ('Courier',10,'bold'))

    def a_game_over(self):
        self.clear()
        self.home()
        self.write(f"Game Over \nPlayer 1 wins by {self.s1 - self.s2} points", align = 'center' , font = ('Courier',24,'bold'))

    def b_game_over(self):
        self.clear()
        self.home()
        self.write(f"Game Over \nPlayer 2 wins by {self.s2 - self.s1} points", align = 'center' , font = ('Courier',24,'bold'))    