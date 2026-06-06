import random
import turtle
from turtle import Turtle, Screen

tim = Turtle()
tim.shape("turtle")
tim.color("DarkGreen")
tim.speed("fastest")
Screen().screensize(canvwidth=100, canvheight=100)
turtle.colormode(255)


class ShapeDim:

    def __init__(self, length, width):
        """ Input length and width for the shape consider radius = length for radial shapes """
        self.length = length
        self.width = width
        self.shape_list = [3, 4, 5, 6, 7, 8, 9]
        self.colour = ["red", "green", "blue", "DarkGreen", "black", "orange", "purple", "yellow"]
        self.movements = [0, 90, 180, 270]

    def square(self):
        """Draws a square of length"""
        for i in range(4):
            tim.forward(self.length)
            tim.right(90)

    def rectangle(self):
        """Draws a rectangle of length"""
        for i in range(2):
            tim.forward(self.length)
            tim.right(90)
            tim.forward(self.width)
            tim.right(90)

    def dashed_line(self):
        """Draws a dashed line of length"""
        for i in range(self.length):
            tim.pd()
            tim.forward(5)
            tim.pu()
            tim.forward(5)

    def all_shapes(self):
        """Draws a triangle, square, pentagon, polygon up to 10 sides  of length"""

        for edges in self.shape_list:
            tim.color(random.choice(self.colour))
            for i in range(edges):
                tim.forward(self.length)
                tim.right(360 // edges)

    def random_walk(self):
        """Draws a random walking scenario"""
        for i in range(self.width):
            tim.color((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            tim.forward(self.length)
            tim.setheading(random.choice(self.movements))

    def spirograph(self):
        """Draws a spirograph"""
        for i in range((360//self.length)):
            tim.color(random.choice(self.colour))
            tim.circle(60)
            tim.setheading(tim.heading()+self.length)
