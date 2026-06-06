import turtle

from color_extractor import extract
from paint import Paint
from turtle import  Screen
my_screen = Screen()
turtle.colormode(255)
colour_list = extract("hirst.jpg", 1000)
print(colour_list)
turtle.hideturtle()


my_painting = Paint()
my_painting.hirst(9, 9, 10, 30, colour_list)


my_screen.exitonclick()

