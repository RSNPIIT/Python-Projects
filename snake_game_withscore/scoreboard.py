from turtle import Turtle
ALIGNMENT = "center"
FONT = ("Courier", 24, "normal")
fnt = ("Courier",30, "bold")


class Scoreboard(Turtle):

    def __init__(self):
        super().__init__()
        self.score = 0
        with open('text.txt') as d:
            self.highscore = int(d.read())
        self.color("white")
        self.penup()
        self.goto(0, 350)
        self.hideturtle()
        self.update_scoreboard()

    def update_scoreboard(self):
        self.clear()
        self.write(f"Score: {self.score}  High Score: {self.highscore}", align=ALIGNMENT, font=FONT)

    def reset(self):
        if self.score > self.highscore:
            self.highscore = self.score
            with open('text.txt','w') as d:
                d.write(f"{self.highscore}")
        self.score = 0
        self.update_scoreboard()

    def increase_score(self):
        self.score += 1
        self.update_scoreboard()

    def game_over(self):
        self.home()
        self.clear()
        self.write("Game Over", align=ALIGNMENT, font=FONT)

