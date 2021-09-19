from turtle import Turtle

FONT = ("Courier", 24, "normal")
SCORE_POS = (-250, 250)


class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.level = 0
        self.hideturtle()
        self.penup()
        self.goto(SCORE_POS)
        self.write(f"Level: {self.level}", align="left", font=FONT)

    def game_over(self):
        self.clear()
        self.goto(-100, 0)
        self.write("GAME OVER", align="left", font=FONT)

    def level_up(self):
        self.clear()
        self.level += 1
        self.goto(SCORE_POS)
        self.write(f"Level: {self.level}", align="left", font=FONT)
