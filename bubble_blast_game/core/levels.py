"""Archer Bubble Blast - Level Configurations & Endless Generator"""
import random
from core.constants import (
    ARENA_LEFT, ARENA_RIGHT,
    SIZE_HUGE, SIZE_LARGE, SIZE_MEDIUM, SIZE_SMALL
)
from core.bouncing_bubble import BouncingBubble

class LevelConfig:
    def __init__(self, name: str, bubbles: list[dict]):
        self.name = name
        self.bubble_defs = bubbles

    def spawn(self) -> list[BouncingBubble]:
        result = []
        for b in self.bubble_defs:
            result.append(
                BouncingBubble(
                    x=float(b["x"]),
                    y=float(b["y"]),
                    size=int(b["size"]),
                    vx=float(b.get("vx", 160.0)),
                    vy=float(b.get("vy", 0.0))
                )
            )
        return result

CAMPAIGN_LEVELS = [
    # Level 1: Gentle Introduction
    LevelConfig("LEVEL 1: TARGET PRACTICE", [
        {"x": 480, "y": 180, "size": SIZE_MEDIUM, "vx": 170.0}
    ]),

    # Level 2: Crossing Paths
    LevelConfig("LEVEL 2: CROSSFIRE", [
        {"x": 260, "y": 180, "size": SIZE_MEDIUM, "vx": 180.0},
        {"x": 700, "y": 180, "size": SIZE_MEDIUM, "vx": -180.0}
    ]),

    # Level 3: The Big One
    LevelConfig("LEVEL 3: COLOSSAL SPHERE", [
        {"x": 480, "y": 160, "size": SIZE_LARGE, "vx": 160.0}
    ]),

    # Level 4: Double Large
    LevelConfig("LEVEL 4: TWIN GIANTS", [
        {"x": 240, "y": 160, "size": SIZE_LARGE, "vx": 160.0},
        {"x": 720, "y": 160, "size": SIZE_LARGE, "vx": -160.0}
    ]),

    # Level 5: The Red Behemoth
    LevelConfig("LEVEL 5: THE TITAN", [
        {"x": 480, "y": 140, "size": SIZE_HUGE, "vx": 150.0}
    ]),

    # Level 6: Trio Challenge
    LevelConfig("LEVEL 6: TRIPLE THREAT", [
        {"x": 220, "y": 150, "size": SIZE_LARGE, "vx": 160.0},
        {"x": 480, "y": 200, "size": SIZE_MEDIUM, "vx": -180.0},
        {"x": 740, "y": 150, "size": SIZE_LARGE, "vx": -160.0}
    ]),

    # Level 7: Dual Titans
    LevelConfig("LEVEL 7: DUAL TITANS", [
        {"x": 280, "y": 130, "size": SIZE_HUGE, "vx": 140.0},
        {"x": 680, "y": 130, "size": SIZE_HUGE, "vx": -140.0}
    ]),

    # Level 8: Master Archer
    LevelConfig("LEVEL 8: ARMAGEDDON", [
        {"x": 200, "y": 130, "size": SIZE_HUGE, "vx": 140.0},
        {"x": 480, "y": 160, "size": SIZE_LARGE, "vx": 170.0},
        {"x": 760, "y": 130, "size": SIZE_HUGE, "vx": -140.0}
    ])
]

def generate_endless_wave(wave: int) -> list[BouncingBubble]:
    """Generates an escalating wave of bouncing bubbles for Endless Arcade mode."""
    bubbles = []
    num_spawns = min(1 + wave // 2, 5)

    for i in range(num_spawns):
        # Determine size by wave difficulty
        roll = random.random()
        if wave == 1:
            size = SIZE_MEDIUM
        elif wave == 2:
            size = SIZE_LARGE if roll < 0.4 else SIZE_MEDIUM
        elif wave < 5:
            if roll < 0.35:
                size = SIZE_HUGE
            elif roll < 0.7:
                size = SIZE_LARGE
            else:
                size = SIZE_MEDIUM
        else:
            # High waves
            if roll < 0.5:
                size = SIZE_HUGE
            elif roll < 0.85:
                size = SIZE_LARGE
            else:
                size = SIZE_MEDIUM

        # Evenly distribute starting horizontal positions
        slice_w = (ARENA_RIGHT - ARENA_LEFT - 120) / max(num_spawns, 1)
        bx = ARENA_LEFT + 60 + i * slice_w + random.uniform(-20, 20)
        by = random.uniform(130, 210)
        direction = 1 if (i % 2 == 0) else -1
        speed = 140.0 + min(wave * 5.0, 90.0)

        bubbles.append(BouncingBubble(bx, by, size=size, vx=direction * speed, vy=-50.0))

    return bubbles
