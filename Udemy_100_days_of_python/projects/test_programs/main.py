# class Computer:
#     # locked variable to this class
#     _dummy_var = 10
#
#     def __init__(self):
#         try:
#             self.__maxprice = 900
#             self.sell()
#         except:
#             def SyntaxError():
#                 print("Handled")
#
#     def sell(self):
#         print("Selling Price: {}".format(Computer._dummy_var))
#         print("Selling Price: {}".format(self.__maxprice))
#
#     def setMaxPrice(self, price):
#         self.__maxprice = price
#
#
# c = Computer()
#
# c.sell()
#
# # change the price
#
# c._dummy_var = 1000
# c.__maxprice = 1000
#
# c.sell()
#
# # using setter function
#
# c.setMaxPrice(1000)
#
# c.sell()

class A:
    def __init__(self):
        self.a = 10
        self._b = 5
        print(__class__.__name__)

class B(A):
    def __init__(self):
        super().__init__()
        try:
            print("try")
            print(self.a)
            print(self.b)
            print(__class__.__name__)

        except AttributeError:
            print("Attribute Error Handled")
            print(__class__.__name__)


obj = B()
