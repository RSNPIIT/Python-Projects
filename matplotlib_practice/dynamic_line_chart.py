import os
from datetime import datetime, timezone
import requests
import matplotlib.pyplot as plt

USERNAME = "RSNPIIT"
YEAR = 2026
MONTH = 11  # November

# Optional: Set GITHUB_TOKEN in your environment for GraphQL (exact monthly totals)
# export GITHUB_TOKEN="ghp_your_token_here"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def fetch_graphql_commits(username: str, year: int, month: int) -> dict[str, int]:
    """Fetches exact commit counts per repo for the given month via GitHub GraphQL API."""
    start_date = f"{year}-{month:02d}-01T00:00:00Z"
    end_day = 30 if month in (4, 6, 9, 11) else (28 if month == 2 else 31)
    end_date = f"{year}-{month:02d}-{end_day}T23:59:59Z"

    query = """
    query($user: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $user) {
        contributionsCollection(from: $from, to: $to) {
          commitContributionsByRepository(maxRepositories: 25) {
            repository {
              name
              primaryLanguage {
                name
              }
            }
            contributions {
              totalCount
            }
          }
        }
      }
    }
    """
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    resp = requests.post(
        "https://github.com",
        json={"query": query, "variables": {"user": username, "from": start_date, "to": end_date}},
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    payload = resp.json()

    if "errors" in payload:
        raise RuntimeError(f"GitHub GraphQL Error: {payload['errors']}")

    items = payload["data"]["user"]["contributionsCollection"]["commitContributionsByRepository"]
    results = {}
    for item in items:
        repo_name = item["repository"]["name"]
        lang = (item["repository"]["primaryLanguage"] or {}).get("name")
        label = f"{repo_name} ({lang})" if lang and lang != "Python" else repo_name
        results[label] = item["contributions"]["totalCount"]

    return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))


def fetch_rest_recent_commits(username: str, year: int, month: int) -> dict[str, int]:
    """Fallback using public REST API (no token needed, capped at most recent 300 events)."""
    counts: dict[str, int] = {}
    for page in range(1, 4):
        url = f"https://github.com{username}/events/public?per_page=100&page={page}"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        events = resp.json()
        if not events:
            break
        for ev in events:
            if ev.get("type") != "PushEvent":
                continue
            created = datetime.strptime(ev["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if created.year == year and created.month == month:
                repo_short = ev["repo"]["name"].split("/")[-1]
                commit_size = ev.get("payload", {}).get("size", 1)
                counts[repo_short] = counts.get(repo_short, 0) + commit_size

    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def plot_commits(data: dict[str, int], source_label: str) -> None:
    if not data:
        print("No commits found for the selected period.")
        return

    repos_rev = list(data.keys())[::-1]
    commits_rev = list(data.values())[::-1]
    total_commits = sum(commits_rev)
    repo_count = len(repos_rev)

    # GitHub Dark Dimmed palette
    bg_color = "#0d1117"
    panel_color = "#161b22"
    grid_color = "#30363d"
    text_color = "#e6edf3"
    muted_text = "#8b949e"
    palette = ["#238636", "#2ea043", "#3fb950", "#56d364", "#7ee787"]
    bar_colors = [palette[min(i * len(palette) // max(repo_count, 1), len(palette) - 1)] for i in range(repo_count)]

    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.8), sharey=True, facecolor=bg_color)

    month_name = datetime(YEAR, MONTH, 1).strftime("%B %Y")
    now_str = datetime.now().strftime("%b %d, %Y %I:%M %p")

    fig.suptitle(
        f"{month_name} GitHub Activity — {total_commits:,} Commits Across {repo_count} Repositories",
        fontsize=16,
        fontweight="bold",
        color=text_color,
        y=0.96,
    )
    fig.text(
        0.5,
        0.905,
        f"Author: {USERNAME}  •  Live Data ({source_label})  •  Generated {now_str}",
        ha="center",
        fontsize=10.5,
        color=muted_text,
    )

    max_val = max(commits_rev)

    # --- Panel 1: Linear Scale ---
    ax1.set_facecolor(panel_color)
    bars1 = ax1.barh(repos_rev, commits_rev, color=bar_colors, edgecolor="#30363d", height=0.58)
    ax1.set_title("Linear Scale (GitHub's 'Tiny Dot' Effect)", color=text_color, fontsize=12, fontweight="bold", pad=12)
    ax1.set_xlabel("Commits", color=text_color, fontsize=10.5, labelpad=8)
    ax1.set_xlim(0, max_val * 1.32)
    ax1.grid(axis="x", color=grid_color, linestyle="--", alpha=0.55)
    ax1.set_axisbelow(True)
    ax1.tick_params(axis="y", colors=text_color, labelsize=10.5)
    ax1.tick_params(axis="x", colors=muted_text, labelsize=9.5)
    for spine in ax1.spines.values():
        spine.set_color(grid_color)

    for bar, val in zip(bars1, commits_rev):
        pct = (val / total_commits) * 100
        ax1.text(
            val + max_val * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{val:,} ({pct:.1f}%)",
            va="center",
            ha="left",
            color=text_color,
            fontsize=9.5,
            fontweight="bold",
        )

    # --- Panel 2: Log Scale ---
    ax2.set_facecolor(panel_color)
    bars2 = ax2.barh(repos_rev, commits_rev, color=bar_colors, edgecolor="#30363d", height=0.58)
    ax2.set_xscale("log")
    ax2.set_title("Logarithmic Scale (Balanced Comparison)", color=text_color, fontsize=12, fontweight="bold", pad=12)
    ax2.set_xlabel("Commits (Log Scale)", color=text_color, fontsize=10.5, labelpad=8)
    ax2.set_xlim(max(1, min(commits_rev) * 0.6), max_val * 2.8)
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
            f"{val:,}",
            va="center",
            ha="left",
            color=text_color,
            fontsize=9.5,
            fontweight="bold",
        )

    fig.subplots_adjust(left=0.27, right=0.97, top=0.83, bottom=0.12, wspace=0.08)
    plt.savefig("november_2026_commits.png", dpi=300, facecolor=bg_color)
    plt.show()


if __name__ == "__main__":
    if GITHUB_TOKEN:
        print("Fetching exact monthly commit counts via GitHub GraphQL API...")
        commit_data = fetch_graphql_commits(USERNAME, YEAR, MONTH)
        source = "GitHub GraphQL API"
    else:
        print("No GITHUB_TOKEN found; falling back to public REST API (last 300 events)...")
        commit_data = fetch_rest_recent_commits(USERNAME, YEAR, MONTH)
        source = "GitHub Public REST API (Recent 300 Events)"

    plot_commits(commit_data, source)

