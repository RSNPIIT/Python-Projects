import numpy as np

# Generating a prices array
pric = np.array([45 , 56 , 1 , 27 , 94 , 112 , 34 , 7 , 3 , 49])
items = np.array(['Cola' , 'Fritters' , 'Fryums' , 'Waffles' , 'Coffee' , 'Papadams' , 'Ice-Cream' , 'Burger' , 'Pizza' , 'Pasta'])
samp = np.array(['Potato' , 'Tomato' , 'Bettroot' , 'Potato' , 'Wheat' , 'Bread' , 'Tomato'])

# Now getting the top three from the price
top3pr = np.sort(pric)
top3 = top3pr[-3 :]
print(f"The Price Array is :-\n\n{pric}\nThe top 3 Price Arrays are :-\n{top3}\n\nThe Stats of the same top 3 array are :-\nMean -> {top3.mean().round(2)}\nMax -> {top3.max()}\nMin -> {top3.min()}\nDatatype -> {top3.dtype}\nDimensions -> {top3.ndim}\nShape (aka Number of elements across differing dimensions) -> {top3.shape}\nSize (aka Length for 1D Array) -> {top3.size}\nMedian (aka the Middlemost value) -> {np.median(top3)} ")

# Now Getting the Price where either the price is 50 and above or it corresponds to Fryums
priviet = pric[(pric >= 50) |  (items == 'Fryums')]
print(f"The Prices of Items equal or over 50 or the Fryums category array is :- \n\n{priviet}")

# Calculating the Discounr Amount Given to Prices with Greater than 60 amount
disc = np.where(pric > 60 , 0.1 , 0)
tot_val_arr = pric * (1 - disc)

print(f"The Discount Array is :-\n\n{disc}\nAnd this makes the Total Amount Array as :--\n\n{tot_val_arr}\nWith the Total Amount to be given as {tot_val_arr.sum().round(2)}")

# And Now Getting the Unique items in a Numpy Array for this I made this
val_s = np.unique(samp)
print(f"My Sample Numpy Array is :-\n\n{samp}\nThis has Redundant values\nThe Array with Unique Elements Extracted from the array is :- {val_s}")