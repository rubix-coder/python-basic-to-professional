from turtle import Turtle, Screen

tim = Turtle()
screen = Screen()
tim.speed("fastest")

def forward():
    tim.forward(10)


def backward():
    tim.backward(10)


def counter_clock():
    tim.left(10)


def clock():
    tim.right(10)


def clear():
    tim.clear()
    tim.pu()
    tim.home()
    tim.pd()


screen.listen()
screen.onkey(key="w", fun=forward)
screen.onkey(key="s", fun=backward)
screen.onkey(key="a", fun=counter_clock)
screen.onkey(key="d", fun=clock)
screen.onkey(key="c", fun=clear)
screen.listen()

screen.exitonclick()
