"""A small reactive autopilot used for attract mode, demos and screenshots."""

from __future__ import annotations

import pygame

from .player import Inputs


class AutoPilot:
    def __init__(self) -> None:
        self.jump_cd = 0.0
        self.jump_hold = 0.0
        self.dash_cd = 0.0

    def _jump(self, inp: Inputs) -> None:
        if self.jump_cd <= 0.0:
            inp.jump_pressed = True
            self.jump_hold = 0.2
            self.jump_cd = 0.5

    def think(self, player, world, dt: float) -> Inputs:
        self.jump_cd = max(0.0, self.jump_cd - dt)
        self.jump_hold = max(0.0, self.jump_hold - dt)
        inp = Inputs(right=True)
        inp.jump_held = self.jump_hold > 0

        if player.climbing:
            inp.up = True
            if player.vine is not None and player.y <= player.vine.top + 18:
                inp.jump_pressed = True
                inp.right = True
            return inp

        cx = player.x + player.w / 2
        feet = player.y + player.h
        gap = not world.has_ground_below(cx + 30, feet + 4, 160)
        hazard = bool(world.hazards_near(pygame.FRect(cx + 12, feet - 42, 98, 58)))
        wall = (world.point_solid(cx + player.w / 2 + 34, feet - 26)
                or world.point_solid(cx + player.w / 2 + 34, feet - 8)
                or world.point_solid(cx + player.w / 2 + 70, feet - 44))
        enemies = world.enemies_near(pygame.FRect(cx + 10, player.y - 20, 210,
                                                  player.h + 44))

        if player.on_ground and (gap or hazard or wall):
            self._jump(inp)
        elif player.on_ground and enemies and abs(enemies[0].x - cx) < 130:
            self._jump(inp)

        if (not player.on_ground) and player.vy > 260 and gap and player.dash_cooldown <= 0:
            inp.dash_pressed = True

        # keep the bot from standing still against geometry
        if player.on_ground and abs(player.vx) < 8:
            self._jump(inp)
        return inp
