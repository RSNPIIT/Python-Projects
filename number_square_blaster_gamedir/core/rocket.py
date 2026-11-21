"""Block Blast - Rocket Projectiles"""
import math
import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Rocket:
    def __init__(
        self,
        x: float,
        y: float,
        angle_rad: float,
        speed: float = 750.0,
        damage: int = 1,
        is_piercing: bool = False
    ):
        self.x = x
        self.y = y
        self.angle = angle_rad
        self.speed = speed
        self.vx = math.cos(angle_rad) * speed
        self.vy = math.sin(angle_rad) * speed
        self.damage = damage
        self.is_piercing = is_piercing
        self.radius = 6.0
        self.alive = True
        self.bounce_count = 0
        self.max_bounces = 3
        self.trail_timer = 0.0

    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Bounce off left and right screen borders
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = -self.vx
            self.bounce_count += 1
        elif self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vx = -self.vx
            self.bounce_count += 1

        # Destroy if goes off top or bottom or too many bounces
        if self.y < -20 or self.y > SCREEN_HEIGHT + 20 or self.bounce_count > self.max_bounces:
            self.alive = False

        return self.alive

    def draw(self, surface: pygame.Surface, offset: tuple[float, float]):
        draw_x = self.x + offset[0]
        draw_y = self.y + offset[1]
        cur_angle = math.atan2(self.vy, self.vx)

        # Draw Rocket body
        length = 16.0 if not self.is_piercing else 22.0
        width = 6.0

        # Tip, left fin, right fin
        tip = (draw_x + math.cos(cur_angle) * length, draw_y + math.sin(cur_angle) * length)
        base_left = (
            draw_x + math.cos(cur_angle + math.pi * 0.8) * width,
            draw_y + math.sin(cur_angle + math.pi * 0.8) * width
        )
        base_right = (
            draw_x + math.cos(cur_angle - math.pi * 0.8) * width,
            draw_y + math.sin(cur_angle - math.pi * 0.8) * width
        )

        body_color = (255, 220, 60) if not self.is_piercing else (50, 240, 255)
        flame_color = (255, 80, 40)

        # Flame exhaust
        flame_tip = (draw_x - math.cos(cur_angle) * 7.0, draw_y - math.sin(cur_angle) * 7.0)
        pygame.draw.polygon(surface, flame_color, [base_left, flame_tip, base_right])
        pygame.draw.polygon(surface, body_color, [tip, base_left, base_right])
        pygame.draw.polygon(surface, (255, 255, 255), [tip, base_left, base_right], width=1)
