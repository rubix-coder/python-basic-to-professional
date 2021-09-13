from turtle import Turtle


class ScoreBoard(Turtle):

    def __init__(self):
        super().__init__()
        self.score = 0
        self.hideturtle()
        self.color("white")
        self.pu()
        self.goto(-12, 250)
        self.update_scoreboard()

    def update_scoreboard(self):
        self.write(f"Score: {self.score}", align="center", font=("Ariel", 24, "normal"))

    def refresh(self):
        self.score += 1
        self.clear()
        self.update_scoreboard()

    def game_over(self):
        self.goto(0,0)
        self.write("Game Over", align="center", font=("Ariel", 24, "normal"))

