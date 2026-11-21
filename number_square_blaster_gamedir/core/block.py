"""Block Blast - Brick & Block Entity"""
import pygame
from core.constants import BLOCK_COLORS, BLOCK_WIDTH, BLOCK_HEIGHT

class Block:
    def __init__(self, col: int, row: int, x: float, y: float, hp: int, is_bomb: bool = False):
        self.col = col
        self.row = row
        self.x = x
        self.y = y
        self.width = BLOCK_WIDTH
        self.height = BLOCK_HEIGHT
        self.hp = hp
        self.max_hp = hp
        self.is_bomb = is_bomb
        self.flash_timer = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def color(self) -> tuple[int, int, int]:
        if self.is_bomb:
            return (255, 45, 65)  # Fiery red for bomb
        # Choose color by HP scale
        tier = min(len(BLOCK_COLORS) - 1, int(self.hp / 15))
        return BLOCK_COLORS[tier]

    def hit(self, damage: int = 1) -> bool:
        """Takes damage. Returns True if destroyed."""
        self.hp -= damage
        self.flash_timer = 0.08
        return self.hp <= 0

    def update(self, dt: float):
        if self.flash_timer > 0:
            self.flash_timer -= dt

    def draw(self, surface: pygame.Surface, offset: tuple[float, float], font: pygame.font.Font):
        rx = self.x + offset[0]
        ry = self.y + offset[1]
        r = pygame.Rect(rx, ry, self.width, self.height)

        # Base color or flash white on hit
        if self.flash_timer > 0:
            col = (255, 255, 255)
        else:
            col = self.color

        # Draw rounded card with beveled modern appearance
        pygame.draw.rect(surface, col, r, border_radius=8)

        # Inner glossy highlight on top half
        inner_highlight = pygame.Rect(rx + 2, ry + 2, self.width - 4, self.height * 0.42)
        highlight_col = (min(255, col[0] + 45), min(255, col[1] + 45), min(255, col[2] + 45))
        pygame.draw.rect(surface, highlight_col, inner_highlight, border_radius=6)

        # Subtle dark border
        pygame.draw.rect(surface, (10, 12, 18), r, width=2, border_radius=8)

        # HP Text or Bomb Icon
        if self.is_bomb:
            text_str = "💣"
            text_surf = font.render(text_str, True, (255, 255, 255))
        else:
            text_str = str(self.hp)
            text_surf = font.render(text_str, True, (15, 18, 26) if col[0] > 180 and col[1] > 180 else (255, 255, 255))

        t_rect = text_surf.get_rect(center=r.center)
        surface.blit(text_surf, t_rect)
