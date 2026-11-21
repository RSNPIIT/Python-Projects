"""Archer Bubble Blast - Player Archer Character"""
import math
import pygame
from core.constants import (
    ARENA_LEFT, ARENA_RIGHT, ARENA_FLOOR,
    PLAYER_SPEED, PowerUpType
)

class Archer:
    def __init__(self, start_x: float = 480.0):
        self.x = start_x
        self.y = ARENA_FLOOR
        self.width = 34.0
        self.height = 52.0
        self.vx = 0.0
        self.speed = PLAYER_SPEED
        self.facing_right = True
        self.walk_time = 0.0

        # Health & State
        self.lives = 3
        self.invulnerable_timer = 0.0
        self.alive = True

        # Powerups
        self.double_arrow_timer = 0.0
        self.has_shield = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height),
            int(self.width),
            int(self.height)
        )

    @property
    def has_double_arrow(self) -> bool:
        return self.double_arrow_timer > 0

    def move_left(self):
        self.vx = -self.speed
        self.facing_right = False

    def move_right(self):
        self.vx = self.speed
        self.facing_right = True

    def stop_moving(self):
        self.vx = 0.0

    def take_hit(self) -> bool:
        """Takes a hit from a bubble. Returns True if damage taken, False if shielded/invulnerable."""
        if self.invulnerable_timer > 0:
            return False

        if self.has_shield:
            self.has_shield = False
            self.invulnerable_timer = 1.2
            return False

        self.lives -= 1
        self.invulnerable_timer = 2.0
        if self.lives <= 0:
            self.alive = False
        return True

    def activate_powerup(self, powerup_type: str):
        if powerup_type == PowerUpType.DOUBLE_ARROW:
            self.double_arrow_timer = 9.0
        elif powerup_type == PowerUpType.SHIELD:
            self.has_shield = True
        elif powerup_type == PowerUpType.EXTRA_LIFE:
            self.lives = min(5, self.lives + 1)

    def update(self, dt: float):
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        if self.double_arrow_timer > 0:
            self.double_arrow_timer -= dt

        # Update position
        self.x += self.vx * dt
        # Clamp to arena walls
        half_w = self.width / 2
        if self.x - half_w < ARENA_LEFT:
            self.x = ARENA_LEFT + half_w
        elif self.x + half_w > ARENA_RIGHT:
            self.x = ARENA_RIGHT - half_w

        if abs(self.vx) > 0:
            self.walk_time += dt * 14.0

    def draw(self, surface: pygame.Surface):
        # Blinking effect when invulnerable
        if self.invulnerable_timer > 0:
            if int(self.invulnerable_timer * 12) % 2 == 0:
                return

        cx = int(self.x)
        feet_y = int(self.y)
        head_y = feet_y - int(self.height)

        # 1. Protective Energy Shield
        if self.has_shield:
            shield_r = 34
            shield_surf = pygame.Surface((shield_r * 2 + 4, shield_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (80, 220, 255, 60), (shield_r + 2, shield_r + 2), shield_r)
            pygame.draw.circle(shield_surf, (140, 240, 255, 180), (shield_r + 2, shield_r + 2), shield_r, width=2)
            surface.blit(shield_surf, (cx - shield_r - 2, feet_y - int(self.height / 2) - shield_r - 2))

        # 2. Archer Legs / Trousers (walking animation)
        leg_offset = math.sin(self.walk_time) * 4 if abs(self.vx) > 0 else 0
        leg_col = (45, 55, 75)
        # Left leg
        pygame.draw.line(surface, leg_col, (cx - 5, feet_y - 18), (cx - 7 - leg_offset, feet_y), 4)
        # Right leg
        pygame.draw.line(surface, leg_col, (cx + 5, feet_y - 18), (cx + 7 + leg_offset, feet_y), 4)

        # 3. Tunic / Body
        tunic_rect = pygame.Rect(cx - 10, feet_y - 36, 20, 18)
        pygame.draw.rect(surface, (40, 120, 70), tunic_rect, border_radius=4)
        # Leather belt
        pygame.draw.rect(surface, (120, 75, 40), (cx - 10, feet_y - 23, 20, 4))
        pygame.draw.rect(surface, (230, 200, 80), (cx - 3, feet_y - 24, 6, 6))

        # 4. Quiver on Back with Arrows
        quiver_x = cx - 12 if self.facing_right else cx + 8
        pygame.draw.line(surface, (140, 85, 45), (quiver_x, feet_y - 38), (quiver_x, feet_y - 20), 4)
        # Arrow fletchings sticking out
        pygame.draw.line(surface, (255, 230, 100), (quiver_x, feet_y - 42), (quiver_x, feet_y - 38), 2)

        # 5. Head & Archer Hood
        head_cx = cx
        head_cy = head_y + 10
        # Face
        pygame.draw.circle(surface, (255, 215, 175), (head_cx, head_cy), 8)
        # Hood / Cap
        pygame.draw.circle(surface, (35, 105, 60), (head_cx, head_cy - 2), 9)
        # Archer feather
        feather_x = head_cx - 6 if self.facing_right else head_cx + 6
        pygame.draw.line(surface, (240, 60, 60), (feather_x, head_cy - 8), (feather_x - 4, head_cy - 14), 2)

        # 6. Bow Aimed Straight Upwards
        bow_x = cx + 8 if self.facing_right else cx - 8
        bow_y = head_cy - 4
        # Curved wooden bow arc pointing UP
        bow_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.arc(bow_surf, (160, 95, 45), (4, 4, 24, 24), math.pi * 0.15, math.pi * 0.85, 3)
        # Bowstring
        pygame.draw.line(bow_surf, (240, 240, 240), (5, 16), (27, 16), 1)
        surface.blit(bow_surf, (bow_x - 16, bow_y - 20))
