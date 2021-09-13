import time
from turtle import Screen
from snake import Snake
from food import Food
from score_board import ScoreBoard

is_game_on = True


def game_end():
    global is_game_on
    is_game_on = False


SCORE = 0
screen = Screen()
screen.setup(width=600, height=600)
screen.bgcolor("black")
screen.title("Snake Game")
screen.tracer(0)

my_snake = Snake()
food = Food()
score = ScoreBoard()

screen.listen()
screen.onkey(my_snake.up, "Up")
screen.onkey(my_snake.down, "Down")
screen.onkey(my_snake.left, "Left")
screen.onkey(my_snake.right, "Right")
screen.onkey(game_end, "x")

while is_game_on:
    screen.update()
    time.sleep(0.1)
    my_snake.move()
    if my_snake.head.distance(food) < 15:
        food.refresh()
        my_snake.extend()
        score.refresh()

    if my_snake.head.xcor() > 240 or my_snake.head.xcor() < -240 or \
            my_snake.head.ycor() > 240 or my_snake.head.ycor() < -240:
        is_game_on = False
        score.game_over()

    for segment in my_snake.segments[1:]:
        if my_snake.head.distance(segment) < 10:
            is_game_on = False
            score.game_over()
