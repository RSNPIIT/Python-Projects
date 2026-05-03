import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Load dataset
df = pd.read_csv("data_received.csv")

# Independent (X) and Dependent (y)
X = df[["Raw Materials"]].values
y = df["Total"].values

# --- Model ---
model = LinearRegression()
model.fit(X, y)

# Predictions
y_pred = model.predict(X)

# R² score
r2 = r2_score(y, y_pred)

# --- Plot ---
plt.figure(figsize=(8, 6))

# Scatter plot
plt.scatter(df["Raw Materials"], y, label="Data Points")

# Regression line
plt.plot(df["Raw Materials"], y_pred, linewidth=2,
         label=f"Regression Line (R² = {r2:.3f})")

# Labels & title
plt.title("Figure 11: Raw Material vs Total Expense")
plt.xlabel("Raw Material Cost (₹)")
plt.ylabel("Total Expense (₹)")

plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()

# --- Terminal Output ---
print("\n===== Regression Analysis =====")
print(f"Slope (Coefficient) : {model.coef_[0]:.4f}")
print(f"Intercept           : {model.intercept_:.2f}")
print(f"R-squared (R²)      : {r2:.4f}")
print("===============================\n")