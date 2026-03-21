import numpy as np
from numpy.random import default_rng

rng = default_rng(12345)

prices = np.arange(10 , 1001 , 10)
ary = rng.random(20)

print(f"The Prices Array is :-\n\n{prices} and it has a size of {prices.size}`\nAnd the Discount Array is :-\n\n{ary} and it has a size of {ary.size}")

price = prices.reshape(10 , 10)
pct_ar = ary.reshape(2 , 10)

print(f"After Resizing the Prices Array Becomes :- \n\n{price}\nAnd After Resizing the Discount Array becomes :- \n\n{pct_ar}")

# Extracting the First Row from each
price = price[0 , :]
pct_ar = pct_ar[0 , :] 
res_m = price * (1 - pct_ar)

print(f"\nThe Original price array is \n\n{price}\nThe Discount Array is \n\n{pct_ar}\n\nThe Final price array is {res_m} and the Sum is {res_m.sum()}")