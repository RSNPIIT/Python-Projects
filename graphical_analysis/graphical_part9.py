import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data_received.csv")

# --- Total cost ---
total_cost = df["Total"].sum()

# --- Consumables (Raw + Stationery) ---
consumables = df["Raw Materials"].sum() + df["Stationaries"].sum()

# --- Remaining (Non-consumables) ---
non_consumables = total_cost - consumables

# --- Percentage ---
consumable_pct = (consumables / total_cost) * 100
non_consumable_pct = 100 - consumable_pct

# --- Terminal Output (VERY IMPORTANT INTERPRETATION) ---
print("\n===== Consumable Expense Analysis =====")
print(f"Total Cost            : ₹{total_cost:.2f}")
print(f"Consumables Cost      : ₹{consumables:.2f}")
print(f"Non-Consumables Cost  : ₹{non_consumables:.2f}")
print(f"Consumables Share     : {consumable_pct:.2f}%")

if 70 <= consumable_pct <= 80:
    print("Insight: ~70–80% cost is consumables → high working capital lock")
elif consumable_pct > 80:
    print("Insight: >80% cost is consumables → very high working capital lock")
else:
    print("Insight: Consumables are significant but not dominant")

print("=======================================\n")

# --- Pie Chart ---
labels = ["Consumables (Raw + Stationery)", "Others"]
sizes = [consumables, non_consumables]

plt.figure(figsize=(7, 7))

plt.pie(
    sizes,
    labels=labels,
    autopct='%1.1f%%',
    startangle=140,
    explode=[0.05, 0],
    
    labeldistance=1.1,  
    pctdistance=0.7      
)

plt.title("Figure 8: Consumable Expense Share", pad=20)  

plt.axis('equal')
plt.tight_layout()

plt.show()