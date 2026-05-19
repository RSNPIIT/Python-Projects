import numpy as np
import pandas as pd

arr = np.random.rand(1000 , 5)
99
df = pd.DataFrame(
    data = arr,
    columns = [f'Col_{i + 1}' for i in range(5)],
    index = [f'Row_{i + 1}' for i in range(1000)]
)
print(f"The dataframe is :-\n\n {df.head(6)}")

# Using the Dot Notation we have that :-
print(f"We calculate the values for the 2nd Column as  :-> \n{df.Col_2}")

# Now we use the same to find that of two columns combined here
print(f"Now we calculate that of the 3rd and 4th Column as :-> \n{df[['Col_3' , 'Col_4']]}")