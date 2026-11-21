"""Bubble Trouble / Archer Bubble Blast - Constants and Arena Config"""

# Screen Dimensions (Spacious Landscape Arcade Arena)
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

# Arena Physical Boundaries
ARENA_LEFT = 36
ARENA_RIGHT = SCREEN_WIDTH - 36
ARENA_TOP = 65
ARENA_FLOOR = SCREEN_HEIGHT - 60

# Physics
GRAVITY = 720.0
PLAYER_SPEED = 420.0
ARROW_SPEED = 900.0

# Bubble Sizes
SIZE_HUGE = 4     # Radius 48px, floor bounce -620
SIZE_LARGE = 3    # Radius 36px, floor bounce -540
SIZE_MEDIUM = 2   # Radius 24px, floor bounce -460
SIZE_SMALL = 1    # Radius 14px, floor bounce -380

BUBBLE_PROPERTIES = {
    SIZE_HUGE: {
        "radius": 46.0,
        "bounce_vy": -610.0,
        "vx": 150.0,
        "color": (255, 60, 85),     # Neon Crimson
        "points": 50
    },
    SIZE_LARGE: {
        "radius": 34.0,
        "bounce_vy": -530.0,
        "vx": 170.0,
        "color": (255, 145, 40),    # Sunset Orange
        "points": 100
    },
    SIZE_MEDIUM: {
        "radius": 23.0,
        "bounce_vy": -460.0,
        "vx": 195.0,
        "color": (50, 225, 120),    # Electric Emerald
        "points": 150
    },
    SIZE_SMALL: {
        "radius": 13.0,
        "bounce_vy": -380.0,
        "vx": 220.0,
        "color": (50, 185, 255),    # Azure Cyan
        "points": 200
    }
}

# Theme Colors
COLOR_BG = (15, 18, 28)
COLOR_ARENA_WALL = (32, 40, 60)
COLOR_FLOOR = (24, 30, 46)
COLOR_TEXT_WHITE = (245, 248, 255)
COLOR_TEXT_GOLD = (255, 215, 60)
COLOR_TEXT_MUTED = (140, 160, 190)

# Powerup Types
class PowerUpType:
    DOUBLE_ARROW = "double_arrow"   # Shoot 2 arrows simultaneously
    SHIELD = "shield"               # 1-hit invulnerability barrier
    SLOW_MO = "slow_mo"             # 50% slow down for 6 seconds
    DYNAMITE = "dynamite"           # Instantly splits all bubbles on screen
    EXTRA_LIFE = "extra_life"       # +1 Heart
