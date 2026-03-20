import numpy as np
import pprint as pp

# Making our array without any list then resizing it
val_ar = np.arange(10 , 1000 , 25)
print('The (Initl.) Array is :->\n')
pp.pprint(val_ar)
print(f'\nIt has a length of {val_ar.size}\n')

# Lets Resize this shall we
r_arr = val_ar.reshape(4 , 10)
pp.pprint(r_arr)

# Getting the First Two Rows
r1 = r_arr[ :2 , : ]
print("\nThe First two Rows in this Array is :-\n")
pp.pprint(r1)

# Getting the First Column
r2 = r_arr[ : , 0]
print("\nThe First column in this Array is :-\n")
pp.pprint(r2)

# Getting the Second Number in the third row 
r3 = r_arr[ 2 , 1 ]
print(f"\nThe Said Element in the Third row is {r3}\n")