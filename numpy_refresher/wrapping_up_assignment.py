import numpy as np
from numpy.random import default_rng

# Initializing the Random number from a large seed
SEED = 2026
rng = default_rng(SEED)

# Hardcoded Family and Sales Array (NOTE -> After Learning Pandas the Code will be updated to take up values from a CSV)
family_array = np.array(['CROP_YEALD' , 'HARVESTING' , 'WATERING' , 'FILTERING' , 'PRODUCE']* 6)
sales_array = np.linspace(10 , 310 , 30)

print(f"The Family Array is :-\n\n{family_array}\nAnd the Sales Array is :-\n\n{sales_array}")

# Taking the Values from Sales corresponding to the Produce item in the family array
prod_array = sales_array[family_array == 'PRODUCE']
random_arr = rng.random(6)

print(f"\nThe Produce Array corresponding to all those values in the sales array corresponding to 'PRODUCE' in the family arrayis :- \n\n{prod_array}\nAccordingly Our Random Array is :-\n\n{random_arr}\n")

prod_val = prod_array[random_arr < 0.5]
print(f"The Produce Value Array having all produce Array Values corresponding to A number less than 0.5 in the Random array is :-\n\n{prod_val}\n")

mean = prod_val.mean()
med = np.median(prod_val)

print(f"\nFor the {prod_val.ndim}D Produce Val Array Given Above -->\nMean -> {mean}\nMedian -> {med}")

# Now Replacing Each Value into Buckets -> (As Median > Mean) of Lesser than Both , Lesser than Median and Greater than Mean , Greater than Both
f_val_ar = np.where(
    prod_val < mean,
    'Lesser than Both Mean and Median',
    np.where(
        prod_val < med,
        'Greater than Mean and Lesser than Median',
        'Greater than Both Mean and Median'
    )
)
print(f"The Final Array Corresponding to the Values in the previous array is :-\n\n{f_val_ar}\n")
print("Thankyou Numpy")