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
CHUNKS_PER_BIOME = 3
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
    {
        "name": "SUNKEN ABYSS",
        "tagline": "drowned shrines of the ancients",
        "sky_top": (2, 8, 18),
        "sky_bottom": (12, 42, 58),
        "haze": (20, 85, 100),
        "accent": (64, 240, 220),
        "accent2": (140, 255, 230),
        "fog": (4, 16, 26),
        "rock": (18, 38, 48),
        "rock_dark": (8, 20, 28),
        "rock_light": (32, 64, 76),
        "moss": (52, 180, 170),
        "moss_dark": (24, 96, 92),
        "thorn": (180, 245, 240),
        "thorn_dark": (90, 175, 170),
        "danger": (255, 90, 130),
        "coin": (255, 215, 110),
        "gem": (100, 220, 255),
        "vine": (50, 110, 116),
        "orb": (80, 240, 230),
    },
    {
        "name": "SOLAR DUNES",
        "tagline": "sun-scorched shifting sands",
        "sky_top": (28, 12, 18),
        "sky_bottom": (110, 52, 24),
        "haze": (175, 96, 42),
        "accent": (255, 185, 70),
        "accent2": (255, 235, 140),
        "fog": (35, 18, 16),
        "rock": (65, 42, 28),
        "rock_dark": (35, 22, 14),
        "rock_light": (95, 62, 40),
        "moss": (230, 155, 60),
        "moss_dark": (145, 88, 30),
        "thorn": (255, 230, 175),
        "thorn_dark": (195, 140, 90),
        "danger": (255, 75, 60),
        "coin": (255, 225, 95),
        "gem": (255, 120, 80),
        "vine": (140, 95, 55),
        "orb": (255, 205, 105),
    },
    {
        "name": "CELESTIAL SPIRE",
        "tagline": "where stars graze the thorns",
        "sky_top": (14, 6, 28),
        "sky_bottom": (45, 24, 78),
        "haze": (90, 55, 140),
        "accent": (195, 140, 255),
        "accent2": (255, 215, 130),
        "fog": (18, 10, 32),
        "rock": (42, 30, 60),
        "rock_dark": (22, 15, 34),
        "rock_light": (72, 52, 98),
        "moss": (160, 110, 235),
        "moss_dark": (88, 52, 135),
        "thorn": (240, 220, 255),
        "thorn_dark": (165, 135, 195),
        "danger": (255, 95, 175),
        "coin": (255, 210, 110),
        "gem": (225, 130, 255),
        "vine": (105, 78, 135),
        "orb": (210, 170, 255),
    },
    {
        "name": "TOXIC MIRE",
        "tagline": "acid whispers in the canopy",
        "sky_top": (8, 16, 10),
        "sky_bottom": (26, 68, 32),
        "haze": (55, 130, 60),
        "accent": (140, 255, 70),
        "accent2": (220, 255, 130),
        "fog": (12, 25, 14),
        "rock": (30, 48, 32),
        "rock_dark": (16, 28, 18),
        "rock_light": (50, 78, 52),
        "moss": (115, 215, 65),
        "moss_dark": (58, 120, 34),
        "thorn": (215, 255, 180),
        "thorn_dark": (130, 190, 105),
        "danger": (255, 80, 95),
        "coin": (255, 220, 85),
        "gem": (110, 255, 150),
        "vine": (75, 125, 70),
        "orb": (160, 255, 90),
    },
    {
        "name": "CRIMSON CITADEL",
        "tagline": "under the blood-red moon",
        "sky_top": (22, 4, 8),
        "sky_bottom": (82, 14, 24),
        "haze": (135, 28, 42),
        "accent": (255, 70, 90),
        "accent2": (255, 170, 140),
        "fog": (28, 8, 12),
        "rock": (52, 22, 26),
        "rock_dark": (28, 10, 12),
        "rock_light": (88, 38, 44),
        "moss": (220, 55, 75),
        "moss_dark": (125, 28, 40),
        "thorn": (255, 205, 215),
        "thorn_dark": (185, 95, 110),
        "danger": (255, 45, 65),
        "coin": (255, 200, 90),
        "gem": (255, 80, 130),
        "vine": (125, 50, 60),
        "orb": (255, 100, 120),
    },
    {
        "name": "AETHER HEIGHTS",
        "tagline": "above the cloudline",
        "sky_top": (10, 16, 32),
        "sky_bottom": (64, 80, 125),
        "haze": (110, 135, 190),
        "accent": (155, 215, 255),
        "accent2": (255, 210, 235),
        "fog": (18, 26, 44),
        "rock": (38, 48, 68),
        "rock_dark": (20, 26, 40),
        "rock_light": (68, 84, 114),
        "moss": (135, 185, 240),
        "moss_dark": (68, 104, 155),
        "thorn": (230, 242, 255),
        "thorn_dark": (155, 180, 210),
        "danger": (255, 115, 145),
        "coin": (255, 215, 120),
        "gem": (195, 165, 255),
        "vine": (95, 120, 155),
        "orb": (175, 230, 255),
    },
]

BIOME_COUNT = len(BIOMES)
TOTAL_LEVELS = 100

# ---------------------------------------------------------------------------
# Difficulty Modes
# ---------------------------------------------------------------------------
DIFFICULTY_MODES = ["easy", "medium", "hard"]

