import numpy as np

#1D Arrays
lis = [x for x in range(1,11)]
myl = np.array(lis)
print(f"The {myl.ndim}D Array status :-\nList :- {lis}\nArray :- {myl}\nSize :- {myl.size}\nShape (i.e - The Elements in each dimension) :- {myl.shape}\nDatatype of the elements :- {myl.dtype}\n")

#2D Arrays
lys = [
    [y for y in range(1, 20)] ,
    [z for z in range(1, 10)]
    ]
try:
    print(np.array(lys))
except ValueError as v:
    print(f"This shows that unequal lengthed datatypes can't form Numpy Arrays as in the example of :- \n{lys}\n")

lks = [
    [y for y in range(21)],
    [z for z in range(21)]
]
kde_arr = np.array(lks)
print(f"The {kde_arr.ndim}D Array status is :-\nList :- {lks}\nArray :- {kde_arr}\nSize :- {kde_arr.size}\nShape :- {kde_arr.shape}\nDatatype :- {kde_arr.dtype}\n")

#What if I give a mixed List
mli = ['I' ,'am' ,'from' ,'Bharat']
kar = np.array(mli)
print(f'For the Mixed List :- {mli}\nThe Array is :- {kar}\nThe Dimension is :- {kar.ndim}\nThe Size is :- {kar.size}\nThe Shape is :- {kar.shape}\nThe Datatype is :- {kar.dtype}')