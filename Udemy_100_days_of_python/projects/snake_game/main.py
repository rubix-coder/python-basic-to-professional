import time
from turtle import Turtle, Screen
from snake import Snake

screen = Screen()
screen.setup(width=600, height=600)
screen.bgcolor("black")
screen.title("Snake Game")
screen.tracer(0)

my_snake = Snake()

screen.listen()
screen.onkey(my_snake.up, "Up")
screen.onkey(my_snake.down, "Down")
screen.onkey(my_snake.left, "Left")
screen.onkey(my_snake.right, "Right")

is_game_on = True
while is_game_on:
    screen.update()
    time.sleep(0.1)

    my_snake.move()

screen.exitonclick()
