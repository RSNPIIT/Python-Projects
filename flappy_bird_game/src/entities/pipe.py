"""
pipe.py - Pipe Obstacle Entity and PipeManager for KFlapper.
Generates top/bottom pipe pairs with lip caps, specular highlights, and fair hitboxes.
"""

import random
import pygame
from ..config import (
    PIPE_WIDTH, PIPE_CAP_HEIGHT, PIPE_CAP_OVERHANG, PIPE_MIN_HEIGHT,
    SCREEN_WIDTH, PLAYABLE_HEIGHT
)


class PipePair:
    """A pair of top and bottom pipes separated by a flight gap."""

    def __init__(self, x: float, gap_y: float, gap_height: float, width: int = PIPE_WIDTH):
        self.x = x
        self.gap_y = gap_y
        self.gap_height = gap_height
        self.width = width
        self.passed = False

    @property
    def top_pipe_bottom(self) -> float:
        return self.gap_y

    @property
    def bottom_pipe_top(self) -> float:
        return self.gap_y + self.gap_height

    def update(self, speed: float):
        self.x -= speed

    def collides_with_circle(self, cx: float, cy: float, radius: float) -> bool:
        """
        Tests if a circle (the bird) intersects either the top or bottom pipe.
        Uses a fair 3-pixel inset so minor graze brushes don't cause frustration.
        """
        inset = 3.0

        # Top Pipe Box: from y = 0 to y = self.top_pipe_bottom
        top_rect = pygame.Rect(
            self.x + inset,
            -10,
            self.width - inset * 2,
            self.top_pipe_bottom + 10 - inset
        )
        if self._circle_intersects_rect(cx, cy, radius, top_rect):
            return True

        # Bottom Pipe Box: from y = self.bottom_pipe_top to ground
        bottom_rect = pygame.Rect(
            self.x + inset,
            self.bottom_pipe_top + inset,
            self.width - inset * 2,
            PLAYABLE_HEIGHT - self.bottom_pipe_top + 10
        )
        if self._circle_intersects_rect(cx, cy, radius, bottom_rect):
            return True

        return False

    @staticmethod
    def _circle_intersects_rect(cx: float, cy: float, r: float, rect: pygame.Rect) -> bool:
        closest_x = max(rect.left, min(cx, rect.right))
        closest_y = max(rect.top, min(cy, rect.bottom))
        dx = cx - closest_x
        dy = cy - closest_y
        return (dx * dx + dy * dy) < (r * r)

    def draw(self, surface: pygame.Surface, theme: dict):
        """Renders authentic shaded arcade pipes with collar lip caps."""
        x = int(self.x)
        w = self.width
        cap_h = PIPE_CAP_HEIGHT
        overhang = PIPE_CAP_OVERHANG
        cap_w = w + overhang * 2
        cap_x = x - overhang

        body_col = theme["pipe_body"]
        hi_col = theme["pipe_highlight"]
        sh_col = theme["pipe_shadow"]
        dark_col = theme["pipe_dark"]

        top_h = int(self.top_pipe_bottom)
        bottom_y = int(self.bottom_pipe_top)
        bottom_h = int(PLAYABLE_HEIGHT - bottom_y)

        # ---------------------------------------------
        # 1. TOP PIPE (Hangs from ceiling downward)
        # ---------------------------------------------
        # Main pipe shaft
        if top_h - cap_h > 0:
            shaft_h = top_h - cap_h
            pygame.draw.rect(surface, body_col, (x, 0, w, shaft_h))
            # Left specular highlight stripe
            pygame.draw.rect(surface, hi_col, (x + 8, 0, 10, shaft_h))
            # Right shadow stripe
            pygame.draw.rect(surface, sh_col, (x + w - 18, 0, 14, shaft_h))
            # Shaft border
            pygame.draw.rect(surface, dark_col, (x, 0, w, shaft_h), 3)

        # Top Pipe Lip Cap (At bottom of top pipe)
        cap_y_top = top_h - cap_h
        pygame.draw.rect(surface, body_col, (cap_x, cap_y_top, cap_w, cap_h))
        pygame.draw.rect(surface, hi_col, (cap_x + 8 + overhang, cap_y_top, 10, cap_h))
        pygame.draw.rect(surface, sh_col, (cap_x + cap_w - 18 - overhang, cap_y_top, 14, cap_h))
        pygame.draw.rect(surface, dark_col, (cap_x, cap_y_top, cap_w, cap_h), 3)

        # ---------------------------------------------
        # 2. BOTTOM PIPE (Rises from ground upward)
        # ---------------------------------------------
        # Bottom Pipe Lip Cap (At top of bottom pipe)
        pygame.draw.rect(surface, body_col, (cap_x, bottom_y, cap_w, cap_h))
        pygame.draw.rect(surface, hi_col, (cap_x + 8 + overhang, bottom_y, 10, cap_h))
        pygame.draw.rect(surface, sh_col, (cap_x + cap_w - 18 - overhang, bottom_y, 14, cap_h))
        pygame.draw.rect(surface, dark_col, (cap_x, bottom_y, cap_w, cap_h), 3)

        # Bottom pipe shaft
        if bottom_h - cap_h > 0:
            shaft_y = bottom_y + cap_h
            shaft_h = bottom_h - cap_h
            pygame.draw.rect(surface, body_col, (x, shaft_y, w, shaft_h))
            # Left specular highlight stripe
            pygame.draw.rect(surface, hi_col, (x + 8, shaft_y, 10, shaft_h))
            # Right shadow stripe
            pygame.draw.rect(surface, sh_col, (x + w - 18, shaft_y, 14, shaft_h))
            # Shaft border
            pygame.draw.rect(surface, dark_col, (x, shaft_y, w, shaft_h), 3)


