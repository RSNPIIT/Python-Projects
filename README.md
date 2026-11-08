# 🐍 Python-Projects Monorepo

<div align="center">

[![Commits](https://img.shields.io/badge/Commits-1%2C016%2B%20Milestone-8A2BE2?style=for-the-badge&logo=git&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Game Engines](https://img.shields.io/badge/Engines-ModernGL%20%7C%20Raylib%20%7C%20Panda3D-E65100?style=for-the-badge&logo=opengl&logoColor=white)](#-flagship-game-engines)
[![Deployments](https://img.shields.io/badge/Deployments-112%20Active-00C853?style=for-the-badge&logo=githubpages&logoColor=white)](#)
[![Polyglot](https://img.shields.io/badge/Polyglot-Julia%20%7C%20R%20%7C%20Shell-00599C?style=for-the-badge)](about_this_dir.jl)
[![License](https://img.shields.io/badge/License-GPL--3.0-4CAF50?style=for-the-badge)](LICENSE)

**An expansive, production-grade monorepo containing 100+ computational projects, custom graphics & shader engines, AI/ML pipelines, automated scrapers, and mathematical simulations.**

[🎮 Flagship Games](#-flagship-game-engines) • [🗂 Project Index](#-monorepo-directory-index) • [⚡ Quickstart](#-quickstart--execution) • [📜 Julia Manifest](about_this_dir.jl) • [⚖️ License](#-license)

</div>

---

## 📌 Monorepo Overview

Welcome to the **Python-Projects Monorepo** maintained by **Ramrup Satpati**. What began as exploratory scripts has evolved into a full-scale codebase with **over 1,000 commits**, hosting everything from commercial-grade hardware-accelerated indie games to mathematical modeling suites and data engineering tools.

### 🌟 Key Highlights
- **1,016+ Commits:** A continuous, battle-tested Git history spanning years of iterative development, refactoring, and atomic deployments.
- **Three Custom Game Engines:** Native 2D OpenGL shader pipelines (`ModernGL`), high-speed arcade action (`Raylib`), and procedural 3D first-person shooters (`Panda3D`).
- **Applied AI & Data Science:** Computer vision pipelines, Monte Carlo risk engines, quantitative stock predictors, and natural language career copilots.
- **Polyglot Benchmarking:** Incorporates **Julia** (see [`about_this_dir.jl`](about_this_dir.jl)), **R**, and **Zsh/Bash** automation utilities.

---

## 🎮 Flagship Game Engines

This repository houses three distinct game engines built from first principles in Python:

| Game | Engine & Stack | Genre / Architecture | Key Features |
| :--- | :--- | :--- | :--- |
| **THORNSPIRE** | `pygame-ce`<br/>`moderngl`<br/>`numpy` | **2D Dark-Fantasy Atmospheric Platformer** | • 100 hand-crafted & procedural levels across 10 Realms<br/>• Hardware-accelerated OpenGL lighting, bloom & particle shaders<br/>• Fluid air-dashing, wall-jumping, and vine climbing physics<br/>• Character customization studio (*Arctic Frost, Classic Hood*) |
| **NOVA STRIKE** | `raylib`<br/>`Python C-FFI` | **Cyberpunk Sci-Fi Top-Down Shooter** | • Twin-stick / mouse-aim tactical combat in Neon City<br/>• 4 multi-sector campaign progression with persistent save states<br/>• Packaged as a standalone native macOS `.app` bundle |
| **CYBER OPS** | `Panda3D`<br/>`Procedural Math` | **3D Tactical First-Person Shooter** | • Procedural 3D mesh building (`mesh_builder.py`) without heavy external models<br/>• Procedural texture synthesis and real-time audio sound generation<br/>• 3D AI enemy pathfinding, dynamic minimap radar & multi-weapon loadouts |

### 🚀 Running the Games Locally

```bash
# 1. Launch Thornspire (Platformer with ModernGL Shaders)
cd thornspire_game_latest/
./run.sh

# 2. Launch Nova Strike (Raylib Cyberpunk Action)
cd ../raylib_game/
./run.sh

# 3. Launch Cyber Ops (Panda3D Tactical FPS)
cd ../panda_3D_shooting_game/
./run.sh
```

---

## 🗂 Monorepo Directory Index

<details open>
<summary><b>🕹️ 1. Game Engines & Interactive Graphics</b></summary>

- [`thornspire_game_latest/`](thornspire_game_latest/) & [`platformer_game/`](platformer_game/) – Flagship 2D platformer with ModernGL shaders, 100 levels & custom skins.
- [`raylib_game/`](raylib_game/) – *Nova Strike // Eclipse Protocol* top-down shooter built on Raylib.
- [`panda_3D_shooting_game/`](panda_3D_shooting_game/) – *Cyber Ops* 3D procedural first-person shooter.
- [`pong_game_folder/`](pong_game_folder/) & `pong_game.py` – Dual-paddle physics simulation.
- [`snake_game_withscore/`](snake_game_withscore/) & `snake_game/` – Classic grid game with local high-score persistence.
- [`turtle_crossing_start/`](turtle_crossing_start/) – Arcade road-crossing timing game.
- `blackjack.py` & `slot_machinegame.py` – Probability-based casino simulations.
</details>

<details>
<summary><b>🤖 2. Artificial Intelligence, Data Science & Computer Vision</b></summary>

- [`computer_vision_project/`](computer_vision_project/) – Real-time computer vision tracking and frame analysis pipelines.
- [`ai_career_copilot/`](ai_career_copilot/) – AI-assisted resume keyword parser and career alignment copilot.
- [`monte_carlo_sim/`](monte_carlo_sim/) – Stochastic probability simulations and distribution modeling.
- [`stock_market_project/`](stock_market_project/) – Financial market telemetry, moving average indicators & volatility analysis.
- [`indian_employee_dataset/`](indian_employee_dataset/) – Demographic salary distribution and predictive workforce attrition modeling.
- [`pandas_dataframes/`](pandas_dataframes/) & [`numpy_refresher/`](numpy_refresher/) – Vectorized computation benchmarks.
- [`matplotlib_practice/`](matplotlib_practice/) & [`graphical_analysis/`](graphical_analysis/) – Advanced statistical visualization templates.
</details>

<details>
<summary><b>🌐 3. Web Scraping, APIs & Automation Systems</b></summary>

- [`amazon_price_tracker/`](amazon_price_tracker/) – Automated retail scraper with price-drop email dispatch.
- [`billboard_project/`](billboard_project/) – Historical Billboard Hot 100 scraper integrated with Spotify playlist generation.
- [`news_scraper_bs4/`](news_scraper_bs4/) & `randomnews.py` – Web-content parsers for dynamic news aggregation.
- `open_weather_api.py` & `api_weather.py` – Live weather telemetry using OpenWeatherMap endpoints.
- [`iss_notifier/`](iss_notifier/) – Real-time International Space Station orbital tracker and flyover alert.
- `yt_download_proj.py` – YouTube video and audio stream extractor with format muxing.
- [`flask_apps/`](flask_apps/) – Modular full-stack web application prototypes.
</details>

<details>
<summary><b>🧮 4. Mathematics, Scientific Computing & Algorithms</b></summary>

- [`chudnovsky_math_calc/`](chudnovsky_math_calc/) – Arbitrary-precision $\pi$ calculation using hypergeometric Chudnovsky series.
- [`collatz_conj_math/`](collatz_conj_math/) – Trajectory exploration and stopping times for the $3n + 1$ Collatz dynamical system.
- `numeric_integration.py` & `numeric_differetiation.py` – Numerical calculus implementations (Simpson's, Trapezoidal, Finite Differences).
- [`leetcode_qn_sols/`](leetcode_qn_sols/) – Algorithmic implementations of competitive programming challenges.
- `binary_search.py` & `sum_gp.py` – Classical divide-and-conquer algorithms and series summation.
</details>

<details>
<summary><b>🖥️ 5. Desktop GUIs, Security & Productivity Tools</b></summary>

- [`manim_lib_animations/`](manim_lib_animations/) – Programmatic mathematical motion graphics generated via the Manim Community Engine.
- [`password_manager_start/`](password_manager_start/) & [`sample_encrypt_proj/`](sample_encrypt_proj/) – Encrypted password storage using cryptographic hashing.
- [`flash_card_project_start/`](flash_card_project_start/) – Spaced-repetition language flashcard GUI.
- [`pomodoro_start/`](pomodoro_start/) & [`flowtime_prog/`](flowtime_prog/) – Interval-based focus timers built with Tkinter.
- `auditor_system.py` & `log_process.py` – Automated log parsing and integrity validation tools.
- [`color_proj_webapp_flsk/`](color_proj_webapp_flsk/) & [`colorgram_proj_dir/`](colorgram_proj_dir/) – Color palette extraction from imagery.
</details>

---

## ⚡ Quickstart & Execution

### 1. Clone the Monorepo
```bash
git clone git@github.com:RSNPIIT/Python-Projects.git
cd Python-Projects
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Explore with Julia Manifest
This repository features an executable Julia manifest detailing the directory structure:
```bash
julia about_this_dir.jl
```

---

## 🛠 Tech Stack & Dependencies

```
Languages     : Python 3.10 / 3.14, Julia, R, Bash / Zsh
Graphics & 3D : ModernGL, Pygame-CE, Raylib, Panda3D, OpenGL, PIL/Pillow
Data & ML     : NumPy, Pandas, Matplotlib, Seaborn, OpenCV, SciPy
Web & Scraping: Flask, BeautifulSoup4, Requests, Spotipy, LXML
Animations    : Manim Community Engine
```

---

## 📜 License

Distributed under the **GNU General Public License v3.0 (GPLv3)**. See [`LICENSE`](LICENSE) for full details.

---

<div align="center">

**Built with relentless consistency by [Ramrup Satpati](https://github.com/RSNPIIT)**  
*Indian Institute of Technology Madras &bull; Systems, Robotics & AI*  
[Portfolio](https://app-portfolio-dczpzvutdgvevdv8sedtls.streamlit.app) &bull; [LinkedIn](https://www.linkedin.com/in/ramrup-satpati-683970341)

</div>
