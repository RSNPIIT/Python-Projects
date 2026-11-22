"""Kapman Game - Player Character Model & Chomp Animation"""
import math
from core.constants import (
    KAPMAN_NORMAL_SPEED, KAPMAN_FRIGHT_SPEED,
    DIR_NONE, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
)
from core.character import Character
from core.maze import Maze

class Kapman(Character):
    def __init__(self, start_col: float = 13.5, start_row: float = 23.0):
        super().__init__(start_col, start_row, KAPMAN_NORMAL_SPEED)
        self.lives = 3
        self.mouth_angle = 35.0
        self.mouth_opening = True
        self.anim_time = 0.0
        self.alive = True
        self.dying = False
        self.death_progress = 0.0  # 0.0 to 1.0

    def reset(self):
        self.reset_position()
        self.alive = True
        self.dying = False
        self.death_progress = 0.0
        self.speed = KAPMAN_NORMAL_SPEED

    def update(self, dt: float, maze: Maze, is_energized: bool = False):
        if self.dying:
            self.death_progress += dt * 0.9
            if self.death_progress >= 1.0:
                self.dying = False
                self.alive = False
            return

        # Boost speed slightly when energized (tables turned!)
        self.speed = KAPMAN_FRIGHT_SPEED if is_energized else KAPMAN_NORMAL_SPEED
        self.update_movement(dt, maze, allow_gate=False)

        # Chomp mouth animation
        if self.direction != DIR_NONE:
            self.anim_time += dt * 14.0
            # Sine wave oscillation between 5 and 50 degrees
            self.mouth_angle = 5.0 + 45.0 * (0.5 + 0.5 * math.sin(self.anim_time))
        else:
            self.mouth_angle = 30.0

    @property
    def rotation_angle(self) -> float:
        """Returns visual rotation angle in degrees based on current direction."""
        if self.direction == DIR_RIGHT:
            return 0.0
        elif self.direction == DIR_DOWN:
            return 90.0
        elif self.direction == DIR_LEFT:
            return 180.0
        elif self.direction == DIR_UP:
            return 270.0
        return 0.0
