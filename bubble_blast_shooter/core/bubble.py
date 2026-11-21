"""Bubble Blast Shooter - 3D Glossy Sphere Renderer & Bubble Model"""
import pygame
from core.constants import BUBBLE_RADIUS, BUBBLE_COLORS

_SPHERE_CACHE: dict[tuple[int, int], pygame.Surface] = {}

def get_bubble_surface(color_id: int, radius: int = BUBBLE_RADIUS) -> pygame.Surface:
    """Returns a pre-rendered 3D glossy marble sphere surface for the given color ID."""
    key = (color_id, radius)
    if key in _SPHERE_CACHE:
        return _SPHERE_CACHE[key]

    size = radius * 2 + 4
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2
    cy = size // 2
    base_col = BUBBLE_COLORS.get(color_id, (200, 200, 200))

    # 1. Subtle dark drop shadow
    pygame.draw.circle(surf, (10, 12, 20, 70), (cx, cy + 2), radius)

    # 2. Main saturated spherical body
    pygame.draw.circle(surf, base_col, (cx, cy), radius)

    # 3. Outer rim shading (darkened edge)
    dark_rim = (max(0, base_col[0] - 65), max(0, base_col[1] - 65), max(0, base_col[2] - 65))
    pygame.draw.circle(surf, (*dark_rim, 180), (cx, cy), radius, width=2)

    # 4. Inner bottom ambient reflection / translucency
    bot_refl_col = (min(255, base_col[0] + 55), min(255, base_col[1] + 55), min(255, base_col[2] + 55))
    bot_surf = pygame.Surface((radius * 2, int(radius * 0.9)), pygame.SRCALPHA)
    pygame.draw.ellipse(bot_surf, (*bot_refl_col, 85), (0, 0, radius * 2, int(radius * 0.9)))
    surf.blit(bot_surf, (cx - radius, cy + int(radius * 0.05)))

    # 5. Top-Left Primary Specular Glint (Sharp white highlight)
    glint_x = cx - int(radius * 0.35)
    glint_y = cy - int(radius * 0.35)
    glint_w = max(4, int(radius * 0.42))
    glint_h = max(3, int(radius * 0.28))
    glint_surf = pygame.Surface((glint_w * 2, glint_h * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(glint_surf, (255, 255, 255, 230), (0, 0, glint_w * 2, glint_h * 2))
    # Rotate glint slightly (-30 deg)
    rotated_glint = pygame.transform.rotate(glint_surf, -25)
    surf.blit(rotated_glint, rotated_glint.get_rect(center=(glint_x, glint_y)))

    # 6. Secondary micro-specular dot
    micro_x = cx + int(radius * 0.28)
    micro_y = cy - int(radius * 0.40)
    pygame.draw.circle(surf, (255, 255, 255, 170), (micro_x, micro_y), max(1, radius // 9))

    _SPHERE_CACHE[key] = surf
    return surf


class Bubble:
    def __init__(self, color_id: int):
        self.color_id = color_id
        self.anim_scale = 1.0
        self.marked_for_removal = False

    def draw(self, surface: pygame.Surface, cx: float, cy: float, radius: int = BUBBLE_RADIUS):
        surf = get_bubble_surface(self.color_id, radius)
        surface.blit(surf, surf.get_rect(center=(int(cx), int(cy))))
