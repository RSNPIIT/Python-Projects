"""
themes.py - Visual Styles and Palettes for Minesweeper.
Includes Modern Cyber Dark, Retro Win95 Classic, Nordic Frost, and Emerald Matrix.
"""

from typing import Dict, Any


THEMES: Dict[str, Dict[str, Any]] = {
    "Cyber Dark": {
        "name": "Cyber Dark",
        "bg_main": "#0f172a",          # Deep slate 900
        "bg_panel": "#1e293b",         # Slate 800
        "bg_board": "#090d16",         # Darkest abyss
        "tile_hidden": "#334155",      # Slate 700
        "tile_hidden_hover": "#475569",# Slate 600
        "tile_pressed": "#1e293b",     # Darker
        "tile_revealed": "#1e293b",    # Slate 800
        "tile_border": "#475569",
        "grid_line": "#0f172a",
        "lcd_bg": "#020617",           # Ultra-dark LCD
        "lcd_fg": "#38bdf8",           # Cyan glow LED
        "lcd_off": "#0c4a6e",          # Dim segment background
        "mine_body": "#f43f5e",        # Rose/Red neon
        "mine_spike": "#fb7185",
        "flag_fabric": "#f43f5e",      # Neon Red
        "flag_pole": "#cbd5e1",
        "flag_base": "#94a3b8",
        "question_mark": "#facc15",    # Neon Amber
        "hint_highlight": "#a855f7",   # Glowing Purple
        "numbers": {
            1: "#38bdf8",              # Neon Sky Blue
            2: "#4ade80",              # Neon Emerald
            3: "#f87171",              # Neon Coral
            4: "#c084fc",              # Neon Purple
            5: "#fb923c",              # Neon Amber Orange
            6: "#2dd4bf",              # Neon Teal
            7: "#e2e8f0",              # Crisp Pearl
            8: "#94a3b8",              # Muted Slate
        }
    },
    "Classic Retro": {
        "name": "Classic Retro",
        "bg_main": "#c0c0c0",          # Traditional Win95 beveled gray
        "bg_panel": "#c0c0c0",
        "bg_board": "#c0c0c0",
        "tile_hidden": "#c0c0c0",
        "tile_hidden_hover": "#d4d4d4",
        "tile_pressed": "#a0a0a0",
        "tile_revealed": "#c0c0c0",
        "tile_border": "#808080",
        "grid_line": "#808080",
        "lcd_bg": "#000000",
        "lcd_fg": "#ff0000",           # Pure 7-segment Red LED
        "lcd_off": "#330000",
        "mine_body": "#000000",
        "mine_spike": "#000000",
        "flag_fabric": "#ff0000",
        "flag_pole": "#000000",
        "flag_base": "#000000",
        "question_mark": "#000080",
        "hint_highlight": "#ffff00",
        "numbers": {
            1: "#0000ff",              # Classic Blue
            2: "#008000",              # Classic Green
            3: "#ff0000",              # Classic Red
            4: "#000080",              # Navy
            5: "#800000",              # Maroon
            6: "#008080",              # Teal
            7: "#000000",              # Black
            8: "#808080",              # Gray
        }
    },
    "Nordic Frost": {
        "name": "Nordic Frost",
        "bg_main": "#1e222d",
        "bg_panel": "#282c37",
        "bg_board": "#181a20",
        "tile_hidden": "#3b4252",
        "tile_hidden_hover": "#4c566a",
        "tile_pressed": "#2e3440",
        "tile_revealed": "#2e3440",
        "tile_border": "#434c5e",
        "grid_line": "#1e222d",
        "lcd_bg": "#12141a",
        "lcd_fg": "#88c0d0",           # Polar ice cyan
        "lcd_off": "#22313a",
        "mine_body": "#bf616a",
        "mine_spike": "#d08770",
        "flag_fabric": "#ebcb8b",      # Warm golden flag
        "flag_pole": "#e5e9f0",
        "flag_base": "#d8dee9",
        "question_mark": "#81a1c1",
        "hint_highlight": "#b48ead",
        "numbers": {
            1: "#88c0d0",
            2: "#a3be8c",
            3: "#bf616a",
            4: "#b48ead",
            5: "#d08770",
            6: "#8fbcbb",
            7: "#eceff4",
            8: "#4c566a",
        }
    },
    "Emerald Matrix": {
        "name": "Emerald Matrix",
        "bg_main": "#05160e",
        "bg_panel": "#0c281a",
        "bg_board": "#020b06",
        "tile_hidden": "#123b26",
        "tile_hidden_hover": "#1a5336",
        "tile_pressed": "#0c281a",
        "tile_revealed": "#071c12",
        "tile_border": "#1b4d32",
        "grid_line": "#04140b",
        "lcd_bg": "#020c07",
        "lcd_fg": "#00ff66",           # Matrix terminal green
        "lcd_off": "#003314",
        "mine_body": "#ff3366",
        "mine_spike": "#ff6688",
        "flag_fabric": "#ffcc00",
        "flag_pole": "#88ffaa",
        "flag_base": "#44aa66",
        "question_mark": "#00ffff",
        "hint_highlight": "#ffff33",
        "numbers": {
            1: "#00ff88",
            2: "#33ffbb",
            3: "#ffaa00",
            4: "#ff5577",
            5: "#ff77ff",
            6: "#00eeff",
            7: "#aaffcc",
            8: "#558866",
        }
    }
}
