import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data_received.csv")

# Extract month
df["Month"] = df["Date"].apply(lambda x: x.split("-")[0])

# Group by month and sum each category
monthly_category = df.groupby("Month")[
    ["Raw Materials", "Stationaries", "Utilities", "Rent", "Misc."]
].sum()

# Ensure correct order
month_order = ["Dec", "Jan", "Feb", "Mar", "Apr"]
monthly_category = monthly_category.reindex(month_order)

# --- Plot ---
plt.figure(figsize=(10, 6))

# Plot each category as a line
for col in monthly_category.columns:
    plt.plot(
        monthly_category.index,
        monthly_category[col],
        marker='o',
        linewidth=2,
        label=col
    )

# Labels & title
plt.title("Figure 6: Monthly Expense Trend by Category")
plt.xlabel("Month")
plt.ylabel("Total Expense (₹)")

# Legend
plt.legend()

plt.grid(alpha=0.3)  # subtle grid for readability

plt.tight_layout()
plt.show()