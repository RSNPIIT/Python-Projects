"""
particles.py - Particle VFX for Hard Drops, Line Clears, Combos & Background Ambience.
"""

import math
import random
import pygame


class SparkParticle:
    def __init__(self, x, y, color, vx=None, vy=None, lifetime=0.45, size=3.5):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(80, 260) if vx is None else 0
        self.vx = math.cos(angle) * speed if vx is None else vx
        self.vy = math.sin(angle) * speed if vy is None else vy
        self.gravity = 340.0
        self.lifetime = lifetime
        self.max_life = lifetime
        self.size = size

    def update(self, dt):
        self.lifetime -= dt
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        return self.lifetime > 0

    def draw(self, surface):
        if self.lifetime <= 0:
            return
        progress = self.lifetime / self.max_life
        alpha = int(255 * progress)
        cur_size = max(1.0, self.size * progress)
        r, g, b = self.color[:3]
        col = (r, g, b, alpha)
        # Draw glowing spark point
        spark_surf = pygame.Surface((int(cur_size * 2), int(cur_size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(spark_surf, col, (int(cur_size), int(cur_size)), int(cur_size))
        surface.blit(spark_surf, (self.x - cur_size, self.y - cur_size), special_flags=pygame.BLEND_ADD)


class FloatingText:
    def __init__(self, x, y, text, color=(255, 235, 60), font_size=24, lifetime=1.2, vy=-45.0):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont('Arial', font_size, bold=True)
        self.lifetime = lifetime
        self.max_life = lifetime
        self.vy = vy

    def update(self, dt):
        self.lifetime -= dt
        self.y += self.vy * dt
        return self.lifetime > 0

    def draw(self, surface):
        if self.lifetime <= 0:
            return
        progress = self.lifetime / self.max_life
        alpha = int(255 * min(1.0, progress * 1.5))

        # Render with glowing border shadow
        shadow_surf = self.font.render(self.text, True, (0, 0, 0))
        shadow_surf.set_alpha(int(alpha * 0.75))
        surface.blit(shadow_surf, (self.x - shadow_surf.get_width() // 2 + 2, self.y + 2))

        text_surf = self.font.render(self.text, True, self.color[:3])
        text_surf.set_alpha(alpha)
        surface.blit(text_surf, (self.x - text_surf.get_width() // 2, self.y))


class LineClearLaser:
    def __init__(self, x, y, width, height, color=(255, 255, 255), lifetime=0.22):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.lifetime = lifetime
        self.max_life = lifetime

    def update(self, dt):
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, surface):
        if self.lifetime <= 0:
            return
        progress = self.lifetime / self.max_life
        alpha = int(255 * progress)
        laser_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        laser_surf.fill((*self.color[:3], alpha))
        surface.blit(laser_surf, (self.x, self.y), special_flags=pygame.BLEND_ADD)


class ParticleManager:
    def __init__(self):
        self.particles = []
        self.floating_texts = []
        self.lasers = []

    def spawn_hard_drop_impact(self, block_coords, color, cell_size):
        for bx, by in block_coords:
            # Bottom edges of landing blocks emit sparks
            px = bx + cell_size * 0.5
            py = by + cell_size
            for _ in range(5):
                vx = random.uniform(-80, 80)
                vy = random.uniform(-140, -40)
                self.particles.append(SparkParticle(px, py, color, vx=vx, vy=vy, lifetime=0.35, size=3.0))

    def spawn_line_clear_explosion(self, row_y, grid_x, grid_width, cell_size, color=(0, 240, 255)):
        self.lasers.append(LineClearLaser(grid_x, row_y, grid_width, cell_size, color=color, lifetime=0.20))
        for col_idx in range(int(grid_width / cell_size)):
            px = grid_x + col_idx * cell_size + cell_size * 0.5
            py = row_y + cell_size * 0.5
            for _ in range(3):
                vx = random.uniform(-120, 120)
                vy = random.uniform(-160, 40)
                self.particles.append(SparkParticle(px, py, color, vx=vx, vy=vy, lifetime=0.5, size=4.0))

    def add_floating_text(self, x, y, text, color=(255, 225, 50), font_size=26):
        self.floating_texts.append(FloatingText(x, y, text, color=color, font_size=font_size))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floating_texts = [t for t in self.floating_texts if t.update(dt)]
        self.lasers = [l for l in self.lasers if l.update(dt)]

    def draw(self, surface):
        for l in self.lasers:
            l.draw(surface)
        for p in self.particles:
            p.draw(surface)
        for t in self.floating_texts:
            t.draw(surface)

    def clear(self):
        self.particles.clear()
        self.floating_texts.clear()
        self.lasers.clear()
