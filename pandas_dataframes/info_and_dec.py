import numpy as np
import pandas as pd

# Static Variables
INC = 'all'

# Making the Numpy Array here
arr = np.random.rand(100 ,5)
print(f"Our numpy array is :-> {arr}")

# Now Making this into a dataframe here
df = pd.DataFrame(
    data = arr,
    index = [f'Row_{i + 1}' for i in range(100)],
    columns = [f'Column_{i + 1}' for i in range(5)]
)
print(f"We made our dataframe it is :-\n{df}\n")

# Finding out the Empty Erroneous Values in the dataFrame
blank = df.isna().sum().sum()
print(f"There are {blank} np.NaN values in the dataframe")

# Getting an information of the dataframe
print(f"The DataFrame Information are :-> \n")
df.info()

# Getting the description of all columns in the dataframe
df_col = df.describe(include = INC)
print(f"The Desctiption of the DataFrame columns are :-> \n{df_col}\n")