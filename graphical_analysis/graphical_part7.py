import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data_received.csv")

# Extract month
df["Month"] = df["Date"].apply(lambda x: x.split("-")[0])

# Define cost groups
df["Fixed"] = df["Rent"] + df["Utilities"]
df["Variable"] = df["Raw Materials"] + df["Stationaries"] + df["Misc."]

# Monthly totals
monthly_costs = df.groupby("Month")[["Fixed", "Variable"]].sum()

# Correct order
month_order = ["Dec", "Jan", "Feb", "Mar", "Apr"]
monthly_costs = monthly_costs.reindex(month_order)

# --- Plot ---
plt.figure(figsize=(10, 6))

plt.plot(
    monthly_costs.index,
    monthly_costs["Fixed"],
    marker='o',
    linewidth=2,
    label="Fixed Cost (Rent + Utilities)"
)

plt.plot(
    monthly_costs.index,
    monthly_costs["Variable"],
    marker='o',
    linewidth=2,
    label="Variable Cost (Raw + Stationery + Misc)"
)

# Labels & title
plt.title("Figure 7: Fixed vs Variable Cost Comparison")
plt.xlabel("Month")
plt.ylabel("Total Expense (₹)")

# Legend
plt.legend()

# Subtle grid
plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()