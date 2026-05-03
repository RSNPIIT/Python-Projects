import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load dataset
df = pd.read_csv("data_received.csv")

# Extract month
df["Month"] = df["Date"].apply(lambda x: x.split("-")[0])

# Monthly averages
monthly_avg = df.groupby("Month")["Total"].mean()

# Correct order
month_order = ["Dec", "Jan", "Feb", "Mar", "Apr"]
monthly_avg = monthly_avg.reindex(month_order)

values = monthly_avg.values

# --- Statistics ---
mean_val = np.mean(values)
median_val = np.median(values)
variance = np.var(values)
std_dev = np.sqrt(variance)
q1 = np.percentile(values, 25)
q3 = np.percentile(values, 75)

# --- PRINT stats to terminal ---
print("\n===== Monthly Expense Statistics =====")
print(f"Mean      : ₹{mean_val:.2f}")
print(f"Median    : ₹{median_val:.2f}")
print(f"Variance  : {variance:.2f}")
print(f"Std Dev   : ₹{std_dev:.2f}")
print(f"Q1 (25%)  : ₹{q1:.2f}")
print(f"Q3 (75%)  : ₹{q3:.2f}")
print("======================================\n")

# --- Plot ONLY bars ---
plt.figure(figsize=(10, 6))

bars = plt.bar(
    monthly_avg.index,
    values,
    width=0.5,
    color='steelblue'
)

# Value labels
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2,
        height,
        f'{height:.0f}',
        ha='center',
        va='bottom'
    )

# Labels & title
plt.title("Figure 5: Average Daily Expense per Month (₹)")
plt.xlabel("Month")
plt.ylabel("Average Daily Expense (₹)")

plt.tight_layout()
plt.show()