from turtle import Turtle
import random


class Food(Turtle):

    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.penup()
        self.shapesize(stretch_len=0.5, stretch_wid=0.5)
        self.color("white")
        self.speed("fastest")
        # (x_pos, y_pos) = (random.randint(-240, 240), random.randint(-240, 240))
        # self.goto(x_pos, y_pos)

    def refresh(self):
        (x_pos, y_pos) = (random.randint(-240, 240), random.randint(-240, 240))
        self.goto(x_pos, y_pos)

