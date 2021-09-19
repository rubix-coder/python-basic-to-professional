from turtle import Turtle, Screen
from paddle import Paddle
from ball import Ball
from scoreboard import Scoreboard
import time

is_game_on = True


def game_end():
    global is_game_on
    is_game_on = False


POSITIONS = [(350, 0), (-350, 0)]

SCORE = 0
screen = Screen()
screen.setup(width=800, height=600)
screen.bgcolor("black")
screen.title("Pong Game")
screen.tracer(0)

r_paddle = Paddle(POSITIONS[0])
l_paddle = Paddle(POSITIONS[1])
ball = Ball()
score = Scoreboard()

screen.listen()
screen.onkey(r_paddle.up, "Up")
screen.onkey(r_paddle.down, "Down")

screen.listen()
screen.onkey(l_paddle.up, "w")
screen.onkey(l_paddle.down, "s")

while is_game_on:
    time.sleep(ball.move_speed)
    screen.update()
    ball.move()
    # detect collision with wall
    if ball.ycor() > 280 or ball.ycor() < -280:
        ball.bounce_y()

    if ball.distance(r_paddle) < 50 and ball.xcor() > 320 or ball.distance(l_paddle) < 50 and ball.xcor() < -320:
        print("made contact")
        ball.bounce_x()

    if ball.xcor()>380:
        print("missed the ball")
        ball.reset_position()
        score.l_point()

    if ball.xcor()<-380:
        print("missed the ball")
        ball.reset_position()
        score.r_point()

screen.exitonclick()
