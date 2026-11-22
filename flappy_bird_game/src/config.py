"""
config.py - Centralized configuration, physics parameters, themes, and skin definitions for KFlapper.
"""

# Screen Resolution (HD 16:9 Arcade Widescreen)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "KFLAPPER // The OG Classic Flappy Bird (HD Edition)"

# World & Ground Dimensions
GROUND_HEIGHT = 110
PLAYABLE_HEIGHT = SCREEN_HEIGHT - GROUND_HEIGHT

# Bird Physics Parameters (scaled for 720p HD)
BIRD_X = 320                       # Horizontal position of bird
BIRD_RADIUS = 24                   # Collision radius
GRAVITY = 0.50                     # Downward acceleration per frame
FLAP_STRENGTH = -9.2               # Upward impulse upon flap
MAX_FALL_SPEED = 12.0              # Terminal downward velocity
TILT_UP_SPEED = 450.0              # Degrees per second when pitching up
TILT_DOWN_SPEED = 240.0            # Degrees per second when diving down
MAX_UPWARD_ANGLE = 26.0            # Upward tilt limit
MAX_DOWNWARD_ANGLE = -90.0         # Steep nosedive limit
FALL_ROTATION_DELAY = 0.16         # Seconds before nose drops after a flap

# Pipe Parameters
PIPE_SPEED = 3.8
PIPE_WIDTH = 96
PIPE_CAP_HEIGHT = 38
PIPE_CAP_OVERHANG = 10
PIPE_SPACING = 360
PIPE_MIN_HEIGHT = 90

# Difficulties Configuration with GUI metadata
DIFFICULTIES = {
    "Chill": {
        "name": "Chill",
        "tag": "EASY",
        "gap": 240,
        "speed": 3.1,
        "badge_color": (74, 222, 128),       # Neon green
        "desc": "Wide 240px Gap • Gentle 3.1 Speed • Smooth soaring"
    },
    "Classic": {
        "name": "Classic",
        "tag": "OG",
        "gap": 195,
        "speed": 3.8,
        "badge_color": (56, 189, 248),       # Neon cyan
        "desc": "OG 195px Gap • 3.8 Authentic Speed • The true challenge"
    },
    "Hardcore": {
        "name": "Hardcore",
        "tag": "PRO",
        "gap": 165,
        "speed": 4.6,
        "badge_color": (244, 63, 94),        # Neon crimson
        "desc": "Razor-tight 165px Gap • 4.6 Fast Speed • High reflex test"
    }
}
DIFF_KEYS = list(DIFFICULTIES.keys())

# Skins Configuration
SKINS = {
    "KFlapper": {
        "name": "KFlapper (Classic)",
        "short_name": "KFlapper",
        "body_color": (255, 215, 0),        # Golden yellow
        "belly_color": (255, 248, 220),     # Soft cream
        "wing_color": (255, 165, 0),        # Vibrant orange
        "beak_color": (255, 69, 0),         # Fiery orange-red
        "eye_pupil": (20, 20, 25),
        "eye_sclera": (255, 255, 255),
        "trail_color": (255, 220, 100),
        "crest": False
    },
    "CyberFalcon": {
        "name": "Cyber Falcon",
        "short_name": "Cyber Falcon",
        "body_color": (0, 220, 255),        # Electric cyan
        "belly_color": (200, 250, 255),     # Ice white
        "wing_color": (255, 0, 128),        # Neon magenta
        "beak_color": (255, 215, 0),        # Laser yellow
        "eye_pupil": (255, 0, 80),          # Neon visor
        "eye_sclera": (10, 20, 40),
        "trail_color": (0, 255, 220),
        "crest": True
    },
    "Phoenix": {
        "name": "Crimson Phoenix",
        "short_name": "Phoenix",
        "body_color": (240, 40, 50),        # Fiery ruby
        "belly_color": (255, 180, 50),      # Amber flame
        "wing_color": (255, 140, 0),        # Molten gold
        "beak_color": (255, 230, 0),        # Sunburst
        "eye_pupil": (20, 10, 10),
        "eye_sclera": (255, 255, 255),
        "trail_color": (255, 80, 20),
        "crest": True
    },
    "MidnightRaven": {
        "name": "Midnight Raven",
        "short_name": "Raven",
        "body_color": (35, 38, 55),         # Obsidian navy
        "belly_color": (60, 65, 90),        # Slate purple
        "wing_color": (120, 80, 180),       # Royal violet
        "beak_color": (220, 180, 50),       # Antique brass
        "eye_pupil": (230, 40, 40),         # Crimson glint
        "eye_sclera": (255, 255, 255),
        "trail_color": (160, 120, 240),
        "crest": False
    },
    "Emerald": {
        "name": "Emerald Parakeet",
        "short_name": "Emerald",
        "body_color": (46, 204, 113),       # Emerald green
        "belly_color": (200, 247, 197),     # Mint green
        "wing_color": (26, 188, 156),       # Turquoise
        "beak_color": (243, 156, 18),       # Warm amber
        "eye_pupil": (20, 30, 25),
        "eye_sclera": (255, 255, 255),
        "trail_color": (80, 230, 160),
        "crest": False
    }
}
SKIN_KEYS = list(SKINS.keys())

