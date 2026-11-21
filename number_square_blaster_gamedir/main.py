"""Block Blast - Main Application Entry Point"""
import os
import sys
import signal
from pathlib import Path

# 1. Suppress pygame banner
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# 2. Lock terminal against Ctrl+C and Ctrl+Z
try:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
except Exception:
    pass

try:
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)
except Exception:
    pass

try:
    signal.signal(signal.SIGQUIT, signal.SIG_IGN)
except Exception:
    pass

import pygame

# Ensure package directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game import BlockBlastGame

def main():
    pygame.init()
    pygame.display.set_caption("Block Blast • Rocket Cannon Shooter")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    game = BlockBlastGame()
    running = True

    try:
        while running:
            dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
            mouse_pos = pygame.mouse.get_pos()

            # Handle Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if game.game_over:
                            game.start_new_game()
                        else:
                            game.is_firing = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        game.is_firing = False
                elif event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_q and (event.mod & (pygame.KMOD_CTRL | pygame.KMOD_META))) or \
                       (event.key == pygame.K_F4 and (event.mod & pygame.KMOD_ALT)):
                        running = False
                    elif event.key == pygame.K_r:
                        game.start_new_game()
                    elif event.key == pygame.K_SPACE:
                        if game.game_over:
                            game.start_new_game()
                        else:
                            game.is_firing = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        game.is_firing = False

            if not running:
                break

            # Update & Draw
            game.update(dt, mouse_pos)
            game.draw(screen, mouse_pos)

            # Flip Display
            pygame.display.flip()

    finally:
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    main()
