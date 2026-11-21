"""Block Blast - Polished Sci-Fi Cannon & Aiming System"""
import math
import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PowerUpType
from core.rocket import Rocket

class Cannon:
    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT - 70
        self.angle = -math.pi / 2
        self.base_cooldown = 0.13
        self.cooldown_timer = 0.0
        self.recoil = 0.0
        self.muzzle_flash_timer = 0.0

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
            return self.base_cooldown * 0.55
        return self.base_cooldown

    def activate_powerup(self, powerup_type: str, duration: float = 7.0):
        if powerup_type in self.powerup_timers:
            self.powerup_timers[powerup_type] = duration

    def aim_at(self, target_x: float, target_y: float):
        dx = target_x - self.x
        dy = target_y - self.y
        angle = math.atan2(dy, dx)
        min_angle = -math.pi * 0.93
        max_angle = -math.pi * 0.07
        self.angle = max(min_angle, min(max_angle, angle))

    def update(self, dt: float):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

        if self.recoil > 0:
            self.recoil = max(0.0, self.recoil - dt * 25.0)

        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer -= dt

        for k in self.powerup_timers:
            if self.powerup_timers[k] > 0:
                self.powerup_timers[k] -= dt

    def shoot(self) -> list[Rocket]:
        if self.cooldown_timer > 0:
            return []

        self.cooldown_timer = self.current_cooldown
        self.recoil = 6.0
        self.muzzle_flash_timer = 0.06
        rockets = []

        is_pierce = self.has_pierce
        damage = 2 if is_pierce else 1

        barrel_len = 38.0
        bx = self.x + math.cos(self.angle) * barrel_len
        by = self.y + math.sin(self.angle) * barrel_len

        if self.has_spread:
            for spread_offset in [-0.20, 0.0, 0.20]:
                rockets.append(Rocket(bx, by, self.angle + spread_offset, damage=damage, is_piercing=is_pierce))
        else:
            rockets.append(Rocket(bx, by, self.angle, damage=damage, is_piercing=is_pierce))

        return rockets

    def draw(self, surface: pygame.Surface, offset: tuple[float, float], mouse_pos: tuple[int, int]):
        cx = self.x + offset[0]
        cy = self.y + offset[1]

        # 1. Futuristic Aiming Reticle & Laser Trajectory
        laser_len = 650.0
        laser_color = (255, 60, 90) if not self.has_pierce else (50, 240, 255)

        # Draw glowing laser sight with alpha surface
        laser_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        steps = 28
        for i in range(2, steps):
            if i % 2 == 0:
                continue
            t1 = (i - 0.6) / steps
            t2 = i / steps
            p1 = (cx + math.cos(self.angle) * (laser_len * t1), cy + math.sin(self.angle) * (laser_len * t1))
            p2 = (cx + math.cos(self.angle) * (laser_len * t2), cy + math.sin(self.angle) * (laser_len * t2))
            pygame.draw.line(laser_surf, (*laser_color, 160), p1, p2, 2)
            pygame.draw.circle(laser_surf, (*laser_color, 120), (int(p2[0]), int(p2[1])), 2)

        surface.blit(laser_surf, (0, 0))

        # Target Crosshair at Mouse
        mx, my = mouse_pos
        ch_r = 14
        ch_surf = pygame.Surface((ch_r * 2 + 4, ch_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ch_surf, (*laser_color, 200), (ch_r + 2, ch_r + 2), ch_r, width=1)
        pygame.draw.line(ch_surf, (*laser_color, 240), (ch_r + 2, 0), (ch_r + 2, ch_r * 2 + 4), 1)
        pygame.draw.line(ch_surf, (*laser_color, 240), (0, ch_r + 2), (ch_r * 2 + 4, ch_r + 2), 1)
        surface.blit(ch_surf, (mx - ch_r - 2, my - ch_r - 2))

        # 2. Cannon Pedestal / Armored Base
        base_r = 30
        pygame.draw.circle(surface, (12, 15, 24), (cx, cy + 4), base_r + 2)
        pygame.draw.circle(surface, (30, 36, 52), (cx, cy), base_r)
        pygame.draw.circle(surface, (45, 56, 80), (cx, cy), base_r - 4)
        pygame.draw.circle(surface, (20, 24, 36), (cx, cy), base_r - 8)

        # 3. Rotating Turret Barrel with Recoil
        recoil_dist = self.recoil
        barrel_len = 36.0 - recoil_dist
        barrel_w = 12.0 if not self.has_spread else 18.0

        # Barrel endpoints
        bx = cx + math.cos(self.angle) * barrel_len
        by = cy + math.sin(self.angle) * barrel_len

        # Metallic barrel housing
        barrel_col = (200, 215, 235) if not self.has_pierce else (70, 235, 255)
        dark_barrel = (20, 26, 40)
        
        # Shadow / outline
        pygame.draw.line(surface, dark_barrel, (cx, cy), (bx, by), int(barrel_w + 6))
        # Inner metallic barrel
        pygame.draw.line(surface, barrel_col, (cx, cy), (bx, by), int(barrel_w))
        # Muzzle brake ring
        pygame.draw.circle(surface, (255, 255, 255), (int(bx), int(by)), int(barrel_w / 2 + 1), width=2)

        # 4. Muzzle Flash when firing
        if self.muzzle_flash_timer > 0:
            flash_r = 16
            flash_surf = pygame.Surface((flash_r * 2, flash_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 230, 100, 230), (flash_r, flash_r), flash_r)
            pygame.draw.circle(flash_surf, (255, 255, 255, 255), (flash_r, flash_r), flash_r // 2)
            surface.blit(flash_surf, (bx - flash_r, by - flash_r))

        # 5. Glowing Energy Core in the Center of Turret
        core_col = (255, 175, 40) if not self.has_pierce else (50, 240, 255)
        pygame.draw.circle(surface, core_col, (int(cx), int(cy)), 9)
        pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(cy)), 4)
