#!/usr/bin/env julia
# ==============================================================================
# Python-Projects Monorepo Manifest & Directory Architecture Guide
# Author: Ramrup Satpati (RSNPIIT) | IIT Madras
# Milestone: 1,000+ Commits | 100+ Projects & Modules
# License: GNU General Public License v3.0 (GPL-3.0)
# ==============================================================================

module PythonProjectsManifest

export ProjectEntry, MonorepoMeta, MONOREPO_CATEGORIES, display_monorepo_summary

"""
    ProjectEntry
Represents an individual project, module, or game engine inside the monorepo.
"""
struct ProjectEntry
    name::String
    path::String
    category::Symbol
    tech_stack::Vector{String}
    description::String
end

"""
    MonorepoMeta
Global metadata capturing the monorepo scale and git history.
"""
struct MonorepoMeta
    repository::String
    author::String
    institution::String
    total_commits::Int
    primary_language::String
    license::String
    status::String
end

const REPO_META = MonorepoMeta(
    "RSNPIIT/Python-Projects",
    "Ramrup Satpati",
    "Indian Institute of Technology Madras (IITM)",
    1016,
    "Python 3.10+ (with Julia, R, Shell polyglot benchmarks)",
    "GPL-3.0",
    "Active Production & Research Monorepo (1,000+ Commits Club)"
)

const MONOREPO_ENTRIES = [
    # --------------------------------------------------------------------------
    # 1. FLAGSHIP GAME ENGINES & GRAPHICS
    # --------------------------------------------------------------------------
    ProjectEntry(
        "Thornspire: Conquer the 10 Realms",
        "thornspire_game_latest/ & platformer_game/",
        :GameEngines,
        ["Python 3.14", "Pygame-CE", "ModernGL", "NumPy", "OpenGL Shaders"],
        "Commercial-grade 2D dark fantasy atmospheric platformer. Features 100 levels across 10 realms, endless loop & time trial modes, hardware-accelerated ModernGL shaders, dynamic lighting, and customization studio."
    ),
    ProjectEntry(
        "Nova Strike // Eclipse Protocol",
        "raylib_game/",
        :GameEngines,
        ["Python", "Raylib", "macOS .app Bundle"],
        "High-performance cyberpunk top-down action shooter set in Neon City. Features twin-stick mouse-aim combat, multi-sector mission progression, and native macOS desktop packaging."
    ),
    ProjectEntry(
        "Cyber Ops: Vanguard Response Unit",
        "panda_3D_shooting_game/",
        :GameEngines,
        ["Panda3D", "Procedural Mesh Engine", "Vector Math"],
        "Procedural 3D tactical FPS inspired by classic tactical shooters. Features custom procedural mesh builders, procedural texture synthesis, dynamic sound generation, enemy AI pathfinding, and real-time tactical radar."
    ),
    ProjectEntry(
        "Arcade Classics & Simulations",
        "pong_game_folder/, snake_game_withscore/, turtle_crossing_start/",
        :GameEngines,
        ["Pygame", "Python Turtle"],
        "Engine implementations of classic gaming systems including Pong with state tracking, Snake with persistent high scores, and Frogger-style traffic crossing."
    ),

    # --------------------------------------------------------------------------
    # 2. AI, MACHINE LEARNING & COMPUTER VISION
    # --------------------------------------------------------------------------
    ProjectEntry(
        "Computer Vision Studio",
        "computer_vision_project/",
        :AI_ML,
        ["OpenCV", "MediaPipe", "NumPy"],
        "Real-time visual tracking, gesture recognition, frame processing, and spatial computer vision pipelines."
    ),
    ProjectEntry(
        "AI Career Copilot",
        "ai_career_copilot/",
        :AI_ML,
        ["NLP", "Transformers", "Regex", "Scikit-Learn"],
        "Automated semantic resume parser, skills taxonomy matcher, and job profile alignment engine."
    ),
    ProjectEntry(
        "Monte Carlo Risk Simulator",
        "monte_carlo_sim/",
        :AI_ML,
        ["NumPy", "SciPy", "Matplotlib"],
        "Stochastic probability simulations, asset pricing simulations, and variance reduction techniques."
    ),
    ProjectEntry(
        "Quantitative Stock Analytics",
        "stock_market_project/",
        :AI_ML,
        ["Pandas", "yfinance", "Matplotlib"],
        "Time-series financial market analysis, moving average crossover signals, and portfolio volatility tracking."
    ),
    ProjectEntry(
        "Organizational Employee Analytics",
        "indian_employee_dataset/",
        :AI_ML,
        ["Pandas", "Seaborn"],
        "End-to-end data cleaning, demographic salary distribution analysis, and attrition predictive features."
    ),

    # --------------------------------------------------------------------------
    # 3. WEB SCRAPING, NETWORK APIS & AUTOMATION
    # --------------------------------------------------------------------------
    ProjectEntry(
        "E-Commerce Arbitrage & Price Tracker",
        "amazon_price_tracker/",
        :Automation,
        ["BeautifulSoup4", "Requests", "SMTP", "LXML"],
        "Headless web scraper monitoring live price movements on retail listings with automated email drop alerts."
    ),
    ProjectEntry(
        "Billboard Hot 100 Spotify Curating Engine",
        "billboard_project/",
        :Automation,
        ["Spotipy API", "BeautifulSoup4", "OAuth2"],
        "Time-travel playlist compiler fetching historical Billboard charts for any user-selected date and assembling matching Spotify playlists."
    ),
    ProjectEntry(
        "Real-time Weather & Satellite Systems",
        "open_weather_api.py, api_weather.py, iss_notifier/",
        :Automation,
        ["REST APIs", "JSON", "Geo-Coordinates"],
        "Geospatial telemetry scrapers calculating real-time International Space Station flyover proximity and local meteorological forecasting."
    ),
    ProjectEntry(
        "YouTube Stream Ingestion Pipeline",
        "yt_download_proj.py/",
        :Automation,
        ["pytube", "FFmpeg"],
        "Automated high-definition video and audio stream extractor with automated format muxing."
    ),

    # --------------------------------------------------------------------------
    # 4. MATHEMATICS, SCIENTIFIC COMPUTING & ALGORITHMS
    # --------------------------------------------------------------------------
    ProjectEntry(
        "Chudnovsky Arbitrary-Precision Pi Engine",
        "chudnovsky_math_calc/",
        :Mathematics,
        ["GMP / Decimal", "Ramanujan-like Series"],
        "Fast hypergeometric series summation calculating thousands of decimal places of Pi using the Chudnovsky algorithm."
    ),
    ProjectEntry(
        "Collatz Dynamical System Visualizer",
        "collatz_conj_math/",
        :Mathematics,
        ["Recursion", "Matplotlib", "Number Theory"],
        "Trajectory mapping and stopping time distribution analysis for the 3n + 1 dynamical system."
    ),
    ProjectEntry(
        "Numerical Methods & Differential Calculus",
        "numeric_integration.py, numeric_differetiation.py, apsum.py",
        :Mathematics,
        ["Newton-Cotes", "Finite Differences"],
        "First-principles implementations of Simpson's rules, trapezoidal integration, and numerical Taylor approximations."
    ),
    ProjectEntry(
        "Competitive Algorithms & Monorepo Sols",
        "leetcode_qn_sols/, binary_search.py",
        :Mathematics,
        ["Data Structures", "Dynamic Programming", "Graph Search"],
        "Optimized solutions for algorithmic problems spanning two-pointers, sliding window, and divide-and-conquer paradigms."
    ),

    # --------------------------------------------------------------------------
    # 5. DESKTOP GUIS, VISUALIZATIONS & SECURITY
    # --------------------------------------------------------------------------
    ProjectEntry(
        "Manim Mathematical Animation Suite",
        "manim_lib_animations/",
        :GUIs_and_Tools,
        ["Manim Community Engine", "LaTeX"],
        "Programmatic video generation illustrating linear algebra transformations, calculus proofs, and geometric figures."
    ),
    ProjectEntry(
        "Encrypted Credential Vault",
        "password_manager_start/, sample_encrypt_proj/",
        :GUIs_and_Tools,
        ["Tkinter", "PBKDF2", "AES/Ciphers"],
        "Zero-knowledge desktop password manager featuring dynamic password generation and encrypted local keyrings."
    ),
    ProjectEntry(
        "Spaced-Repetition Flashcard Engine",
        "flash_card_project_start/",
        :GUIs_and_Tools,
        ["Tkinter", "Pandas", "CSV State Storage"],
        "Language learning desktop interface utilizing Leitner-inspired spaced repetition cycles with persistent progress."
    ),
    ProjectEntry(
        "Productivity Pomodoro Suite",
        "pomodoro_start/, flowtime_prog/",
        :GUIs_and_Tools,
        ["Tkinter Canvas", "State Machines"],
        "Focus interval tracking utility with visual work/rest session transitions and auditory triggers."
    )
]

