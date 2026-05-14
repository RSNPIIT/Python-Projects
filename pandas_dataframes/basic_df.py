import numpy as np
import pandas as pd

# Static Variables
FRAC = 0.2

# Making a Numpy Array here
arr = np.random.rand(100, 5)
print(f"Our Numpy Array is -> \n{arr}")

# Conversion to a Pandas dataFrame
print("Now we make this into a pandas dataframe ->")
df = pd.DataFrame(
    data = arr,
    columns = [f'Approximation_{i+1}' for i in range(5)],
    index = [f'Index_{i+1}' for i in range(100)]
)

# Now Extracting our things from the Rows and columns
print(f"The DataFrame is Loaded\nIt is :->\n{df}")
rows = df.index
cols = df.columns
size = df.shape
dgh = df.dtypes

print(f"Summary is this :->\nThe Rows are :-> \n{rows}\nThe Columns are :-> \n{cols}\nThe Dimensions are :->\n{size}\nThe datatypes are :-> {dgh}\n")

# Now Using the Head , Tail and the Sample Method
hd = df.head(5)
tl = df.tail(5)
t20 = df.sample(frac = FRAC)
print(f"The First 5 Rows are :-> \n{hd}\nThe Last 5 Rows are :-> \n{tl}\n20% of the sum total rows are :-> \n{t20}\n")