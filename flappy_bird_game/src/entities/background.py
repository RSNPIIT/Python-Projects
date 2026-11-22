"""
background.py - Multi-Layer Parallax Background & Animated Ground for KFlapper.
Renders layered sky gradients, scrolling clouds, city silhouettes, hills, and authentic striped ground.
"""

import math
import random
import pygame
from ..config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_HEIGHT, PLAYABLE_HEIGHT
)


class Background:
    """Manages parallax atmospheric layers and endless scrolling ground."""

    def __init__(self):
        self.ground_offset = 0.0
        self.clouds_offset = 0.0
        self.city_offset = 0.0
        self.hills_offset = 0.0

        # Pre-generate cloud positions
        self.clouds = [
            {"x": random.uniform(0, SCREEN_WIDTH), "y": random.uniform(60, 220), "scale": random.uniform(0.7, 1.4)}
            for _ in range(8)
        ]

        # Pre-generate city skyline building profiles
        self.buildings = []
        cur_x = 0
        while cur_x < SCREEN_WIDTH + 300:
            bw = random.randint(45, 90)
            bh = random.randint(110, 260)
            self.buildings.append({"x": cur_x, "w": bw, "h": bh, "has_antenna": random.random() < 0.35})
            cur_x += bw

    def update(self, speed: float):
        """Scrolls each layer according to its parallax depth factor."""
        self.ground_offset = (self.ground_offset + speed) % 32.0
        self.hills_offset = (self.hills_offset + speed * 0.45) % (SCREEN_WIDTH * 2)
        self.city_offset = (self.city_offset + speed * 0.22) % (SCREEN_WIDTH * 2)
        self.clouds_offset = (self.clouds_offset + speed * 0.10) % (SCREEN_WIDTH * 2)

    def draw_sky(self, surface: pygame.Surface, theme: dict):
        """Draws a vertical 2-point gradient for the sky."""
        top_c = theme["sky_top"]
        bot_c = theme["sky_bottom"]
        h = PLAYABLE_HEIGHT

        # Draw gradient lines in steps of 4 for peak performance
        step = 4
        for y in range(0, h, step):
            factor = y / h
            r = int(top_c[0] + (bot_c[0] - top_c[0]) * factor)
            g = int(top_c[1] + (bot_c[1] - top_c[1]) * factor)
            b = int(top_c[2] + (bot_c[2] - top_c[2]) * factor)
            pygame.draw.rect(surface, (r, g, b), (0, y, SCREEN_WIDTH, step))

    def draw_clouds(self, surface: pygame.Surface, theme: dict):
        """Draws drifting fluffy cloud clusters."""
        cloud_col = theme["cloud_color"]
        shadow_col = theme["cloud_shadow"]

        for c in self.clouds:
            # Wrap around screen
            base_x = (c["x"] - self.clouds_offset) % (SCREEN_WIDTH + 200) - 100
            base_y = c["y"]
            sc = c["scale"]

            # Shadow base
            pygame.draw.ellipse(surface, shadow_col, (base_x - 40 * sc, base_y - 10 * sc, 120 * sc, 45 * sc))
            # Cloud puffs
            pygame.draw.circle(surface, cloud_col, (int(base_x), int(base_y)), int(26 * sc))
            pygame.draw.circle(surface, cloud_col, (int(base_x + 30 * sc), int(base_y - 8 * sc)), int(32 * sc))
            pygame.draw.circle(surface, cloud_col, (int(base_x + 60 * sc), int(base_y + 2 * sc)), int(22 * sc))
            pygame.draw.ellipse(surface, cloud_col, (base_x - 30 * sc, base_y - 2 * sc, 110 * sc, 34 * sc))

    def draw_city(self, surface: pygame.Surface, theme: dict):
        """Draws distant skyline buildings and radio towers."""
        city_col = theme["city_color"]
        ground_y = PLAYABLE_HEIGHT

        # Wrap building array across width
        offset = self.city_offset
        total_w = self.buildings[-1]["x"] + self.buildings[-1]["w"]

        for b in self.buildings:
            bx = (b["x"] - offset) % total_w - 60
            if -100 <= bx <= SCREEN_WIDTH + 60:
                by = ground_y - b["h"]
                pygame.draw.rect(surface, city_col, (int(bx), by, b["w"], b["h"]))
                # Antenna
                if b["has_antenna"]:
                    ax = int(bx + b["w"] / 2)
                    pygame.draw.line(surface, city_col, (ax, by), (ax, by - 28), 2)
                    pygame.draw.circle(surface, (255, 100, 100), (ax, by - 28), 3)

    def draw_hills(self, surface: pygame.Surface, theme: dict):
        """Draws rolling gentle green hills in front of the skyline."""
        hill_col = theme["hill_color"]
        bush_col = theme["bush_color"]
        ground_y = PLAYABLE_HEIGHT

        # Draw hill mounds
        hill_w = 400
        for i in range(-1, 5):
            hx = i * hill_w - (self.hills_offset % hill_w)
            # Big rolling arc
            pygame.draw.ellipse(surface, hill_col, (hx - 100, ground_y - 95, hill_w + 200, 160))

        # Near decorative bushes
        for i in range(-1, 9):
            bx = i * 180 - ((self.hills_offset * 1.4) % 180)
            pygame.draw.circle(surface, bush_col, (int(bx + 40), ground_y - 12), 34)
            pygame.draw.circle(surface, bush_col, (int(bx + 80), ground_y - 18), 44)
            pygame.draw.circle(surface, bush_col, (int(bx + 120), ground_y - 10), 30)

    def draw_ground(self, surface: pygame.Surface, theme: dict):
        """Draws the iconic classic scrolling ground with diagonal hash stripes."""
        y = PLAYABLE_HEIGHT
        h = GROUND_HEIGHT

        top_col = theme["ground_top"]
        body_col = theme["ground_body"]
        stripe_col = theme["ground_stripe"]

        # 1. Main Dirt Fill
        pygame.draw.rect(surface, body_col, (0, y, SCREEN_WIDTH, h))

        # 2. Diagonal Soil Hash Stripes
        stripe_w = 16
        gap = 32
        start_x = -int(self.ground_offset) - 40
        while start_x < SCREEN_WIDTH + 40:
            pts = [
                (start_x, y + 16),
                (start_x + stripe_w, y + 16),
                (start_x - 14 + stripe_w, y + h),
                (start_x - 14, y + h)
            ]
            pygame.draw.polygon(surface, stripe_col, pts)
            start_x += gap

        # 3. Top Grass Lawn Border
        grass_h = 16
        pygame.draw.rect(surface, top_col, (0, y, SCREEN_WIDTH, grass_h))

        # Dark border line between grass and dirt
        pygame.draw.line(surface, (40, 80, 20), (0, y + grass_h), (SCREEN_WIDTH, y + grass_h), 2)
        # Top boundary line
        pygame.draw.line(surface, (30, 60, 15), (0, y), (SCREEN_WIDTH, y), 3)

    def draw(self, surface: pygame.Surface, theme: dict):
        """Renders complete background and environment."""
        self.draw_sky(surface, theme)
        self.draw_clouds(surface, theme)
        self.draw_city(surface, theme)
        self.draw_hills(surface, theme)

    def draw_foreground(self, surface: pygame.Surface, theme: dict):
        """Renders ground on top of pipes."""
        self.draw_ground(surface, theme)
