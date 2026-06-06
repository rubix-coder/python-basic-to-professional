from turtle import Turtle, Screen
import random

is_bet_on = False
screen = Screen()
screen.setup(width=500, height=400)
user_bet = screen.textinput(title="make your bet", prompt="Which turtle will win the race? enter a colour: ")
colours = ["red", "orange", "yellow", "green", "blue", "purple"]
turtles = []
for colour in colours:
    new_turtle = Turtle(shape="turtle")
    new_turtle.color(colour)
    turtles.append(new_turtle)

for y_pos, turtle in enumerate(turtles):
    turtle.pu()
    turtle.goto(x=-230, y=(-150 + (y_pos * 50)))

if user_bet:
    is_bet_on = True

while is_bet_on:
    for turtle in turtles:
        if turtle.xcor() >= 230:
            winning_color = turtle.pencolor()
            if winning_color == user_bet.lower():
                print(f"You won! Winning turtle is: {turtle.pencolor()}")
                is_bet_on = False
            else:
                print(f"You Lost! Winning turtle is: {turtle.pencolor()}")
        else:
            turtle.pu()
            turtle.forward(random.randint(1, 50))

screen.exitonclick()
