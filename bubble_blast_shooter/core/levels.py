"""Bubble Blast Shooter - Level Definitions & Endless Wave Generator"""
import random
from core.constants import EVEN_COLS, ODD_COLS
from core.bubble import Bubble
from core.grid import BubbleGrid

class LevelData:
    def __init__(self, name: str, ammo: int, layout_generator):
        self.name = name
        self.ammo = ammo
        self.layout_generator = layout_generator

    def load_into(self, grid: BubbleGrid):
        grid.clear()
        self.layout_generator(grid)


def _gen_level_1_diagonal(grid: BubbleGrid):
    """Diagonal color bands matching the user screenshot exactly!"""
    num_rows = 9
    for r in range(num_rows):
        cols = grid.get_cols_for_row(r)
        for c in range(cols):
            # Diagonal stripe formula: (c - r) % 6
            color_id = (c - r * 2) % 6
            grid.set_bubble(r, c, Bubble(color_id))


def _gen_level_2_rainbow(grid: BubbleGrid):
    """Horizontal layered rainbow bands."""
    num_rows = 8
    for r in range(num_rows):
        color_id = r % 6
        cols = grid.get_cols_for_row(r)
        for c in range(cols):
            grid.set_bubble(r, c, Bubble(color_id))


def _gen_level_3_checker(grid: BubbleGrid):
    """Two-column vertical colored pillars."""
    num_rows = 9
    for r in range(num_rows):
        cols = grid.get_cols_for_row(r)
        for c in range(cols):
            color_id = (c // 2 + (r % 2)) % 5
            grid.set_bubble(r, c, Bubble(color_id))


def _gen_level_4_clusters(grid: BubbleGrid):
    """Clusters and islands of matching colors."""
    num_rows = 9
    for r in range(num_rows):
        cols = grid.get_cols_for_row(r)
        for c in range(cols):
            color_id = ((r // 2) * 3 + (c // 3)) % 6
            grid.set_bubble(r, c, Bubble(color_id))


def _gen_level_5_diamond(grid: BubbleGrid):
    """Diamond geometric core with surrounding colored perimeter."""
    num_rows = 10
    center_c = 5
    for r in range(num_rows):
        cols = grid.get_cols_for_row(r)
        for c in range(cols):
            dist = abs(c - center_c) + abs(r - 4)
            color_id = dist % 6
            grid.set_bubble(r, c, Bubble(color_id))


CAMPAIGN_LEVELS = [
    LevelData("LEVEL 1: DIAGONAL SPECTRUM", ammo=45, layout_generator=_gen_level_1_diagonal),
    LevelData("LEVEL 2: RAINBOW ARCHES", ammo=42, layout_generator=_gen_level_2_rainbow),
    LevelData("LEVEL 3: COLOR PILLARS", ammo=40, layout_generator=_gen_level_3_checker),
    LevelData("LEVEL 4: ISLE CLUSTERS", ammo=40, layout_generator=_gen_level_4_clusters),
    LevelData("LEVEL 5: DIAMOND CORE", ammo=38, layout_generator=_gen_level_5_diamond),
]


def generate_endless_board(grid: BubbleGrid, wave: int):
    """Generates a randomized balanced board for Endless Survival mode."""
    grid.clear()
    num_rows = min(6 + wave // 2, 9)
    active_colors = list(range(min(4 + wave // 3, 6)))

    for r in range(num_rows):
        cols = grid.get_cols_for_row(r)
        c = 0
        while c < cols:
            cluster_len = random.randint(2, 4)
            color_id = random.choice(active_colors)
            for _ in range(cluster_len):
                if c < cols:
                    grid.set_bubble(r, c, Bubble(color_id))
                    c += 1
