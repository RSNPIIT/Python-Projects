"""Archer Bubble Blast - Vertical Harpoon Arrow"""
import pygame
from core.constants import ARENA_TOP, ARENA_FLOOR, ARROW_SPEED

class Arrow:
    def __init__(self, x: float, start_y: float = ARENA_FLOOR):
        self.x = x
        self.tip_y = start_y - 20
        self.base_y = start_y
        self.speed = ARROW_SPEED
        self.alive = True

    def update(self, dt: float) -> bool:
        self.tip_y -= self.speed * dt
        # When arrowhead hits ceiling, arrow is consumed
        if self.tip_y <= ARENA_TOP:
            self.alive = False
        return self.alive

    def collides_with_bubble(self, bx: float, by: float, radius: float) -> bool:
        """Check if bubble circle intersects the vertical arrow cable."""
        # 1. Horizontal check: is bubble center within radius of the x-line?
        if abs(bx - self.x) > radius:
            return False

        # 2. Vertical check: is bubble center between tip_y and base_y?
        if by + radius < self.tip_y or by - radius > self.base_y:
            return False

        return True

    def draw(self, surface: pygame.Surface):
        x = int(self.x)
        tip_y = int(self.tip_y)
        base_y = int(self.base_y)

        # 1. Glowing Harpoon Cable / Rope
        cable_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        # Soft outer glow
        pygame.draw.line(cable_surf, (255, 210, 80, 80), (x, tip_y), (x, base_y), 6)
        # Inner white/golden rope core
        pygame.draw.line(cable_surf, (255, 240, 150, 220), (x, tip_y), (x, base_y), 3)
        pygame.draw.line(cable_surf, (255, 255, 255, 255), (x, tip_y), (x, base_y), 1)
        surface.blit(cable_surf, (0, 0))

        # 2. Steel Arrowhead Tip
        arrow_w = 8
        arrow_h = 14
        pts = [
            (x, tip_y),
            (x - arrow_w, tip_y + arrow_h),
            (x, tip_y + arrow_h - 4),
            (x + arrow_w, tip_y + arrow_h)
        ]
        pygame.draw.polygon(surface, (235, 240, 250), pts)
        pygame.draw.polygon(surface, (120, 140, 180), pts, width=1)
