"""Bubble Blast - Grid, Collision & Chain Reaction Coordinator"""
from typing import Optional
import pygame
from core.constants import (
    GRID_COLS, GRID_ROWS, CELL_SIZE,
    GRID_OFFSET_X, GRID_OFFSET_Y,
    STAGE_EMPTY, STAGE_RED, BUBBLE_COLORS
)
from core.bubble import Bubble
from core.projectile import Projectile
from systems.particles import ParticleSystem
from systems.sound import SoundManager

class BubbleGrid:
    def __init__(self, particles: ParticleSystem, sound: SoundManager):
        self.particles = particles
        self.sound = sound
        self.bubbles: list[list[Bubble]] = []
        self.projectiles: list[Projectile] = []
        self.combo_count = 0

        self._init_grid()

    def _init_grid(self):
        self.bubbles.clear()
        for r in range(GRID_ROWS):
            row_bubbles = []
            for c in range(GRID_COLS):
                cx = GRID_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2
                cy = GRID_OFFSET_Y + r * CELL_SIZE + CELL_SIZE // 2
                row_bubbles.append(Bubble(c, r, cx, cy, STAGE_EMPTY))
            self.bubbles.append(row_bubbles)

    def load_level_layout(self, layout: list[list[int]]):
        """Load an 8x6 matrix of bubble stages."""
        self.projectiles.clear()
        self.combo_count = 0
        for r in range(min(GRID_ROWS, len(layout))):
            for c in range(min(GRID_COLS, len(layout[r]))):
                self.bubbles[r][c].stage = layout[r][c]

    def get_bubble_at_pos(self, px: float, py: float) -> Optional[Bubble]:
        for row in self.bubbles:
            for b in row:
                if b.is_alive:
                    dist = ((px - b.x)**2 + (py - b.y)**2)**0.5
                    if dist <= b.base_radius + 4:
                        return b
        return None

    def pop_bubble(self, bubble: Bubble):
        """Pop a Red Bubble: emit 4 projectiles and particle burst."""
        color = bubble.color
        self.combo_count += 1
        bubble.stage = STAGE_EMPTY

        # Audio
        self.sound.play("pop")
        self.sound.play_combo_chain(self.combo_count)

        # Particles
        self.particles.emit_bubble_pop(bubble.x, bubble.y, color)

        # Spawn 4 Darts: Up, Down, Left, Right
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in directions:
            self.projectiles.append(Projectile(bubble.x, bubble.y, dx, dy, color))

    def tap_bubble(self, bubble: Bubble) -> bool:
        """User taps a bubble."""
        if not bubble.is_alive:
            return False

        self.combo_count = 0
        self.sound.play("tap")

        popped = bubble.hit()
        if popped:
            self.pop_bubble(bubble)
        else:
            self.sound.play("advance")

        return True

    def update(self, dt: float):
        # 1. Update Bubbles
        for row in self.bubbles:
            for b in row:
                b.update(dt)

        # 2. Update Projectiles & Check Collisions
        for proj in list(self.projectiles):
            if not proj.update(dt):
                self.projectiles.remove(proj)
                continue

            # Collision check with all living bubbles
            hit_target = None
            for row in self.bubbles:
                for b in row:
                    if b.is_alive:
                        dist = ((proj.x - b.x)**2 + (proj.y - b.y)**2)**0.5
                        if dist <= b.base_radius + proj.radius:
                            hit_target = b
                            break
                if hit_target:
                    break

            if hit_target:
                proj.alive = False
                if proj in self.projectiles:
                    self.projectiles.remove(proj)

                # Process bubble impact
                popped = hit_target.hit()
                if popped:
                    self.pop_bubble(hit_target)
                else:
                    self.sound.play("advance")

    def count_alive_bubbles(self) -> int:
        return sum(1 for row in self.bubbles for b in row if b.is_alive)

    def is_cleared(self) -> bool:
        return self.count_alive_bubbles() == 0

    def is_quiescent(self) -> bool:
        """True when all projectiles have finished flying (board is still)."""
        return len(self.projectiles) == 0

    def draw(self, surface: pygame.Surface):
        # 1. Draw Cell Background Plates
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                cx = GRID_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2
                cy = GRID_OFFSET_Y + r * CELL_SIZE + CELL_SIZE // 2
                # Subtle ring plate on board
                pygame.draw.circle(surface, (20, 25, 38), (cx, cy), 28)
                pygame.draw.circle(surface, (28, 34, 52), (cx, cy), 28, width=1)

        # 2. Draw Bubbles
        for row in self.bubbles:
            for b in row:
                b.draw(surface)

        # 3. Draw Projectiles
        for proj in self.projectiles:
            proj.draw(surface)
