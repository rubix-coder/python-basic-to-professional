import time
import random
import matplotlib.pyplot as plt
import pandas as pd

data = pd.DataFrame()
c = []
time_list = []
n_list = []
for i in range(100):
    x = [random.randint(0, 100) for i in range(random.randint(0, 10000))]
    n_list.append(len(x))
    start = time.time()
    for it in x:
        for j in range(it):
            c.append((it ** 2) * 2 * j)
    end = time.time()
    time_list.append(round(abs(end - start), 2))
    print(f"time: {end - start}")
data = pd.DataFrame({"n_list": n_list, "time": time_list})
data = data.sort_values(by="n_list", ascending=True, axis=0)
plt.scatter(data.n_list, data.time)
print(data)
plt.show()
