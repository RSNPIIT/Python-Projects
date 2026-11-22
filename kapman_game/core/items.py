"""Kapman Game - Bonus Collectibles & Floating Score Badges"""
import pygame
from core.constants import TILE_SIZE, BONUS_ITEM_DURATION

BONUS_SCARAB = "scarab"
BONUS_ANKH = "ankh"
BONUS_EYE = "eye"
BONUS_RUBY = "ruby"

BONUS_DEFINITIONS = {
    1: {"type": BONUS_SCARAB, "points": 100, "label": "SCARAB"},
    2: {"type": BONUS_ANKH, "points": 300, "label": "ANKH"},
    3: {"type": BONUS_EYE, "points": 500, "label": "EYE OF HORUS"},
    4: {"type": BONUS_RUBY, "points": 1000, "label": "ROYAL RUBY"},
}

class BonusItem:
    def __init__(self, level: int = 1, row: float = 17.0, col: float = 13.5):
        self.row = row
        self.col = col
        self.x = (col + 0.5) * TILE_SIZE
        self.y = (row + 0.5) * TILE_SIZE
        item_info = BONUS_DEFINITIONS.get(min(level, 4), BONUS_DEFINITIONS[1])
        self.type = item_info["type"]
        self.points = item_info["points"]
        self.label = item_info["label"]
        self.timer = BONUS_ITEM_DURATION
        self.alive = True

    def update(self, dt: float) -> bool:
        self.timer -= dt
        if self.timer <= 0:
            self.alive = False
        return self.alive


class FloatingScore:
    def __init__(self, x: float, y: float, points: int, color: tuple[int, int, int] = (255, 220, 80)):
        self.x = x
        self.y = y
        self.text = f"+{points}"
        self.color = color
        self.lifetime = 0.85
        self.max_lifetime = 0.85
        self.vy = -35.0

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        self.y += self.vy * dt
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, offset_y: int = 0):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha > 0:
            txt_surf = font.render(self.text, True, self.color)
            txt_surf.set_alpha(alpha)
            surface.blit(txt_surf, txt_surf.get_rect(center=(int(self.x), int(self.y + offset_y))))
