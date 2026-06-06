import random
import turtle
from turtle import Turtle

tim = Turtle()
tim.speed("fastest")
tim.width(2)


class Paint:

    def __init__(self):
        pass

    def hirst(self, x_spots, y_spots, spot_size, spot_gap, colour_list):
        gap = 0
        turtle.setpos(-x_spots, -y_spots)
        for y in range(y_spots):
            for x in range(x_spots):
                tim.hideturtle()
                tim.pd()
                tim.color(random.choice(colour_list))
                tim.dot(spot_size)
                tim.pu()
                tim.forward(spot_gap)
            gap += spot_gap
            tim.setpos(0, turtle.position()[1] + gap)
