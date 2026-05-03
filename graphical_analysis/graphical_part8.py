import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data_received.csv")

# Extract month
df["Month"] = df["Date"].apply(lambda x: x.split("-")[0])

# --- Split phases ---
before = df[df["Month"] == "Dec"]          # Home phase
after = df[df["Month"].isin(["Jan", "Feb", "Mar", "Apr"])]  # Retail phase

# --- Average monthly expense ---
before_total = before["Total"].sum()
after_total_avg = after.groupby("Month")["Total"].sum().mean()

# --- Plot ---
plt.figure(figsize=(8, 6))

labels = ["Before (Dec - Home)", "After (Jan–Apr Avg - Retail)"]
values = [before_total, after_total_avg]

bars = plt.bar(labels, values, color=['orange', 'green'], width=0.5)

# Value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height, f'{int(height)}',
             ha='center', va='bottom')

plt.title("Figure 9: Expense Comparison — Home vs Retail Phase")
plt.ylabel("Total Expense (₹)")

plt.tight_layout()
plt.show()

# =========================================================
# ----------- TERMINAL STATISTICS FUNCTION -----------------
# =========================================================

def compute_stats(series):
    mean_val = series.mean()
    median_val = series.median()
    
    mode_val = series.mode()
    mode_val = mode_val.iloc[0] if not mode_val.empty else "No unique mode"
    
    variance = series.var()
    std_dev = series.std()
    
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    
    avedev = np.mean(np.abs(series - mean_val))
    
    return {
        "Mean": mean_val,
        "Median": median_val,
        "Mode": mode_val,
        "Variance": variance,
        "Std Dev": std_dev,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "Avg Abs Dev": avedev
    }

# --- Profit / Loss (simple proxy) ---
# Assuming profit = Total - (Raw + Stationery + Misc + Rent + Utilities)
# → In your dataset, this is already balanced → so:
# We'll define "loss days" = high cost spikes

def profit_loss_info(df_phase):
    avg = df_phase["Total"].mean()
    loss_days = df_phase[df_phase["Total"] > avg * 1.5].shape[0]
    profit_days = df_phase.shape[0] - loss_days
    return profit_days, loss_days

# --- Compute stats ---
before_stats = compute_stats(before["Total"])
after_stats = compute_stats(after["Total"])

before_profit, before_loss = profit_loss_info(before)
after_profit, after_loss = profit_loss_info(after)

# --- Print ---
def print_stats(name, stats, profit, loss):
    print(f"\n===== {name} Phase =====")
    print(f"Profit Days : {profit}")
    print(f"Loss Days   : {loss}")
    print("-" * 40)
    
    for k, v in stats.items():
        if isinstance(v, (int, float)):
            print(f"{k:<15}: ₹{v:.2f}")
        else:
            print(f"{k:<15}: {v}")
    
    print("=" * 40)

print_stats("BEFORE (Home - Dec)", before_stats, before_profit, before_loss)
print_stats("AFTER (Retail - Jan–Apr)", after_stats, after_profit, after_loss)