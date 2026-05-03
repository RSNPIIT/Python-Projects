import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data_received.csv")

# Extract month
df["Month"] = df["Date"].apply(lambda x: x.split("-")[0])

# Monthly total expense
monthly_total = df.groupby("Month")["Total"].sum()

# Correct order
month_order = ["Dec", "Jan", "Feb", "Mar", "Apr"]
monthly_total = monthly_total.reindex(month_order)

# --- Plot ---
plt.figure(figsize=(10, 6))

bars = plt.bar(
    monthly_total.index,
    monthly_total.values,
    color='teal',
    width=0.6
)

# Value labels
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2,
        height,
        f'{int(height)}',
        ha='center',
        va='bottom'
    )

# Labels & title
plt.title("Figure 4: Total Monthly Expenditure (₹)")
plt.xlabel("Month")
plt.ylabel("Total Expense (₹)")

plt.tight_layout()
plt.show()