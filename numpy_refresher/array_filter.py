import numpy as np

# Generating the Array for the prices of goods
val = np.linspace(10 , 101 , 10)

# Generating an Array for the Items List
items = np.array(['Cola' , 'Fritters' , 'Fryums' , 'Waffles' , 'Coffee' , 'Papadams' , 'Ice-Cream' , 'Burger' , 'Pizza' , 'Pasta'])

# Displaying the Output
print(f"The Prices Array is :-\n{val}\nAccordingly the Items Array is :-\n{items}")

# Displaying the Price of those items which are Greater than 50 or the Item is Cola
arr = items[(val >= 50) | (items == 'Cola')]
print(f'The Said Array containing the prices greater than 50INR OR Cola is :- \n{arr}')

shipping_cost = np.where(val >= 60 , 0 , 5)
print(f'The Shipping cost array consisting of Free Shipping above 60 INR and 5 INR Otherwise is :-> {shipping_cost}\nThe Summation of the Array (i.e the total shipping cost) is {shipping_cost.sum()}')