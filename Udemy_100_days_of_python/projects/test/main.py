# tup = (1, 2, 3)
# l = list(tup)
# l.append(2)
# print(tuple(l))

# new_l[0] = list_x[-1]
#
# list_x = [2, 3, 4, 5]
# #n=2 list_x = [4,5,0,2,3]
#
#
# print(list_x)


def rotate_element(n, list_n):
    # print(list_n)
    for i in range(4):
        list_n = list_n[-1:] + list_n[:-1]
        # print(list_n)


#
# # print([ele ** 2 for ele in list_x])
# # print([True if 4 in list_x ])
#
# # # rotation
# # def rotate_list(n, list_a):
# #     for i in range(n):
# #         for i,el in enumerate(range(-1, -len(list_x), -1)):
# #             new_l[] = list_a[el]

import time
import random
import matplotlib.pyplot as plt
import pandas as pd

data = pd.DataFrame()
c = []
time_list = []
n_list = []
for i in range(100):
    x = [random.randint(0, 200) for i in range(random.randint(0, 10000))]
    n_list.append(len(x))
    start = time.time()
    for it in x:
        rotate_element(len(x), x)
        # for j in range(it):
        #     for k in range(j):
        #         c.append((it ** 2))
    end = time.time()
    time_list.append(round(abs(end - start), 2))
    print(f"time: {end - start}")
data = pd.DataFrame({"n_list": n_list, "time": time_list})
data = data.sort_values(by="n_list", ascending=True, axis=0)
plt.scatter(data.n_list, data.time)
print(data)
plt.show()

# a = [3, -2, 1, -3]
#
# # Max Product in a contiguous subarray:
# #  1: check for the product to be  > 0
# # facing 0 as element
# # ! getting -ve product of 3 elements -> discard those and move further
# # complexity O(n^2)
# # if negative get product of next number and check whether > 0
#
# pr = 1
# list_pr = []
# for ele in a:
#     for i, e in enumerate(range(1, len(a))):
#         list_pr.append(pr *= ele)
#         if list_pr[i] < 0:
#             if list_pr *= a[i+1] > 0:
#                 list_pr.append(pr * ele)
# print(max(list_pr))
#
# # max([pr*ele if pr*ele > 0 for ele in a])
#
