import numpy as np
import pandas as pd

PRED_VAL = 500
arr = np.linspace(10 ,1500, 150)
print(f"The Array is {arr}\nAnd the Length is {arr.size}")

lis_c = [f'val_{k}' for k in range(140 , 180 , 2)]

print('-'*50)
print("Making this into a Series\n")
lis = [f'val_{j}' for j in range(150 ,0 , -1)]
ser = pd.Series(arr , index = lis ,name = "My Series")

print("Getting the Lowest 10 Prices and Sort them by Index")
print("-"*50)
nser = ser.sort_values(ascending = True).astype('int64')[ :10]

print(f"The Requisite Series is :-\n{nser}\n")
print('-'*50)

print("Now Filtering the Pandas' series....\nLets filter the values greater than our targeted value or the index is in a predefined range\n")
val_srt = ser.sort_index(ascending = True).astype('int64')
mask = (val_srt.index.isin(lis_c)) | (val_srt <= PRED_VAL)
nyl = val_srt.loc[mask]

print(f"The Required Filtered Series is :-\n{nyl.reset_index()}")