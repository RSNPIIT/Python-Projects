import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data_received.csv")

# Create a proper sequential index
df["Index"] = range(len(df))

# Identify spike days
spike_days = df[df["Total"] > 5000]

# --- Plot ---
plt.figure(figsize=(12, 6))

# Line plot
plt.plot(df["Index"], df["Total"], linewidth=1.5)

# Highlight spikes
plt.scatter(
    spike_days["Index"],
    spike_days["Total"],
    color='red',
    label="Spike Days"
)

# Annotate spikes using original Date labels
for _, row in spike_days.iterrows():
    plt.text(
        row["Index"],
        row["Total"] + 200,
        row["Date"],  # show actual label like "Jan-31"
        ha='center',
        fontsize=8
    )

# Labels & title
plt.title("Figure 10: High Expense Days (Spike Analysis)")
plt.xlabel("Timeline (Sequential Days)")
plt.ylabel("Total Expense (₹)")

plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()