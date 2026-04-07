import math as m
import numpy as np
import pandas as pd
import time as ti
import matplotlib.pyplot as plt

# Static Variables
ST = 'int64'
SRT = 10
NR = 'nearest'
SSF = 'string'
NF = 'float64'
SLP = round(1540 / 149 , 3)
RAD = m.atan(SLP)
DEG = m.degrees(RAD)

# Generating the Array here and what's better than to use the Linspace
arr = np.linspace(SRT , 1550 , 150)

print(f"We have generated the {arr.ndim}D array here\nThe Size is {arr.size}\nThe Shape (i.e in each dimension the number of elements) {arr.shape}\nThe sum is {arr.sum()} and the Mean is {arr.mean()}")
idx = [f'v{i}' for i in range(arr.size)]

# We will Now Obtain the Percentile but it is a Pandas Method
ser = pd.Series(arr , index = idx , name = 'My Series').astype(ST)
val = '₹ ' + ser.quantile([0.1 , 0.9] , interpolation = NR).astype(NF).astype(SSF)

print(f"The Said Quantile is -> \n\n{val}")

# We will now compute the probability distribution here
# sop = val.str.replace('₹' , '').str.strip().astype(NF).value_counts(normalize = True)
sop = ser.value_counts(normalize = True)
print(f"The Probability Distribution is :- \n\n{sop}")

# Now We Will reset the index cause
kdx = ser.reset_index(drop = True)
print(f"Now We Make a Graph\nIt will come out to be linear (y = mx + c) form with m (aka Slope) = {SLP} and c (aka Intercept) = {SRT}\nWith Angle to the x axis being {DEG}° and Angle to the y axis being {90 - DEG}° respectively\n")
ti.sleep(1)
plt.plot(kdx)
# This Line below What this does it - It forces MatPlotLib Module to ensure 1 unit of x ensures 1 unit of y
# plt.gca().set_aspect('equal', adjustable='box')
plt.title('My Graph')
plt.show()
print("\nThankyou")