import matplotlib.pyplot as plt
import math

def sig(x):
    return 1 / (1 + math.exp(-x))


plt.plot([sig(x) for x in range(-10, 10)])
plt.show()