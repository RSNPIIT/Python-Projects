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

# Difficulties
DIFFICULTIES = {
    "Classic": {
        "name": "Classic",
        "gap": 195,
        "speed": 3.8,
        "desc": "The authentic arcade challenge (OG spacing & speed)"
    },
    "Chill": {
        "name": "Chill",
        "gap": 240,
        "speed": 3.1,
        "desc": "Relaxed gaps and gentle scroll speed for relaxed soaring"
    },
    "Hardcore": {
        "name": "Hardcore",
        "gap": 165,
        "speed": 4.6,
        "desc": "Razor-sharp pipe margins and brisk scrolling"
    }
}

# Skins Configuration
SKINS = {
    "KFlapper": {
        "name": "KFlapper (Classic)",
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

# Time-of-Day / Sky Themes
TIME_THEMES = {
    "Day": {
        "name": "Day",
        "sky_top": (100, 190, 240),
        "sky_bottom": (195, 235, 250),
        "cloud_color": (255, 255, 255),
        "cloud_shadow": (215, 235, 245),
        "city_color": (155, 205, 195),
        "hill_color": (110, 185, 120),
        "bush_color": (80, 160, 90),
        "pipe_body": (115, 190, 45),
        "pipe_highlight": (160, 225, 75),
        "pipe_shadow": (75, 135, 30),
        "pipe_dark": (45, 95, 20),
        "ground_top": (110, 200, 50),
        "ground_body": (220, 185, 120),
        "ground_stripe": (190, 150, 95)
    },
    "Sunset": {
        "name": "Sunset",
        "sky_top": (80, 45, 120),
        "sky_bottom": (245, 130, 90),
        "cloud_color": (255, 200, 190),
        "cloud_shadow": (180, 120, 140),
        "city_color": (100, 60, 110),
        "hill_color": (120, 60, 80),
        "bush_color": (90, 40, 60),
        "pipe_body": (95, 165, 55),
        "pipe_highlight": (145, 200, 85),
        "pipe_shadow": (65, 115, 35),
        "pipe_dark": (40, 80, 25),
        "ground_top": (140, 130, 50),
        "ground_body": (160, 100, 80),
        "ground_stripe": (130, 75, 60)
    },
    "Night": {
        "name": "Night",
        "sky_top": (12, 18, 42),
        "sky_bottom": (35, 50, 90),
        "cloud_color": (70, 85, 125),
        "cloud_shadow": (40, 50, 80),
        "city_color": (25, 35, 65),
        "hill_color": (20, 40, 50),
        "bush_color": (15, 30, 35),
        "pipe_body": (70, 140, 60),
        "pipe_highlight": (105, 180, 90),
        "pipe_shadow": (45, 95, 40),
        "pipe_dark": (25, 60, 25),
        "ground_top": (50, 120, 60),
        "ground_body": (90, 85, 95),
        "ground_stripe": (70, 65, 75)
    }
}
THEME_KEYS = list(TIME_THEMES.keys())