"""
    display_monorepo_summary()
Prints a high-impact ASCII overview of the monorepo architecture.
"""
function display_monorepo_summary()
    println("="^80)
    println("  🐍 PYTHON-PROJECTS MONOREPO MANIFEST (Julia Edition)")
    println("  Author: ", REPO_META.author, " | ", REPO_META.institution)
    println("  Milestone: ", REPO_META.total_commits, "+ Commits | Status: ", REPO_META.status)
    println("="^80)
    println()
    
    categories = Dict(
        :GameEngines   => "🎮 FLAGSHIP GAME ENGINES & GRAPHICS",
        :AI_ML         => "🤖 AI, MACHINE LEARNING & COMPUTER VISION",
        :Automation    => "🌐 WEB SCRAPING, APIS & AUTOMATION",
        :Mathematics   => "🧮 MATHEMATICS & NUMERICAL COMPUTING",
        :GUIs_and_Tools=> "🖥️ DESKTOP GUIS, TOOLS & SECURITY"
    )
    
    for (cat_key, cat_title) in categories
        println(cat_title)
        println("-"^80)
        matching = filter(e -> e.category == cat_key, MONOREPO_ENTRIES)
        for item in matching
            println(" • [", item.name, "] -> ", item.path)
            println("   Tech: ", join(item.tech_stack, ", "))
            println("   Desc: ", item.description)
            println()
        end
    end
    println("="^80)
    println("  Manifest generated successfully. Ready for Linux, Flathub, and Monorepo indexing!")
    println("="^80)
end

end # module

# Execute when run directly via julia about_this_dir.jl
if abspath(PROGRAM_FILE) == @__FILE__
    using .PythonProjectsManifest
    display_monorepo_summary()
end
