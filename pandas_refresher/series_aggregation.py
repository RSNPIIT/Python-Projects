import numpy as np
import pandas as pd
import time as ti
import matplotlib.pyplot as plt

# Static Variables
ST = 'int64'
NR = 'nearest'
SSF = 'string'
NF = 'float64'

# Generating the Array here and what's better than to use the Linspace
arr = np.linspace(10 , 1550 , 150)

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
print("Now We Make a Graph --- And My Theory is that it will come out to be Linear (y = mx + c) graph with m = 1 and c = 0 thus y = x at pi/4 rad angle to the x and y axes respectively\n")
ti.sleep(1)
plt.plot(kdx)
plt.title('My Graph')
plt.show()
print("\nThankyou")