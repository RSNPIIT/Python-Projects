import matplotlib.pyplot as plt

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

# Reverse order so the top repo is at the top of the chart
repos_rev = repos[::-1]
commits_rev = commits[::-1]
total_commits = sum(commits)

# GitHub Dark Dimmed palette
bg_color = "#0d1117"
panel_color = "#161b22"
grid_color = "#30363d"
text_color = "#e6edf3"
muted_text = "#8b949e"
bar_colors = ["#238636", "#2ea043", "#2ea043", "#3fb950", "#3fb950", "#56d364", "#7ee787"]

plt.rcParams["font.sans-serif"] = "DejaVu Sans"
fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(16, 6.8), sharey=True, facecolor=bg_color
)

fig.suptitle(
    "November 2026 GitHub Activity — 1,924 Commits Across 7 Repositories",
    fontsize=16,
    fontweight="bold",
    color=text_color,
    y=0.96,
)
fig.text(
    0.5,
    0.905,
    "Author: RSNPIIT  •  Peak Month Surge (Nov 1 – Nov 22, 2026)",
    ha="center",
    fontsize=10.5,
    color=muted_text,
)

# --- Panel 1: Linear Scale (GitHub's Exact View) ---
ax1.set_facecolor(panel_color)
bars1 = ax1.barh(repos_rev, commits_rev, color=bar_colors, edgecolor="#30363d", height=0.58)
ax1.set_title("Linear Scale (GitHub's 'Tiny Dot' Effect)", color=text_color, fontsize=12, fontweight="bold", pad=12)
ax1.set_xlabel("Commits", color=text_color, fontsize=10.5, labelpad=8)
ax1.set_xlim(0, 1180)
ax1.grid(axis="x", color=grid_color, linestyle="--", alpha=0.55)
ax1.set_axisbelow(True)
ax1.tick_params(axis="y", colors=text_color, labelsize=10.5)
ax1.tick_params(axis="x", colors=muted_text, labelsize=9.5)
for spine in ax1.spines.values():
    spine.set_color(grid_color)

for bar, val in zip(bars1, commits_rev):
    pct = (val / total_commits) * 100
    ax1.text(
        val + 18,
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
bars2 = ax2.barh(repos_rev, commits_rev, color=bar_colors, edgecolor="#30363d", height=0.58)
ax2.set_xscale("log")
ax2.set_title("Logarithmic Scale (Balanced Comparison)", color=text_color, fontsize=12, fontweight="bold", pad=12)
ax2.set_xlabel("Commits (Log Scale)", color=text_color, fontsize=10.5, labelpad=8)
ax2.set_xlim(10, 2600)
ax2.grid(axis="x", which="major", color=grid_color, linestyle="--", alpha=0.55)
ax2.grid(axis="x", which="minor", color=grid_color, linestyle=":", alpha=0.25)
ax2.set_axisbelow(True)
ax2.tick_params(axis="y", left=False)
ax2.tick_params(axis="x", colors=muted_text, labelsize=9.5)
for spine in ax2.spines.values():
    spine.set_color(grid_color)

for bar, val in zip(bars2, commits_rev):
    ax2.text(
        val * 1.16,
        bar.get_y() + bar.get_height() / 2,
        f"{val}",
        va="center",
        ha="left",
        color=text_color,
        fontsize=9.5,
        fontweight="bold",
    )

# Clean spacing with generous left margin so repo names never clip
fig.subplots_adjust(left=0.27, right=0.97, top=0.83, bottom=0.12, wspace=0.08)
plt.savefig("november_2026_commits.png", dpi=300, facecolor=bg_color)
plt.show()

