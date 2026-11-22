"""
medals.py - Tiered Achievement Medals (Bronze, Silver, Gold, Platinum).
Renders circular metallic badges with specular glints and ribbon tails.
"""

import math
import pygame


def draw_medal(surface: pygame.Surface, x: int, y: int, tier: str, radius: int = 24):
    """
    Renders metallic circular medal badge.
    Tiers: 'bronze', 'silver', 'gold', 'platinum'
    """
    if not tier:
        return

    cx, cy = x, y

    # Palette mappings
    palettes = {
        "bronze": {
            "outer": (140, 75, 40),
            "rim": (185, 110, 60),
            "inner": (215, 140, 80),
            "hi": (255, 195, 140),
            "ribbon": (40, 110, 180)
        },
        "silver": {
            "outer": (130, 140, 150),
            "rim": (185, 195, 205),
            "inner": (220, 225, 235),
            "hi": (255, 255, 255),
            "ribbon": (180, 40, 60)
        },
        "gold": {
            "outer": (190, 130, 20),
            "rim": (235, 175, 35),
            "inner": (255, 215, 65),
            "hi": (255, 250, 180),
            "ribbon": (40, 140, 70)
        },
        "platinum": {
            "outer": (70, 140, 180),
            "rim": (120, 210, 245),
            "inner": (195, 245, 255),
            "hi": (255, 255, 255),
            "ribbon": (140, 60, 190)
        }
    }

    p = palettes.get(tier.lower(), palettes["bronze"])

    # 1. Hanging Ribbon Tails
    rw = int(radius * 0.45)
    rh = int(radius * 1.2)
    # Left ribbon tail
    pygame.draw.polygon(surface, p["ribbon"], [
        (cx - rw, cy + radius - 4),
        (cx - rw - 6, cy + radius + rh),
        (cx - 2, cy + radius + rh - 6),
        (cx, cy + radius - 4)
    ])
    # Right ribbon tail
    pygame.draw.polygon(surface, p["ribbon"], [
        (cx, cy + radius - 4),
        (cx + 2, cy + radius + rh - 6),
        (cx + rw + 6, cy + radius + rh),
        (cx + rw, cy + radius - 4)
    ])

    # 2. Outer Bevel Rim
    pygame.draw.circle(surface, p["outer"], (cx, cy), radius)
    pygame.draw.circle(surface, p["rim"], (cx, cy), radius - 3)

    # 3. Inner Center Disc
    pygame.draw.circle(surface, p["inner"], (cx, cy), radius - 6)

    # 4. Embossed Star
    star_pts = []
    star_r_out = radius * 0.52
    star_r_in = radius * 0.24
    for i in range(10):
        r = star_r_out if i % 2 == 0 else star_r_in
        ang = math.radians(i * 36 - 90)
        star_pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    pygame.draw.polygon(surface, p["outer"], star_pts)

    # 5. Glossy Specular Glint
    glint_x = cx - int(radius * 0.35)
    glint_y = cy - int(radius * 0.35)
    pygame.draw.circle(surface, p["hi"], (glint_x, glint_y), int(radius * 0.24))


def get_medal_for_score(score: int) -> str:
    if score >= 40:
        return "platinum"
    elif score >= 30:
        return "gold"
    elif score >= 20:
        return "silver"
    elif score >= 10:
        return "bronze"
    return ""
