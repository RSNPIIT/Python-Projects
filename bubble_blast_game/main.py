"""Archer Bubble Blast - Main Application Entry Point"""
import os
import sys
import signal
from pathlib import Path

# 1. Suppress pygame banner
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# 2. Lock terminal against Ctrl+C and Ctrl+Z signals
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
from game import BubbleBlastGame

def main():
    pygame.init()
    pygame.display.set_caption("Bubble Blast - Archer Harpoon Arcade")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    game = BubbleBlastGame()
    running = True

    try:
        while running:
            dt = clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if game.show_quit_dialog:
                        running = False
                    else:
                        game.show_quit_dialog = True

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        game.handle_click(event.pos)
                        if game.should_exit:
                            running = False

                elif event.type == pygame.KEYDOWN:
                    # Cmd+Q / Ctrl+Q / Alt+F4 intercept
                    is_cmd_q = (event.key == pygame.K_q and (event.mod & (pygame.KMOD_CTRL | pygame.KMOD_META)))
                    is_alt_f4 = (event.key == pygame.K_F4 and (event.mod & pygame.KMOD_ALT))
                    if is_cmd_q or is_alt_f4:
                        game.show_quit_dialog = True
                    else:
                        game.handle_keydown(event.key)
                        if game.should_exit:
                            running = False

            if not running:
                break

            # Update simulation
            game.update(dt)

            # Render frame
            game.draw(screen)

            # Flip buffer
            pygame.display.flip()

    finally:
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    main()
