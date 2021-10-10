# def add(*args):
#     return sum(args[-2:])
#
#
# # print(add(2, 3, 4, 5, 6))
#
#
# def calculate(n, **kwargs):
#     n += kwargs["add"]
#     n *= kwargs["multiply"]
#     print(n)
#
#
# calculate(2, add=3, multiply=5)
#
#
# class Car:
#     def __init__(self, **kw):
#         self.make = kw.get("make")
#         self.model = kw.get("model")
#         self.colour =
#
# my_car = Car(make="Nissan")
# print(my_car.model)

x = input()
e, f, r = [int(x) for x in x.split(" ")]
n_e = 0
dr = 0
x = e+f
while x != 0:
    x = x - r + n_e
    n_e = 1
    dr += 1
print(x)
print(dr)
