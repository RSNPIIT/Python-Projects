import matplotlib.pyplot as plt
import numpy as np

# November 2026 Commit Data (Total: 1,924 commits across 7 repositories)
repos = [
    "Strategies_for_Professional_Growth",
    "Python-Projects",
    "Rust-Projects",
    "Household_Electricity_Price_Prediction",
    "Tokens_to_Transformers_GAI_LLM",
    "sandbox-cli (Rust)",
    "LLM_Using_Python_project",
]
commits = [885, 507, 402, 43, 40, 31, 16]

# Reverse order so the highest bar appears at the top
repos_rev = repos[::-1]
commits_rev = commits[::-1]

# GitHub Dark Dimmed palette
bg_color = "#0d1117"
panel_color = "#161b22"
grid_color = "#30363d"
text_color = "#e6edf3"
bar_colors = ["#238636", "#2ea043", "#2ea043", "#3fb950", "#3fb950", "#56d364", "#56d364"]

plt.rcParams["font.sans-serif"] = "DejaVu Sans"
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), facecolor=bg_color)
fig.suptitle(
    "November 2026 GitHub Activity — 1,924 Commits Across 7 Repositories",
    fontsize=15,
    fontweight="bold",
    color=text_color,
    y=0.97,
)

# --- Panel 1: Linear Scale (GitHub's Exact View) ---
ax1.set_facecolor(panel_color)
bars1 = ax1.barh(repos_rev, commits_rev, color=bar_colors, edgecolor="#30363d", height=0.6)
ax1.set_title("Linear Scale (GitHub's 'Tiny Dot' Effect)", color=text_color, fontsize=12, pad=10)
ax1.set_xlabel("Commits", color=text_color)
ax1.set_xlim(0, 1020)
ax1.grid(axis="x", color=grid_color, linestyle="--", alpha=0.6)
ax1.tick_params(colors=text_color)
for spine in ax1.spines.values():
    spine.set_color(grid_color)

for bar, val in zip(bars1, commits_rev):
    pct = (val / sum(commits)) * 100
    ax1.text(
        val + 14,
        bar.get_y() + bar.get_height() / 2,
        f"{val} ({pct:.1f}%)",
        va="center",
        ha="left",
        color=text_color,
        fontsize=9.5,
        fontweight="bold",
    )

# --- Panel 2: Log Scale (Making Smaller Repos Visible) ---
ax2.set_facecolor(panel_color)
bars2 = ax2.barh(repos_rev, commits_rev, color=bar_colors, edgecolor="#30363d", height=0.6)
ax2.set_xscale("log")
ax2.set_title("Logarithmic Scale (Balanced Comparison)", color=text_color, fontsize=12, pad=10)
ax2.set_xlabel("Commits (Log Scale)", color=text_color)
ax2.set_xlim(10, 1800)
ax2.grid(axis="x", which="both", color=grid_color, linestyle="--", alpha=0.5)
ax2.tick_params(colors=text_color)
for spine in ax2.spines.values():
    spine.set_color(grid_color)

for bar, val in zip(bars2, commits_rev):
    ax2.text(
        val * 1.15,
        bar.get_y() + bar.get_height() / 2,
        f"{val}",
        va="center",
        ha="left",
        color=text_color,
        fontsize=9.5,
        fontweight="bold",
    )

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig("november_2026_commits.png", dpi=300, facecolor=bg_color)
plt.show()

