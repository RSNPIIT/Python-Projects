#!/usr/bin/env python3
"""Generate the screenshots and preview GIF used in the README.

Run from anywhere:
    .venv/bin/python tools/capture.py

The tool uses SDL's dummy drivers, so it never opens a window.  It leaves the
save file reset afterwards and writes into ``screenshots/``.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
from PIL import Image  # noqa: E402

from game.game import Game, DEFAULT_SAVE  # noqa: E402
from game.player import Inputs  # noqa: E402

SHOTS = ROOT / "screenshots"
SAVE = ROOT / "save.json"


def reset_save() -> None:
    SAVE.write_text(json.dumps(DEFAULT_SAVE, indent=2))


def snap(game: Game, name: str) -> None:
    game.draw()
    pygame.image.save(game.screen, str(SHOTS / name))
    print(f"  wrote {name}")


def find_vine(game: Game):
    game.world.ensure_until(9000)
    for chunk in game.world.chunks.values():
        if chunk.vines:
            return chunk.vines[0]
    return None


def main() -> int:
    SHOTS.mkdir(parents=True, exist_ok=True)
    reset_save()
    pygame.init()

    game = Game(seed=None, mute=True, headless=True)
    game.audio.set_muted(True)

    print("capturing title ...")
    game.state = "title"
    for _ in range(30):
        game.step(1 / 60)
    snap(game, "title.png")

    print("capturing mode select ...")
    game.state = "mode_select"
    game.mode_select_index = 1
    for _ in range(20):
        game.step(1 / 60)
    snap(game, "mode_select.png")

    print("capturing difficulty select ...")
    game.state = "difficulty_select"
    game.pending_mode = "loop"
    game.diff_select_index = 1
    for _ in range(20):
        game.step(1 / 60)
    snap(game, "difficulty_select.png")

    print("capturing customize ...")
    game.state = "customize"
    game.custom_index = 0
    for _ in range(30):
        game.step(1 / 60)
    snap(game, "customize.png")

    print("capturing level select ...")
    game.state = "level_select"
    game.save["unlocked_level"] = 12
    game.save["level_records"] = {
        "1": {"stars": 3, "time": 18.4, "coins": 15, "gems": 2},
        "2": {"stars": 2, "time": 24.1, "coins": 10, "gems": 1},
        "3": {"stars": 3, "time": 21.0, "coins": 12, "gems": 3},
    }
    game.selected_level = 5
    snap(game, "level_select.png")

    print("capturing level gameplay ...")
    game.god = True
    game.autopilot = True
    game.start_level(1)
    for _ in range(60 * 5):
        game.step(1 / 60)
    game.god = False
    game.autopilot = False
    snap(game, "levels_gameplay.png")

    print("capturing level complete ...")
    game.coins = 28
    game.gems = 3
    game.elapsed = 34.2
    game._complete_level()
    snap(game, "level_complete.png")

    print("capturing climb ...")
    game.start_run("loop", seed=1234)
    vine = find_vine(game)
    if vine is not None:
        game.player.x = vine.x - 14
        game.player.y = vine.bottom - 46
        game.player.on_ground = True
        game._snap_camera()
        game._poll_inputs = lambda: Inputs(up=True)
        for _ in range(72):
            game.step(1 / 60)
        snap(game, "gameplay_climb.png")

    print("capturing loop gameplay ...")
    game.god = True
    game.autopilot = True
    game.start_run("loop", seed=99)
    for _ in range(60 * 43):
        game.step(1 / 60)
    # settle on the ground for a cleaner composition
    for _ in range(180):
        game.step(1 / 60)
        if game.player.on_ground and abs(game.player.vy) < 10:
            break
    snap(game, "gameplay_loop.png")

    print("capturing trial + pause ...")
    game.start_run("trial", seed=7)
    for _ in range(60 * 26):
        game.step(1 / 60)
    snap(game, "gameplay_trial.png")
    game.state = "paused"
    game.menu_index = 0
    snap(game, "pause.png")

    print("capturing game over ...")
    game.menu_index = 0
    game.god = True
    game.autopilot = True
    game.start_run("loop", seed=42)
    for _ in range(60 * 26):
        game.step(1 / 60)
    game.god = False
    game.autopilot = False
    game.player.armor = 0
    game.player.invuln = 0
    game.player.hearts = 1
    game._hurt_player(game.player.x - 90)
    for _ in range(120):
        game.step(1 / 60)
    print(f"  final score {game.final_score}, state {game.state}")
    snap(game, "gameover.png")

    print("capturing preview.gif ...")
    game.god = True
    game.autopilot = True
    game.start_run("loop", seed=2026)
    for _ in range(60 * 3):
        game.step(1 / 60)

    frames: list[Image.Image] = []
    fps = 12
    seconds = 4.0
    step = 60 // fps
    for _ in range(int(seconds * fps)):
        for _ in range(step):
            game.step(1 / 60)
        game.draw()
        rgb = pygame.surfarray.array3d(game.screen)
        img = Image.fromarray(rgb.swapaxes(0, 1))
        frames.append(img.resize((480, 270), Image.LANCZOS))
    frames[0].save(
        SHOTS / "preview.gif",
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),
        loop=0,
        optimize=True,
    )
    print(f"  wrote preview.gif ({len(frames)} frames, "
          f"{(SHOTS / 'preview.gif').stat().st_size / 1e6:.1f} MB)")

    reset_save()
    print("done. save file reset.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
