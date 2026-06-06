import random
import time
from turtle import Screen
from player import Player
from car_manager import CarManager
from scoreboard import Scoreboard

screen = Screen()
screen.setup(width=600, height=600)
screen.tracer(0)
screen.title("turtle-crossing")
cars = []
tim = Player()
score = Scoreboard()

screen.listen()
screen.onkey(tim.up, "Up")
screen.onkey(tim.down, "Down")

game_is_on = True
while game_is_on:
    if random.randint(1, 6) == 1:
        cars.append(CarManager())
    time.sleep(0.1)

    for car in cars:
        car.move()
        if car.distance(tim) < 20:
            score.game_over()
            game_is_on = False
        if tim.ycor() > 280:
            score.level_up()
            car.level_up()
            tim.finish()

    screen.update()
screen.exitonclick()
