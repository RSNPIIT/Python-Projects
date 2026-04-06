import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

# Load data
df = pd.read_csv("data_received.csv")

# Convert Date column to datetime
# Extract month from Date (e.g., "Dec", "Jan")
df['Month'] = df['Date'].str[:3]

# Assign year: Dec → 2025, Jan–Apr → 2026
df['Year'] = df['Month'].apply(lambda x: 2025 if x == 'Dec' else 2026)

# Combine into full date string
df['Full_Date'] = df['Date'] + '-' + df['Year'].astype(str)

# Convert to proper datetime
df['Date'] = pd.to_datetime(df['Full_Date'], format='%b-%d-%Y')

# Drop helper columns (optional but clean)
df = df.drop(columns=['Month', 'Year', 'Full_Date'])

# Sort by date (important)
df = df.sort_values(by='Date')

# Create numeric index for regression (time axis)
df['Day_Index'] = np.arange(len(df))

# Independent (X) and dependent (y)
X = df[['Day_Index']]
y = df['Total']

# Fit Linear Regression model
model = LinearRegression()
model.fit(X, y)

# Predict values (trendline)
y_pred = model.predict(X)

# Compute R^2
r_squared = model.score(X, y)

# ---- Plot ----
plt.figure(figsize=(12,6))

# Actual data
plt.plot(df['Date'], y, label='Actual Total')

# Trendline
plt.plot(df['Date'], y_pred, linestyle='--', label='Trendline')

plt.xlabel("Date")
plt.ylabel("Total Expense")
plt.title("Expense Trend Analysis")

plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

# ---- Annotate Peak Values ----

# Option 1: Top N peaks (recommended)
N = 5  # number of peaks you want to label

top_peaks = df.nlargest(N, 'Total')

for i, row in top_peaks.iterrows():
    plt.annotate(
        f"{int(row['Total'])}",
        (row['Date'], row['Total']),
        textcoords="offset points",
        xytext=(0,10),
        ha='center',
        fontsize=9,
        arrowprops=dict(arrowstyle='->')
    )
    
plt.show()

# Print R^2
print(f"R-squared (R²): {r_squared:.4f}")