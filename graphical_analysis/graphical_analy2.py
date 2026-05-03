import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data_received.csv")

# Sum each expense category
categories = ["Raw Materials", "Stationaries", "Utilities", "Rent", "Misc."]
totals = df[categories].sum()

explode = [0.08, 0.08, 0, 0, 0]

plt.figure(figsize=(8, 8))
plt.pie(
    totals,
    labels=categories,
    autopct='%1.1f%%',
    startangle=140,
    explode=explode
)

plt.title("Figure 2: Share of Total Expenses by Category")
plt.axis('equal')

plt.show()