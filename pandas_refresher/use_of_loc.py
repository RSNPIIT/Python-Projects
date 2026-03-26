import numpy as np
import pandas as pd

#First Make a Series shall we ?
arry = np.linspace(10 , 1000 , 15)

print(f"The Array is \n\n{arry}\n and the length is {arry.size}")

#Here is how to basically slice the Series using the Loc operator

lis = [f'val{i}' for i in range(arry.size)]
ser = pd.Series(arry , index = lis, name = 'Series Example')

print(f"Our Series Borrowed from the Numpy Array is \n\n{ser}\n")
print("Now we use the .loc for the Slicing of the List Cause why Not ?\nAs an Exercise we will slice from th 4th Element to the  13th element\n")

print(f"The Corresponding sliced series is \n(NOTE :- I have Converted to int64 for more readability Cause why Not ?)\n{ser.loc['val3' : 'val13'].astype('int')}\n")