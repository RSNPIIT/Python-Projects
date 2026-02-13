import functools as fc

#Lambda with sorted function
lis = [[5,6,7],[1,2,3],[7,8,9],[-1,9,6]]
n_l = sorted(lis , key = lambda x : x[1])
print(f"The New List is : {n_l}")

#Lambda with Map Function
lis = [56 , 78 , 94 , 112 , 450 , 75 , 47 , 63]
nkl = list(map(lambda x : x ** 2 , lis))
print(f"The Squared List is : {nkl}")

#using Lambda Map to convert celcius to fahrenheit (used when we want  complete list)
tlis = [0 ,20 ,37 , 100]
nl = list(map(lambda x : round((x * 1.8) + 32, 3) , tlis))
print(f"The Fahrenheit List is : {nl}")

#Using Lambda with Filter Function
ljis = [56 , 78 , 94 , 112 , 450 , 75 , 47 , 63]
ev_l = list(filter(lambda x : abs(x) % 2 == 0 , ljis))
print(f"The Even List is : {ev_l}")

#Using Lambda with Reduce Function (Used when we want a single value)
lkis = [56 , 78 , 94 , 112 , 450 , 75 , 47 , 63]
eva = fc.reduce(lambda x,y : x * y , lkis)
print(f"The Product of the list Elements is : {eva}")