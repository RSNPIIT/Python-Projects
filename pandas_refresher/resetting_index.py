import numpy as np
import pandas as pd
import os as o
import sys as s
import time as ti

# Static Variables
NAME = 'Custom Series'
print("So This is All About Creating Unique Indeces and then Resetting Them")

# Generating the Array
arr = np.linspace(150 , 2015 , 60)
print(f"The Generated Array is \n\n{arr}\nThe Length of this Array is {arr.size}")

# Now Converting the Array to a Pandas Series
print(f"\nConverting this to a Pandas Series Cause Why Not ??\nAnd We give our own Custom Indices\n")
idex = [f'val{i}' for i in range(arr.size)]
ser = pd.Series(arr , index = idex , name = NAME)
print(f"The Said Series is :-\n\n{ser}\n")

try:
    a = abs(int(input("Enter the Value of the starting slice index (in int64 form) : ")))
    b = abs(int(input("Enter the Value of the ending slice index (in int64 form) : ")))

    if a > b or a >= arr.size or b >= arr.size or (a == 0 and b == 0):
        print("These Values Are Invalid in Slicing Owing to which You cant Proceed")
        ti.sleep(1)
        o.system('cls' if o.name == 'nt' else 'clear') 
        s.exit()
except (KeyboardInterrupt , EOFError) as kb:
    print("\nExitting----\nPlease Dont Spam")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear') 
    s.exit()
except ValueError as v:
    print("\nThe Non Integral Values are not allowed here\n")
    ti.sleep(1)
    o.system('cls' if o.name == 'nt' else 'clear')
    s.exit()

# Now We Select a Random Value As a Slicing Example 
new_ser = ser.loc[f'val{a}' : f'val{b}']
print(f"The New Series is this :=\n\n{new_ser}\nStats :- \nThis has the Length of {new_ser.size}\nMean Value of {new_ser.mean()}\nMax Value of {new_ser.max()}\nAnd Minimum Value of {new_ser.min()}\nAnd a Median Value of {new_ser.median()}")

# Resetting the Index temporarily
print(f"But Did You see something the Indices\nHow About we Change the Indices to Default and yes we can do so....\nThats the Power of Open Source\n")
print(new_ser.reset_index())

# Now Making the Reset Permanent
print(f"\nLook How good this looks\nMaking this permanent\n\n{new_ser.reset_index(drop = True).astype('int64')}")