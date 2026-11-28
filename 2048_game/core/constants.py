"""2048 Game - Constants & Visual Design Specifications"""
import pygame

# Grid & Screen Geometry
GRID_SIZE = 4
TILE_SIZE = 106
GRID_GAP = 14
BOARD_PADDING = 14

BOARD_WIDTH = GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * GRID_GAP  # 494 px
BOARD_HEIGHT = BOARD_WIDTH                                        # 494 px

SCREEN_WIDTH = 550
SCREEN_HEIGHT = 730

BOARD_OFFSET_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2                # 28 px
BOARD_OFFSET_Y = 195

FPS = 60

# Directions
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

# Themes
THEME_LIGHT = "light"
THEME_DARK = "dark"

# Color Palettes (Light Classic Theme)
PALETTE_LIGHT = {
    "bg": (250, 248, 239),               # #FAF8EF
    "board_bg": (187, 173, 160),         # #BBADA0
    "cell_empty": (205, 193, 180),       # #CDC1B4
    "text_dark": (119, 110, 101),        # #776E65
    "text_light": (249, 246, 242),       # #F9F6F2
    "button_bg": (143, 122, 102),        # #8F7A66
    "button_hover": (159, 138, 118),
    "button_text": (255, 255, 255),
    "badge_bg": (187, 173, 160),
    "badge_title": (238, 228, 218),
    "badge_val": (255, 255, 255),
    "overlay_bg": (238, 228, 218, 190),
    "overlay_text": (119, 110, 101),
}

# Color Palettes (Dark Night Mode Theme)
PALETTE_DARK = {
    "bg": (26, 27, 38),                  # Deep Navy Charcoal
    "board_bg": (36, 40, 59),            # Slate container
    "cell_empty": (53, 59, 87),          # Dim cell
    "text_dark": (192, 202, 245),
    "text_light": (255, 255, 255),
    "button_bg": (122, 162, 247),        # Accent Blue
    "button_hover": (140, 176, 255),
    "button_text": (20, 24, 38),
    "badge_bg": (36, 40, 59),
    "badge_title": (122, 162, 247),
    "badge_val": (255, 255, 255),
    "overlay_bg": (26, 27, 38, 215),
    "overlay_text": (255, 255, 255),
}

# Tile Color Map (Standard 2048 values)
TILE_COLORS = {
    2: {"bg": (238, 228, 218), "text": (119, 110, 101)},          # #EEE4DA
    4: {"bg": (237, 224, 200), "text": (119, 110, 101)},          # #EDE0C8
    8: {"bg": (242, 177, 121), "text": (249, 246, 242)},          # #F2B179
    16: {"bg": (245, 149, 99), "text": (249, 246, 242)},          # #F59563
    32: {"bg": (246, 124, 95), "text": (249, 246, 242)},          # #F67C5F
    64: {"bg": (246, 94, 59), "text": (249, 246, 242)},           # #F65E3B
    128: {"bg": (237, 207, 114), "text": (249, 246, 242), "glow": True}, # #EDCF72
    256: {"bg": (237, 204, 97), "text": (249, 246, 242), "glow": True},  # #EDCC61
    512: {"bg": (237, 200, 80), "text": (249, 246, 242), "glow": True},  # #EDC850
    1024: {"bg": (237, 197, 63), "text": (249, 246, 242), "glow": True}, # #EDC53F
    2048: {"bg": (237, 194, 46), "text": (249, 246, 242), "glow": True, "pulse": True}, # #EDC22E
    4096: {"bg": (163, 103, 194), "text": (249, 246, 242), "glow": True}, # Amethyst
    8192: {"bg": (114, 88, 212), "text": (249, 246, 242), "glow": True},  # Royal Violet
    16384: {"bg": (60, 58, 50), "text": (249, 246, 242), "glow": True},   # Onyx
    32768: {"bg": (35, 34, 30), "text": (249, 246, 242), "glow": True},
    65536: {"bg": (20, 20, 18), "text": (249, 246, 242), "glow": True},
}

# Animation Timings (seconds)
ANIM_SLIDE_DURATION = 0.11   # 110ms slide
ANIM_SPAWN_DURATION = 0.14   # 140ms scale-up
ANIM_MERGE_DURATION = 0.16   # 160ms pop bounce

# UI Radii
TILE_BORDER_RADIUS = 8
BOARD_BORDER_RADIUS = 10
BUTTON_BORDER_RADIUS = 6
BADGE_BORDER_RADIUS = 6
