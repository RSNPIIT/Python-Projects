import numpy as np
import pandas as pd

data = pd.read_csv('annomaly.csv')
print(data.head(6))

print("\nMissing Values in Each Column :- \n")
print(data.isnull().sum())

# Remove inf / -inf first
data.replace([np.inf, -np.inf], np.nan, inplace=True)

# Fill numeric columns only
numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].mean())

# Fill Performance Rating separately (optional)
if 'Performance Rating' in data.columns:
    data['Performance Rating'] = data['Performance Rating'].fillna(data['Performance Rating'].median())
