import numpy as np
import time as ti
import os as o
import sys as s
from numpy.random import default_rng

# Getting the Random Array with a Seed
rng = default_rng(12345)

# Getting the array done without a list (aka -> ARange , Linspace , Integers ,RNG)
n1 = np.linspace(10 , 100 , 10)
n2 = np.arange(10 , 101 , 10)
n3 = rng.integers(10 , 101 , 100)
n4 = rng.random(9)

# Defining the function to do everything without having to repeat
def auth_it(arr):
    print(f"\nFor the Array :- {arr}\n")
    try:
        a = abs(int(input("Enter the value of the x re-assignment axis : ")))
        b = abs(int(input("Enter the value of the y re-assignment axis : ")))
    except (KeyboardInterrupt , EOFError) as kb:
        print(f"Please dont spam\nExitting....")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()
    except ValueError as v:
        print(f"Non Integer Values are not allowed here\n")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear')
        s.exit()

    if a > 0 and b > 0 and a * b == len(arr):
        nas = arr.reshape(a , b)
    else:
        print(f"The values of X-axis -> {a} and Y-axis -> {b} are not allowed \nRedirecting to the standard value\n")
        nas = arr
    print(f"The Reshaped {nas.ndim}D array is :- {nas}\nThe Status is :-\nSize -> {nas.size}\nShape -> {nas.shape} \nThe Datatype is -> {nas.dtype}")

# Printing the Status for all the array
arrs = [n1 , n2 , n3 , n4]
for arr in arrs:
    auth_it(arr)
