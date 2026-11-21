"""Bubble Blast - Constants and Game Settings"""

# Screen Dimensions
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 860
FPS = 60

# Grid Dimensions
GRID_COLS = 6
GRID_ROWS = 8

# Cell Dimensions
CELL_SIZE = 72
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_OFFSET_Y = 160

# Bubble Stages
STAGE_EMPTY = 0
STAGE_BLUE = 1    # 3 hits to pop
STAGE_YELLOW = 2  # 2 hits to pop
STAGE_GREEN = 3   # 1 hit to pop
STAGE_RED = 4     # CRITICAL: 1 hit explodes into 4 projectiles!

# Visual Colors
COLOR_BG = (14, 17, 26)
COLOR_CARD_BG = (22, 27, 40)
COLOR_TEXT_WHITE = (245, 248, 255)
COLOR_TEXT_MUTED = (140, 155, 180)
COLOR_TEXT_GOLD = (255, 215, 60)

# Bubble Sphere Colors
BUBBLE_COLORS = {
    STAGE_RED: (255, 65, 85),       # Neon Crimson
    STAGE_GREEN: (50, 220, 125),     # Electric Green
    STAGE_YELLOW: (255, 205, 50),    # Sunny Amber
    STAGE_BLUE: (50, 165, 255),      # Azure Blue
}

# Projectile speed
PROJECTILE_SPEED = 720.0