# Progressive Biome Milestones (0-29 Earth, 30-59 Martian, 60-89 Cyber, 90+ Night)
BIOMES = [
    {
        "id": "earth",
        "name": "Earth Meadow",
        "threshold": 0,
        "banner": "SECTOR 1 // EARTH MEADOW",
        "accent": (74, 222, 128),
        "sky_top": (95, 185, 240),
        "sky_bottom": (195, 235, 250),
        "cloud_color": (255, 255, 255),
        "cloud_shadow": (210, 230, 245),
        "city_color": (150, 195, 185),
        "hill_color": (105, 180, 115),
        "bush_color": (75, 155, 85),
        "pipe_body": (115, 190, 45),
        "pipe_highlight": (160, 225, 75),
        "pipe_shadow": (75, 135, 30),
        "pipe_dark": (45, 95, 20),
        "ground_top": (110, 200, 50),
        "ground_body": (220, 185, 120),
        "ground_stripe": (190, 150, 95),
        "ambient_fx": "feathers"
    },
    {
        "id": "martian",
        "name": "Martian Red Wasteland",
        "threshold": 30,
        "banner": "SECTOR 2 // MARTIAN RED DUST",
        "accent": (239, 68, 68),
        "sky_top": (100, 20, 25),
        "sky_bottom": (235, 75, 45),
        "cloud_color": (210, 95, 70),
        "cloud_shadow": (140, 50, 40),
        "city_color": (125, 40, 42),
        "hill_color": (165, 50, 45),
        "bush_color": (110, 30, 30),
        "pipe_body": (185, 55, 45),
        "pipe_highlight": (250, 130, 80),
        "pipe_shadow": (125, 32, 25),
        "pipe_dark": (65, 15, 15),
        "ground_top": (220, 80, 50),
        "ground_body": (155, 50, 40),
        "ground_stripe": (115, 35, 30),
        "ambient_fx": "red_dust"
    },
    {
        "id": "cyber",
        "name": "Cyber Neon City",
        "threshold": 60,
        "banner": "SECTOR 3 // CYBER SYNTHWAVE",
        "accent": (56, 189, 248),
        "sky_top": (18, 8, 42),
        "sky_bottom": (125, 20, 115),
        "cloud_color": (145, 60, 185),
        "cloud_shadow": (75, 25, 105),
        "city_color": (32, 22, 65),
        "hill_color": (50, 25, 88),
        "bush_color": (25, 12, 45),
        "pipe_body": (0, 195, 225),
        "pipe_highlight": (130, 250, 255),
        "pipe_shadow": (0, 115, 145),
        "pipe_dark": (0, 45, 75),
        "ground_top": (0, 235, 255),
        "ground_body": (28, 20, 45),
        "ground_stripe": (195, 0, 180),
        "ambient_fx": "cyber_sparks"
    },
    {
        "id": "night",
        "name": "Cosmic Midnight Aurora",
        "threshold": 90,
        "banner": "SECTOR 4 // COSMIC MIDNIGHT",
        "accent": (168, 85, 247),
        "sky_top": (8, 12, 28),
        "sky_bottom": (28, 45, 85),
        "cloud_color": (50, 80, 130),
        "cloud_shadow": (20, 32, 65),
        "city_color": (20, 28, 52),
        "hill_color": (16, 32, 44),
        "bush_color": (12, 22, 30),
        "pipe_body": (75, 115, 150),
        "pipe_highlight": (155, 195, 240),
        "pipe_shadow": (42, 65, 92),
        "pipe_dark": (20, 32, 50),
        "ground_top": (45, 130, 95),
        "ground_body": (42, 48, 65),
        "ground_stripe": (28, 32, 48),
        "ambient_fx": "stars"
    }
]

# Quick access mapping
TIME_THEMES = {b["id"]: b for b in BIOMES}
THEME_KEYS = [b["id"] for b in BIOMES]
