import numpy as np
import pandas as pd
import os as o
import time as ti

LIS = o.listdir()
FILE = 'annomaly.csv'
NFILE = 'clean_annomaly.csv'

if FILE in LIS:
    df = pd.read_csv(FILE)
    print(f"The Dataset has been loaded\nIt looks like this ->\n{df.head()}")
    print(f"Original Dataset shape is -> {df.shape}")
    print(f"Original Dataset size is -> {df.size}")

    print(f"Starting cleaning ......")
    ti.sleep(1)

    df.replace([np.inf, -np.inf, 'inf', '-inf', 'NaN'], np.nan, inplace=True)
    df.drop_duplicates(inplace = True)
    df.drop_duplicates(
        subset = ['Emp_ID'],
        keep = 'first',
        inplace = True
    )
    df['Age'] = df['Age'].fillna(df['Age'].median())
    df['Experience'] = df['Experience'].fillna(df['Experience'].median())
    df['Salary'] = df['Salary'].astype(float)
    df['Salary'] = df.groupby('Department')['Salary'].transform(lambda x: x.fillna(x.median()))
    df['Salary'] = '₹' + df['Salary'].astype(str)
    
    df['Performance Rating'] = df['Performance Rating'].astype(float)
    df['Performance Rating'] = df.groupby('Department')['Performance Rating'].transform(lambda x: x.fillna(x.mean()))
    df['Performance Rating'] = df['Performance Rating'].round(2)

    df['Emp_ID'] = df['Emp_ID'].astype(int)
    df['Age'] = df['Age'].astype(int)
    df['Experience'] = df['Experience'].astype(int)

    print(f"\nDataset has been cleaned comfortably :->\n{df.head()}")
    df.to_csv(
        NFILE,
        index = False
    )
else:
    print("The File is not found here at all")