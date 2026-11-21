"""
config.py - Global Configuration and Styling Constants for Reimagined Tetris.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
HIGHSCORES_FILE = DATA_DIR / "highscores.json"

# Display & Window Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
TITLE = "REIMAGINED TETRIS // CYBER MATRIX"

# Board Settings
DEFAULT_COLS = 10
DEFAULT_ROWS = 20
BUFFER_ROWS = 4  # Hidden rows above the visible ceiling
WIDE_COLS = 16   # The user's original wide mode option

CELL_SIZE = 32   # Pixel dimensions per block cell in standard mode
CELL_SIZE_WIDE = 24  # For wide mode to comfortably fit screen

# Handling & Timing (Tetris Guideline / Competitive Feel)
DAS_DELAY = 10   # Delayed Auto Shift delay (frames before fast-repeat kicks in)
ARR_RATE = 2     # Auto Repeat Rate (frames between moves when held)
SOFT_DROP_FACTOR = 20  # Multiplier for soft drop speed
LOCK_DELAY = 30  # Frames of grace period on ground before locking (0.5s at 60fps)
MAX_LOCK_RESETS = 15  # Guideline extended placement resets allowed

# Color Palette (Futuristic Cyberpunk / Dark Glass Aesthetic)
COLOR_BG_DEEP = (10, 12, 18)
COLOR_PANEL_BG = (15, 20, 30, 200)
COLOR_PANEL_BORDER = (45, 65, 95)
COLOR_PANEL_BORDER_GLOW = (0, 220, 255)

# 7 Standard Tetromino Colors + Ghost
TETROMINO_COLORS = {
    'I': (0, 240, 255),    # Vibrant Cyan
    'O': (255, 225, 50),    # Vibrant Yellow
    'T': (180, 50, 255),    # Vibrant Purple
    'S': (80, 255, 80),     # Vibrant Green
    'Z': (255, 50, 75),     # Vibrant Red
    'J': (50, 100, 255),    # Vibrant Blue
    'L': (255, 140, 30),    # Vibrant Orange
}

# Block rendering styling
COLOR_GHOST = (180, 220, 255, 75)
COLOR_GRID_LINE = (30, 42, 60, 90)
COLOR_MATRIX_BG = (8, 12, 18, 230)
COLOR_MATRIX_BORDER = (0, 190, 255)

# Text & Accent Colors
COLOR_TEXT_TITLE = (255, 255, 255)
COLOR_TEXT_PRIMARY = (230, 240, 255)
COLOR_TEXT_MUTED = (130, 155, 180)
COLOR_ACCENT_CYAN = (0, 235, 255)
COLOR_ACCENT_GOLD = (255, 205, 50)
COLOR_ACCENT_MAGENTA = (255, 60, 180)

# Scoring Table (Official Tetris Guideline Multiplied by Level)
SCORE_TABLE = {
    'single': 100,
    'double': 300,
    'triple': 500,
    'tetris': 800,
    'b2b_tetris': 1200,
    'tspin_mini': 100,
    'tspin_single': 800,
    'tspin_double': 1200,
    'tspin_triple': 1600,
    'b2b_tspin_double': 1800,
    'b2b_tspin_triple': 2400,
    'soft_drop': 1,
    'hard_drop': 2,
    'all_clear_single': 800,
    'all_clear_double': 1200,
    'all_clear_triple': 1800,
    'all_clear_tetris': 2000,
    'b2b_all_clear_tetris': 3200,
}
