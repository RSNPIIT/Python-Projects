"""Block Blast - Constants and Game Settings"""
import pygame

# Window & Board Dimensions (Modern Mobile-Arcade Portrait)
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 860
FPS = 60

# Grid Settings
GRID_COLS = 6
GRID_ROWS_MAX = 10
BLOCK_PADDING = 8
BOARD_TOP_MARGIN = 90
BOARD_BOTTOM_MARGIN = 140
DEADLINE_Y = SCREEN_HEIGHT - BOARD_BOTTOM_MARGIN  # 720 px: Game over if blocks reach here!

BLOCK_WIDTH = (SCREEN_WIDTH - (GRID_COLS + 1) * BLOCK_PADDING) / GRID_COLS
BLOCK_HEIGHT = 50

# Modern Neon Color Palette
COLOR_BG = (15, 17, 26)
COLOR_GRID_BG = (22, 25, 38)
COLOR_DEADLINE = (255, 60, 90)
COLOR_TEXT_WHITE = (245, 245, 250)
COLOR_TEXT_MUTED = (130, 140, 165)
COLOR_TEXT_GOLD = (255, 205, 60)

# Block Colors based on HP Tiers
BLOCK_COLORS = [
    (50, 205, 140),   # Tier 1: Neon Mint
    (56, 180, 245),   # Tier 2: Sky Cyan
    (140, 100, 250),  # Tier 3: Electric Purple
    (250, 150, 50),   # Tier 4: Sunset Orange
    (255, 75, 110),   # Tier 5: Neon Crimson
    (255, 215, 0),    # Tier 6: Radiant Gold (Boss)
]

# Powerup Types
class PowerUpType:
    SPREAD_SHOT = "spread"      # 3-way rocket split
    PIERCE = "pierce"           # Laser-piercing rocket
    RAPID_FIRE = "rapid"        # 2x firing rate
    BOMB = "bomb"               # 3x3 explosion
    FREEZE = "freeze"           # Pushes blocks back up