DIFFICULTIES = {
    "easy": {
        "name": "EASY",
        "tagline": "forgiving ascent · 5 lives · 2 shields",
        "desc": "Smooth pace & extra shields",
        "hearts": 5,
        "max_hearts": 6,
        "armor": 2,
        "speed_mult": 0.85,
        "proj_mult": 0.82,
        "invuln_mult": 1.35,
        "color": (88, 245, 166),
        "glow": (146, 255, 214),
    },
    "medium": {
        "name": "MEDIUM",
        "tagline": "true challenge · 3 lives · 1 shield · brisk foes",
        "desc": "Balanced climb & brisk foes",
        "hearts": 3,
        "max_hearts": 5,
        "armor": 1,
        "speed_mult": 1.10,
        "proj_mult": 1.10,
        "invuln_mult": 1.0,
        "color": (255, 198, 76),
        "glow": (255, 136, 86),
    },
    "hard": {
        "name": "HARD",
        "tagline": "brutal gauntlet · 2 lives · 0 shields · relentless speed",
        "desc": "No shields & fierce gauntlets",
        "hearts": 2,
        "max_hearts": 4,
        "armor": 0,
        "speed_mult": 1.34,
        "proj_mult": 1.38,
        "invuln_mult": 0.72,
        "color": (255, 84, 114),
        "glow": (255, 148, 76),
    },
}

# ---------------------------------------------------------------------------
# Hero Customization
# ---------------------------------------------------------------------------
HERO_CLOAKS = [
    {
        "name": "Dusk Wanderer",
        "cloak": (34, 48, 62),
        "cloak_light": (58, 80, 96),
        "cloak_dark": (18, 28, 38),
        "trim": (200, 222, 214),
        "eye": (128, 255, 224),
    },
    {
        "name": "Crimson Ember",
        "cloak": (68, 22, 26),
        "cloak_light": (118, 42, 48),
        "cloak_dark": (38, 12, 16),
        "trim": (255, 195, 165),
        "eye": (255, 120, 80),
    },
    {
        "name": "Emerald Warden",
        "cloak": (20, 52, 38),
        "cloak_light": (38, 92, 66),
        "cloak_dark": (12, 32, 22),
        "trim": (185, 245, 205),
        "eye": (120, 255, 160),
    },
    {
        "name": "Royal Amethyst",
        "cloak": (46, 24, 66),
        "cloak_light": (82, 45, 112),
        "cloak_dark": (26, 12, 40),
        "trim": (225, 190, 255),
        "eye": (205, 140, 255),
    },
    {
        "name": "Solar Gold",
        "cloak": (68, 48, 20),
        "cloak_light": (120, 88, 38),
        "cloak_dark": (40, 28, 12),
        "trim": (255, 235, 160),
        "eye": (255, 220, 100),
    },
    {
        "name": "Arctic Frost",
        "cloak": (30, 58, 76),
        "cloak_light": (60, 102, 130),
        "cloak_dark": (16, 34, 48),
        "trim": (220, 245, 255),
        "eye": (140, 230, 255),
    },
    {
        "name": "Shadow Stalker",
        "cloak": (18, 18, 24),
        "cloak_light": (38, 38, 48),
        "cloak_dark": (8, 8, 12),
        "trim": (150, 150, 170),
        "eye": (255, 80, 110),
    },
    {
        "name": "Cyber Neon",
        "cloak": (24, 20, 52),
        "cloak_light": (50, 42, 98),
        "cloak_dark": (14, 10, 32),
        "trim": (100, 255, 240),
        "eye": (255, 110, 230),
    },
]

HERO_SCARFS = [
    {
        "name": "Ruby Scarf",
        "scarf": (232, 92, 84),
        "scarf_dark": (168, 52, 58),
    },
    {
        "name": "Amber Silk",
        "scarf": (245, 180, 60),
        "scarf_dark": (180, 120, 30),
    },
    {
        "name": "Electric Aqua",
        "scarf": (65, 220, 245),
        "scarf_dark": (35, 150, 175),
    },
    {
        "name": "Toxic Lime",
        "scarf": (145, 245, 75),
        "scarf_dark": (90, 175, 40),
    },
    {
        "name": "Astral Violet",
        "scarf": (195, 110, 250),
        "scarf_dark": (135, 65, 185),
    },
    {
        "name": "Snow Pearl",
        "scarf": (240, 245, 250),
        "scarf_dark": (175, 185, 195),
    },
    {
        "name": "Midnight Obsidian",
        "scarf": (45, 45, 55),
        "scarf_dark": (20, 20, 28),
    },
]

HERO_HEADGEARS = [
    {"id": "hood", "name": "Classic Hood", "desc": "Pointed traveler's cowl"},
    {"id": "crown", "name": "Golden Crown", "desc": "Gleaming royal circlet"},
    {"id": "horns", "name": "Bramble Horns", "desc": "Curved stag-thorn antlers"},
    {"id": "bandana", "name": "Ninja Bandana", "desc": "Forehead plate with ribbons"},
    {"id": "halo", "name": "Radiant Halo", "desc": "Floating luminous celestial ring"},
    {"id": "wizard", "name": "Sorcerer Hat", "desc": "Curved brim mystical cap"},
]

HERO_TRAILS = [
    {"id": "classic", "name": "Classic Scarf", "desc": "Standard flowing cloth trail"},
    {"id": "flame", "name": "Fire Embers", "desc": "Fiery ember sparks drifting behind"},
    {"id": "stars", "name": "Stardust Sparkles", "desc": "Twinkling star motes"},
    {"id": "ghost", "name": "Phantom Echoes", "desc": "Ethereal translucent silhouettes"},
    {"id": "prismatic", "name": "Rainbow Aura", "desc": "Shifting spectrum hue wave"},
]

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
