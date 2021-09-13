# from turtle import Turtle, Screen
#
# is_game_on = True
#
#
# def game_end():
#     global is_game_on
#     is_game_on = False
#
#
# SCORE = 0
# screen = Screen()
# screen.setup(width=800, height=700)
# screen.bgcolor("black")
# screen.title("Pong Game")
#
# paddle = Turtle(shape="square")
# paddle.color("white")
# paddle.shapesize(stretch_wid=5, stretch_len=1)
# paddle.pu()
# screen.tracer(0)
# paddle.goto(-350, 0)
#
#
# def down():
#     new_y = paddle.ycor()-20
#     paddle.goto(paddle.xcor(), new_y)
#
#
# def up():
#     new_y = paddle.ycor()+20
#     paddle.goto(paddle.xcor(), new_y)
#
#
# screen.listen()
# screen.onkey(up, "Up")
# screen.onkey(down, "Down")
#
# while is_game_on:
#     screen.update()
# screen.exitonclick()
# Python program to demonstrate
# operator overloading


class Geek():
    def __init__(self, value):
        self.value = value

    def __and__(self, obj):
        print("And operator overloaded")
        if isinstance(obj, Geek):
            return self.value & obj.value
        else:
            raise ValueError("Must be a object of class Geek")

    def __or__(self, obj):
        print("Or operator overloaded")
        if isinstance(obj, Geek):
            return self.value | obj.value
        else:
            raise ValueError("Must be a object of class Geek")

    def __xor__(self, obj):
        print("Xor operator overloaded")
        if isinstance(obj, Geek):
            return self.value ^ obj.value
        else:
            raise ValueError("Must be a object of class Geek")

    def __lshift__(self, obj):
        print("lshift operator overloaded")
        if isinstance(obj, Geek):
            return self.value << obj.value
        else:
            raise ValueError("Must be a object of class Geek")

    def __rshift__(self, obj):
        print("rshift operator overloaded")
        if isinstance(obj, Geek):
            return self.value & obj.value
        else:
            raise ValueError("Must be a object of class Geek")

    def __invert__(self):
        print("Invert operator overloaded")
        return ~self.value


# Driver's code
# if __name__ == "__main__":
#     a = Geek(10)
#     b = Geek(12)
#     print(a & b)
#     print(a | b)
#     print(a ^ b)
#     print(a << b)
#     print(a >> b)
#     print(~a)

def mul(n1, n2):
    return n1 * n2


def test_mul(n1, n2):
    assert mul(n1, n2) <= 30, "multiplication should return less than 30"



if __name__ == "__main__":
    n1 = int(input("n1: "))
    n2 = int(input("n2: "))

    test_mul(n1,n2)
    print("Passed")
