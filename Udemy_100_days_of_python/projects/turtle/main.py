from turtle_brain import *

# draw_shape = ShapeDim(int(input("len: ")), int(input("wid: ")))
draw_shape = ShapeDim(random.randint(10, 50), random.randint(1, 10000))

tim.width(2)
draw_shape.spirograph()

screen = Screen()
screen.exitonclick()
