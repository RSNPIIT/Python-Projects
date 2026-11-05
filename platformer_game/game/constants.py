"""Tuning constants, colour palettes and asset-free visual identity."""

from __future__ import annotations

SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
WINDOW_TITLE = "THORNSPIRE  ·  climb the bramble"

TITLE = "THORNSPIRE"
SUBTITLE = "climb the bramble · outrun the dark"

# ---------------------------------------------------------------------------
# Physics (pixels / seconds)
# ---------------------------------------------------------------------------
GRAVITY = 2300.0
MAX_FALL = 1180.0

MOVE_SPEED = 340.0
GROUND_ACCEL = 3000.0
AIR_ACCEL = 2000.0
GROUND_FRICTION = 3200.0
AIR_FRICTION = 500.0

JUMP_VELOCITY = 740.0
JUMP_CUT = 0.42
JUMP_HOLD_TIME = 0.26          # seconds of low-gravity lift while Space is held
JUMP_HOLD_GRAVITY = 0.60       # gravity multiplier during the lift window
JUMP_CUT_SPEED = 380.0         # upward speed cap once Space is released
COYOTE_TIME = 0.11
JUMP_BUFFER = 0.14

WALL_SLIDE_SPEED = 150.0
WALL_JUMP_X = 350.0
WALL_JUMP_Y = 710.0
WALL_STICK_TIME = 0.09

CLIMB_SPEED = 185.0
CLIMB_HORIZONTAL = 120.0

DASH_SPEED = 830.0
DASH_TIME = 0.155
DASH_COOLDOWN = 0.85

PLAYER_W = 28
PLAYER_H = 46

MAX_HEARTS = 5
START_HEARTS = 3
INVULN_TIME = 1.45

MAX_ARMOR = 3
START_ARMOR = 1
ARMOR_INVULN = 0.95

# ---------------------------------------------------------------------------
# World
# ---------------------------------------------------------------------------
TILE = 40
CHUNK_W = 1440
CHUNKS_PER_BIOME = 9
WORLD_FLOOR = 1150.0
FALL_LIMIT = 1080.0
TRIAL_TIME = 90.0
TRIAL_CHRONO = 5.0

CAMERA_SMOOTH_X = 8.0
CAMERA_SMOOTH_Y = 5.0
CAMERA_LOOKAHEAD = 95.0

# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
COIN_VALUE = 10
GEM_VALUE = 100
HEART_VALUE = 25
CHRONO_VALUE = 40
ARMOR_VALUE = 60
CHECKPOINT_VALUE = 50
LOOP_BONUS = 500
DISTANCE_POINTS = 2

COMBO_WINDOW = 3.6
COMBO_STEP = 5          # pickups per extra multiplier
COMBO_MAX = 5

# ---------------------------------------------------------------------------
# Palette.  All colours are 0-255 RGB tuples; shaders receive them normalised.
# ---------------------------------------------------------------------------
BIOMES = [
    {
        "name": "VERDANT HOLLOW",
        "tagline": "where the roots remember",
        "sky_top": (4, 9, 16),
        "sky_bottom": (22, 62, 56),
        "haze": (34, 104, 88),
        "accent": (104, 255, 188),
        "accent2": (255, 198, 96),
        "fog": (7, 22, 24),
        "rock": (22, 46, 42),
        "rock_dark": (10, 25, 23),
        "rock_light": (38, 74, 64),
        "moss": (84, 206, 142),
        "moss_dark": (36, 108, 78),
        "thorn": (223, 255, 219),
        "thorn_dark": (130, 190, 158),
        "danger": (255, 102, 112),
        "coin": (255, 201, 92),
        "gem": (170, 132, 255),
        "vine": (90, 140, 102),
        "orb": (140, 255, 210),
    },
    {
        "name": "EMBER REACH",
        "tagline": "the embers still climb",
        "sky_top": (16, 6, 14),
        "sky_bottom": (84, 30, 20),
        "haze": (134, 52, 30),
        "accent": (255, 128, 78),
        "accent2": (255, 214, 128),
        "fog": (30, 12, 12),
        "rock": (48, 28, 27),
        "rock_dark": (26, 14, 14),
        "rock_light": (82, 48, 38),
        "moss": (226, 112, 58),
        "moss_dark": (128, 54, 35),
        "thorn": (255, 218, 168),
        "thorn_dark": (190, 126, 84),
        "danger": (255, 86, 74),
        "coin": (255, 190, 80),
        "gem": (255, 100, 154),
        "vine": (120, 74, 56),
        "orb": (255, 176, 94),
    },
    {
        "name": "FROST WEALD",
        "tagline": "silence under the rime",
        "sky_top": (6, 12, 26),
        "sky_bottom": (30, 60, 94),
        "haze": (56, 104, 132),
        "accent": (124, 224, 255),
        "accent2": (214, 244, 255),
        "fog": (10, 20, 34),
        "rock": (30, 44, 60),
        "rock_dark": (14, 24, 36),
        "rock_light": (58, 78, 96),
        "moss": (132, 202, 232),
        "moss_dark": (58, 108, 138),
        "thorn": (228, 248, 255),
        "thorn_dark": (140, 180, 208),
        "danger": (255, 120, 140),
        "coin": (255, 216, 126),
        "gem": (150, 164, 255),
        "vine": (94, 124, 148),
        "orb": (150, 230, 255),
    },
    {
        "name": "VOID BLOOM",
        "tagline": "something flowers in the dark",
        "sky_top": (10, 4, 22),
        "sky_bottom": (46, 18, 68),
        "haze": (82, 32, 96),
        "accent": (220, 120, 255),
        "accent2": (122, 255, 232),
        "fog": (16, 8, 28),
        "rock": (36, 24, 50),
        "rock_dark": (19, 12, 30),
        "rock_light": (68, 46, 86),
        "moss": (180, 112, 242),
        "moss_dark": (96, 52, 140),
        "thorn": (246, 222, 255),
        "thorn_dark": (170, 120, 200),
        "danger": (255, 100, 160),
        "coin": (255, 210, 140),
        "gem": (255, 122, 224),
        "vine": (108, 80, 136),
        "orb": (230, 150, 255),
    },
]

BIOME_COUNT = len(BIOMES)

# Shared UI palette ---------------------------------------------------------
UI = {
    "ivory": (240, 240, 230),
    "muted": (156, 172, 168),
    "dim": (98, 112, 112),
    "ink": (7, 12, 14),
    "panel": (10, 16, 18),
    "gold": (255, 205, 110),
    "gem": (180, 150, 255),
    "danger": (255, 96, 110),
    "heal": (126, 255, 176),
}

# Player palette -----------------------------------------------------------
PLAYER = {
    "cloak": (34, 48, 62),
    "cloak_light": (58, 80, 96),
    "cloak_dark": (18, 28, 38),
    "trim": (200, 222, 214),
    "scarf": (232, 92, 84),
    "scarf_dark": (168, 52, 58),
    "skin": (12, 16, 22),
    "eye": (128, 255, 224),
    "lantern": (255, 196, 112),
    "boot": (24, 28, 36),
}

# Fonts --------------------------------------------------------------------
FONT_TITLE = "copperplate,didot,georgia,dejavuserif"
FONT_UI = "avenirnext,helveticaneue,dejavusans,arial"
FONT_UI_CONDENSED = "avenirnextcondensed,avenirnext,dejavusans,arial"
FONT_MONO = "menlo,sfnsmono,dejavusansmono,couriernew"

SAVE_NAME = "save.json"
