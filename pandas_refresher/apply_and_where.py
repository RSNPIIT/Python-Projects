import numpy as np
import pandas as pd

# Our Series is this
ser = pd.Series([
    10, 25, 30, np.nan, 45,
    50, 65, 70, 85,
    90, np.nan, 110, 120,
    140, 155, np.nan, 175, 190,
    205, 225, 240, np.nan,
    260, 275, 290, 310
] ).astype('float64')

def buy_bool(prc , lim):
    if prc < lim:
        return "Buy" 
    return "Wait"

sr = ser.dropna().astype('int64').apply(buy_bool , args = (ser.quantile(0.9) ,))
print(f'The Series is :-\n{ser}\nAnd the Filtered Series is :-\n{sr}\n')

jit = np.where(ser > ser.median() , 'Greater' , 'Lower')
print(f'The Work on Numpy where is done and it came out as :-\n{jit}')