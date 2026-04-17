import pandas as pd
import numpy as np

# Pandas data Types here -> 
# NOTE = Used np.nan as pd.NA are still in early stages and they default to np.nan
ser = pd.Series([
    10, 25, 30, np.nan, 45,
    50, 65, 70, 85,
    90, np.nan, 110, 120,
    140, 155, np.nan, 175, 190,
    205, 225, 240, np.nan,
    260, 275, 290, 310
] ).astype('float64')

print(f'The {ser.ndim}D series is :- \n{ser}\nThe size of this serset is :-> {ser.size}')

# Pandas Methods to Work with Missing Values 
print(f"\nLets Calculate the Number of Missing Values in the series :- \nAfter Analysis Pandas (PyPI) found out that the number of missing values are -> {ser.isna().sum()}")

# Now We will drop the Missing Values
# Method used are -> [dropna()] = It returns the new series and the original series stays intact
std_ser = ser.dropna()
print(f"\nLets Drop the NA & NAN Values ->\n{std_ser}")

# After Dropping we basically Replace the NA & NAN Values with the Median of the Series
# Method(s) used are -> [fillna() , median()] = It modifies the list in place and doesnt return a new series
medi = ser.median()
print(f"\nLets fill the NA values here ->\n\nFor an example we fill up with the median value of the Series -> {medi}\nThe Series becomes\n{ser.fillna(medi)}")