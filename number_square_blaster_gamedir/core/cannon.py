"""Block Blast - Player Cannon / Turret Launcher"""
import math
import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PowerUpType
from core.rocket import Rocket

class Cannon:
    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT - 75
        self.angle = -math.pi / 2  # Pointing straight up (-90 deg)
        self.target_angle = self.angle
        
        # Fire cooldown
        self.base_cooldown = 0.14  # Fire every 140ms
        self.cooldown_timer = 0.0

        # PowerUp active durations
        self.powerup_timers: dict[str, float] = {
            PowerUpType.SPREAD_SHOT: 0.0,
            PowerUpType.PIERCE: 0.0,
            PowerUpType.RAPID_FIRE: 0.0,
        }

    @property
    def has_spread(self) -> bool:
        return self.powerup_timers[PowerUpType.SPREAD_SHOT] > 0

    @property
    def has_pierce(self) -> bool:
        return self.powerup_timers[PowerUpType.PIERCE] > 0

    @property
    def current_cooldown(self) -> float:
        if self.powerup_timers[PowerUpType.RAPID_FIRE] > 0:
            return self.base_cooldown * 0.5
        return self.base_cooldown

    def activate_powerup(self, powerup_type: str, duration: float = 7.0):
        if powerup_type in self.powerup_timers:
            self.powerup_timers[powerup_type] = duration

    def aim_at(self, target_x: float, target_y: float):
        dx = target_x - self.x
        dy = target_y - self.y
        # Only aim upwards into the playfield
        angle = math.atan2(dy, dx)
        # Clamp angle between -165 deg and -15 deg
        min_angle = -math.pi * 0.92
        max_angle = -math.pi * 0.08
        self.angle = max(min_angle, min(max_angle, angle))

    def update(self, dt: float):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

        for k in self.powerup_timers:
            if self.powerup_timers[k] > 0:
                self.powerup_timers[k] -= dt

    def shoot(self) -> list[Rocket]:
        if self.cooldown_timer > 0:
            return []

        self.cooldown_timer = self.current_cooldown
        rockets = []

        is_pierce = self.has_pierce
        damage = 2 if is_pierce else 1

        barrel_len = 34.0
        bx = self.x + math.cos(self.angle) * barrel_len
        by = self.y + math.sin(self.angle) * barrel_len

        if self.has_spread:
            # 3 rockets in spread fan
            for spread_offset in [-0.22, 0.0, 0.22]:
                rockets.append(Rocket(bx, by, self.angle + spread_offset, damage=damage, is_piercing=is_pierce))
        else:
            rockets.append(Rocket(bx, by, self.angle, damage=damage, is_piercing=is_pierce))

        return rockets

    def draw(self, surface: pygame.Surface, offset: tuple[float, float], mouse_pos: tuple[int, int]):
        cx = self.x + offset[0]
        cy = self.y + offset[1]

        # 1. Aim Trajectory Laser Guide
        laser_len = 500.0
        lx = cx + math.cos(self.angle) * laser_len
        ly = cy + math.sin(self.angle) * laser_len

        # Dashed laser sight
        steps = 22
        for i in range(1, steps):
            if i % 2 == 0:
                continue
            t1 = (i - 0.5) / steps
            t2 = i / steps
            p1 = (cx + math.cos(self.angle) * (laser_len * t1), cy + math.sin(self.angle) * (laser_len * t1))
            p2 = (cx + math.cos(self.angle) * (laser_len * t2), cy + math.sin(self.angle) * (laser_len * t2))
            laser_col = (255, 60, 100, 140) if not self.has_pierce else (50, 240, 255, 180)
            pygame.draw.line(surface, laser_col[:3], p1, p2, 2)

        # 2. Cannon Barrel
        barrel_len = 32.0
        barrel_w = 8.0 if not self.has_spread else 14.0
        bx = cx + math.cos(self.angle) * barrel_len
        by = cy + math.sin(self.angle) * barrel_len

        barrel_col = (230, 235, 245) if not self.has_pierce else (50, 240, 255)
        pygame.draw.line(surface, (10, 15, 22), (cx, cy), (bx, by), int(barrel_w + 4))
        pygame.draw.line(surface, barrel_col, (cx, cy), (bx, by), int(barrel_w))

        # 3. Cannon Chassis / Base
        pygame.draw.circle(surface, (15, 20, 30), (cx, cy), 28)
        pygame.draw.circle(surface, (50, 60, 85), (cx, cy), 24)
        pygame.draw.circle(surface, (80, 100, 140), (cx, cy), 18)
        pygame.draw.circle(surface, (255, 180, 50), (cx, cy), 8)
