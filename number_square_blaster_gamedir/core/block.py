"""Block Blast - Polished Arcade Brick Entity"""
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
            return (240, 50, 60)
        tier = min(len(BLOCK_COLORS) - 1, int(self.hp / 14))
        return BLOCK_COLORS[tier]

    def hit(self, damage: int = 1) -> bool:
        self.hp -= damage
        self.flash_timer = 0.07
        return self.hp <= 0

    def update(self, dt: float):
        if self.flash_timer > 0:
            self.flash_timer -= dt

    def draw(self, surface: pygame.Surface, offset: tuple[float, float], font: pygame.font.Font):
        rx = int(self.x + offset[0])
        ry = int(self.y + offset[1])
        w = int(self.width)
        h = int(self.height)

        # 1. Soft Drop Shadow Underneath
        shadow_rect = pygame.Rect(rx + 2, ry + 4, w, h)
        shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 90), (0, 0, w, h), border_radius=10)
        surface.blit(shadow_surf, (rx + 2, ry + 4))

        # 2. Main Block Body
        block_rect = pygame.Rect(rx, ry, w, h)
        if self.flash_timer > 0:
            base_col = (255, 255, 255)
            border_col = (255, 255, 255)
        else:
            base_col = self.color
            border_col = (
                min(255, int(base_col[0] * 1.35)),
                min(255, int(base_col[1] * 1.35)),
                min(255, int(base_col[2] * 1.35))
            )

        pygame.draw.rect(surface, base_col, block_rect, border_radius=10)

        # 3. Glossy Reflection (Curved Sheen on Upper Half)
        sheen_surf = pygame.Surface((w - 4, int(h * 0.45)), pygame.SRCALPHA)
        pygame.draw.rect(sheen_surf, (255, 255, 255, 55), (0, 0, w - 4, int(h * 0.45)), border_radius=8)
        surface.blit(sheen_surf, (rx + 2, ry + 2))

        # 4. Neon Highlight Border
        pygame.draw.rect(surface, border_col, block_rect, width=2, border_radius=10)

        # 5. Label Rendering (HP or TNT)
        if self.is_bomb:
            # Draw TNT text with hazard look
            tnt_text = font.render("TNT", True, (255, 255, 255))
            t_rect = tnt_text.get_rect(center=block_rect.center)
            # Subtle glow behind TNT
            pygame.draw.circle(surface, (255, 100, 50), block_rect.center, 14)
            surface.blit(tnt_text, t_rect)
        else:
            hp_str = str(self.hp)
            # Outline shadow for crisp typography
            shadow_text = font.render(hp_str, True, (10, 14, 22))
            main_text = font.render(hp_str, True, (255, 255, 255))
            
            tr = main_text.get_rect(center=block_rect.center)
            # 4-direction shadow outline
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                surface.blit(shadow_text, (tr.x + dx, tr.y + dy))
            surface.blit(main_text, tr)