class PipeManager:
    """Handles spawning, scrolling, scoring checks, and culling of pipe obstacles."""

    def __init__(self, gap_size: float = 195.0, speed: float = 3.8):
        self.gap_size = gap_size
        self.speed = speed
        self.pipes = []
        self.spawn_distance = 360.0

    def reset(self, gap_size: float = 195.0, speed: float = 3.8):
        self.gap_size = gap_size
        self.speed = speed
        self.pipes.clear()

    def spawn_pipe(self, x: float):
        # Calculate random valid gap position
        min_y = PIPE_MIN_HEIGHT
        max_y = PLAYABLE_HEIGHT - PIPE_MIN_HEIGHT - self.gap_size
        gap_y = random.uniform(min_y, max_y)
        self.pipes.append(PipePair(x, gap_y, self.gap_size))

    def update(self) -> int:
        """
        Updates pipe positions.
        Returns: number of pipes cleared by the bird this frame (usually 0 or 1).
        """
        score_increment = 0

        # Move existing pipes
        for pipe in self.pipes:
            pipe.update(self.speed)

        # Cull off-screen pipes
        self.pipes = [p for p in self.pipes if p.x > -PIPE_WIDTH - PIPE_CAP_OVERHANG * 2]

        # Spawn next pipe if needed
        if not self.pipes:
            self.spawn_pipe(SCREEN_WIDTH + 80)
        else:
            last_pipe = self.pipes[-1]
            if last_pipe.x <= SCREEN_WIDTH - self.spawn_distance:
                self.spawn_pipe(SCREEN_WIDTH + 80)

        return score_increment

    def check_score(self, bird_x: float) -> bool:
        """Checks if bird passed a pipe's midpoint."""
        for pipe in self.pipes:
            if not pipe.passed and bird_x > (pipe.x + pipe.width / 2):
                pipe.passed = True
                return True
        return False

    def check_collision(self, bird) -> bool:
        """Checks if bird collided with any active pipe."""
        cx, cy, r = bird.get_hitbox_circle()
        for pipe in self.pipes:
            if pipe.collides_with_circle(cx, cy, r):
                return True
        return False

    def draw(self, surface: pygame.Surface, theme: dict):
        for pipe in self.pipes:
            pipe.draw(surface, theme)
