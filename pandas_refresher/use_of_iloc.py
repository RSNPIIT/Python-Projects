import pandas as pd

# The Index to do
lis = [f'val{i}' for i in range(1 , 6)]
ser = pd.Series([1 , 2 , 3 , 4 , 5] , index = lis ,name = 'My Series')
print(f"The Series We made is :- \n{ser}\n")

# Now We use the I-Loc Operator 
print("Now will demonstrate how we access an element via iLoc Operator\nFor an example Lets Access from the 2nd pos. Element to the 4th pos. \nNOTE :- In iloc slicing, the last index is NOT included (Python-style slicing)")
print(f"The Said Series is :- \n{ser.iloc[1 : 4]}")