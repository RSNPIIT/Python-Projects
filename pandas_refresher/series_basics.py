import numpy as np
import pandas as pd

# Creating the Numpy Array over here
arr = np.linspace(10, 1500, 150)

print(f"The Array is :-\n\n{arr}\n")
print(f"The Status of the {arr.ndim}D Array are :-")
print(f"Size     :- {arr.size}")
print(f"Mean     :- {arr.mean()}")
print(f"Max      :- {arr.max()}")
print(f"Min      :- {arr.min()}")
print(f"Median   :- {np.median(arr)}")
print(f"Shape    :- {arr.shape}")
print(f"Datatype :- {arr.dtype}\n")

# Now saving the array into a Pandas Series
ser = pd.Series(arr, name="Numpy-Pandas Series")

print(f"The Pandas Series is :-\n\n{ser}\n")
print(f"The Data behind this is :-")
print(ser.describe())

# Converting the Datatype from float64 to int64
n_ser = ser.astype('int')

print(f"\nThe Pandas Series After the Datatype change is :-\n\n{n_ser}\n")
print(f"The Details are (Cause I am curious about Pandas methods)")
print(f"Indices  -> {n_ser.index}")
print(f"Values   -> {n_ser.values}")
print(f"Datatype -> {n_ser.dtype}")
print(f"Name     -> {n_ser.name}\n")
print(f"(These are Pandas Stats Methods)")
print(f"Maximum Element -> {n_ser.max()}")
print(f"Minimum Element -> {n_ser.min()}")
print(f"Size            -> {n_ser.size}")
print(f"Mean            -> {n_ser.mean()}")
print(f"Median          -> {n_ser.median()}")