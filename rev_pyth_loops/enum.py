#Introduction to the Enumerate Method in Python
#Syntax is -> enumerate(iterable, start=0)

fruits = ['apple', 'banana', 'cherry']

for index, fruit in enumerate(fruits):
    print(f"Index {index}: {fruit}")