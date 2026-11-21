"""Bubble Blast - Handcrafted Puzzle Levels & Endless Level Generator"""
import random
from core.constants import (
    GRID_ROWS, GRID_COLS,
    STAGE_EMPTY, STAGE_BLUE, STAGE_YELLOW, STAGE_GREEN, STAGE_RED
)

LEVELS = [
    # Level 1: Intro to Chain Reactions (1 Touch)
    {
        "name": "First Pop",
        "touches": 1,
        "layout": [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 4, 0, 0, 0],
            [0, 4, 4, 4, 0, 0],
            [0, 0, 4, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    },
    # Level 2: Crossfire Domino (1 Touch)
    {
        "name": "Crossfire",
        "touches": 1,
        "layout": [
            [0, 0, 0, 0, 0, 0],
            [0, 4, 0, 0, 4, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 4, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 4, 0, 0, 4, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    },
    # Level 3: Green Bubble Absorption (1 Touch)
    {
        "name": "Green Evolution",
        "touches": 1,
        "layout": [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 4, 0, 0, 0],
            [0, 0, 3, 0, 0, 0],
            [0, 4, 3, 4, 0, 0],
            [0, 0, 4, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    },
    # Level 4: Dual Trigger (2 Touches)
    {
        "name": "Dual Spark",
        "touches": 2,
        "layout": [
            [0, 0, 0, 0, 0, 0],
            [4, 0, 0, 0, 0, 4],
            [3, 0, 0, 0, 0, 3],
            [0, 0, 4, 4, 0, 0],
            [0, 0, 3, 3, 0, 0],
            [4, 0, 0, 0, 0, 4],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    },
    # Level 5: Yellow Cascade (2 Touches)
    {
        "name": "Amber Sun",
        "touches": 2,
        "layout": [
            [0, 0, 0, 0, 0, 0],
            [0, 4, 2, 4, 0, 0],
            [0, 2, 4, 2, 0, 0],
            [0, 4, 2, 4, 0, 0],
            [0, 0, 4, 0, 0, 0],
            [0, 0, 3, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    },
    # Level 6: The Perimeter Ring (1 Touch)
    {
        "name": "Outer Ring",
        "touches": 1,
        "layout": [
            [0, 0, 0, 0, 0, 0],
            [4, 3, 3, 3, 3, 4],
            [3, 0, 0, 0, 0, 3],
            [3, 0, 4, 0, 0, 3],
            [3, 0, 0, 0, 0, 3],
            [4, 3, 3, 3, 3, 4],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    },
    # Level 7: Blue Diamond (2 Touches)
    {
        "name": "Azure Core",
        "touches": 2,
        "layout": [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 4, 4, 0, 0],
            [0, 4, 1, 1, 4, 0],
            [0, 4, 1, 1, 4, 0],
            [0, 0, 4, 4, 0, 0],
            [0, 0, 3, 3, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    },
    # Level 8: Precision Cascade (2 Touches)
    {
        "name": "Domino Alley",
        "touches": 2,
        "layout": [
            [0, 4, 0, 0, 4, 0],
            [0, 3, 0, 0, 3, 0],
            [0, 2, 0, 0, 2, 0],
            [4, 1, 4, 4, 1, 4],
            [0, 2, 0, 0, 2, 0],
            [0, 3, 0, 0, 3, 0],
            [0, 4, 0, 0, 4, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    },
    # Level 9: Matrix Overload (3 Touches)
    {
        "name": "Matrix Core",
        "touches": 3,
        "layout": [
            [0, 0, 0, 0, 0, 0],
            [4, 2, 4, 2, 4, 0],
            [2, 3, 1, 3, 2, 0],
            [4, 1, 4, 1, 4, 0],
            [2, 3, 1, 3, 2, 0],
            [4, 2, 4, 2, 4, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    },
    # Level 10: Grand Cascade (2 Touches)
    {
        "name": "Grand Finale",
        "touches": 2,
        "layout": [
            [4, 3, 2, 2, 3, 4],
            [3, 4, 3, 3, 4, 3],
            [2, 3, 4, 4, 3, 2],
            [2, 3, 4, 4, 3, 2],
            [3, 4, 3, 3, 4, 3],
            [4, 3, 2, 2, 3, 4],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    }
]

def generate_arcade_wave(wave_num: int) -> tuple[list[list[int]], int]:
    """Generate a random board layout for Arcade / Endless mode."""
    layout = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    
    # Fill 15 to 25 random slots
    num_bubbles = min(32, 14 + wave_num * 2)
    coords = [(r, c) for r in range(1, 7) for c in range(GRID_COLS)]
    random.shuffle(coords)

    for r, c in coords[:num_bubbles]:
        # Proportion of stages depends on wave
        roll = random.random()
        if roll < 0.45:
            stage = STAGE_RED
        elif roll < 0.75:
            stage = STAGE_GREEN
        elif roll < 0.92:
            stage = STAGE_YELLOW
        else:
            stage = STAGE_BLUE
        layout[r][c] = stage

    # Provide 2 to 4 touches depending on difficulty
    touches = max(2, min(5, 3 + wave_num // 4))
    return layout, touches
