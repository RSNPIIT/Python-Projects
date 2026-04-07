import random as r
import numpy as np
import pandas as pd
import time as ti
import matplotlib.pyplot as plt

# Creating the Series Here
MAX_VAL = 150
lis = [r.randint(150 , 245) for _ in range(MAX_VAL)]
# ins = [f'{i}' for i in range(MAX_VAL)]
ser = pd.Series(lis , name = 'Sample Series').astype('float64')

# Now Getting the MaxValue of the series
print(f"The Pandas Series is :-\n\n{ser}\n")
sval = ser.max()
print(f"The Maximum Element is {sval}\n")

# Raising the Prices of the Goods by 10% and adding 10INR further
ser = np.round(ser * 1.1 + 10 , 3)
ser = '₹' + ser.astype('string')
print(f"The New Series Formed by Adding 10% to each element and then adding 10 INR is ->\n\n{ser}")

# And Now the Percentage as to what percentage of ser's element are forming the max
vag = ser.str.replace('₹' , '').astype('float64')
prc = np.round((abs(vag - sval) / sval) * 100 , 3)
prc = prc.astype('string') + '%'
prk = prc.reset_index(drop = True)

print(f"The Percent Share of the Elements is \n\n{prc}\nAnd also we can reset the index here\n\n{prk}")

# Making a beautiful analysis of the Values of the Percentages
krp = prc.str.replace('%' , '').astype('float64').astype('int64')
aly = np.where(
    krp <= 5,
    'High Contribution',
    np.where(
        krp <= 15,
        'Moderate Contribution',
        'High Contribution'
    )
)
print(f"The Analysis is Done :- It Has been found out that the Results are this :-\n{aly}")

print("Generating the Visual Element of the Series Here ----\n")
ti.sleep(1)
plt.plot(vag)
plt.title('My Series')
plt.show()