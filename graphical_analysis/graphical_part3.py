import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data_received.csv")

categories = ["Raw Materials", "Stationaries", "Utilities", "Rent", "Misc."]

# Average per category
avg_expense = df[categories].mean()

# Global mean
global_mean = avg_expense.mean()

# Plot
plt.figure(figsize=(10, 6))

bars = plt.bar(categories, avg_expense)

# --- Mean line (different color + legend) ---
plt.axhline(
    y=global_mean,
    color='red',                 # distinct color
    linestyle='--',
    linewidth=2,
    label=f"Mean = ₹{global_mean:.2f}"
)

# Annotate mean value on the line
plt.text(
    x=len(categories) - 0.5,     # position near right side
    y=global_mean + 5,
    s=f"₹{global_mean:.1f}",
    color='red',
    ha='right'
)

# Labels & title
plt.title("Figure 3: Average Daily Expense by Category")
plt.ylabel("Average Daily Expense (₹)")
plt.xlabel("Expense Category")

# Bar labels
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f'{height:.0f}',
        ha='center',
        va='bottom'
    )

# Legend for mean line
plt.legend()

plt.xticks(rotation=20)
plt.tight_layout()
plt.show()