"""Bubble Blast - Main Application Entry Point"""
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
from game import BubbleBlastGame

def main():
    pygame.init()
    pygame.display.set_caption("Bubble Blast • Classic Chain Reaction Puzzle")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    game = BubbleBlastGame()
    running = True

    try:
        while running:
            dt = clock.tick(FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if game.show_quit_dialog:
                        running = False
                    else:
                        game.request_quit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if game.show_quit_dialog:
                            action = game.handle_quit_click(event.pos)
                            if action == "quit":
                                running = False
                        else:
                            game.handle_mouse_down(event.pos, event.button)

                elif event.type == pygame.KEYDOWN:
                    if game.show_quit_dialog:
                        if event.key in (pygame.K_y, pygame.K_RETURN):
                            running = False
                        elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                            game.cancel_quit()
                    else:
                        # Quit triggers: Cmd+Q on Mac, Ctrl+Q, Alt+F4
                        if (event.key == pygame.K_q and (event.mod & (pygame.KMOD_CTRL | pygame.KMOD_META))) or \
                           (event.key == pygame.K_F4 and (event.mod & pygame.KMOD_ALT)):
                            game.request_quit()
                        elif event.key == pygame.K_ESCAPE:
                            if game.state in ("PLAYING", "VICTORY", "DEFEAT"):
                                game.state = "MENU"
                            else:
                                game.request_quit()
                        elif event.key == pygame.K_r:
                            if game.state in ("PLAYING", "VICTORY", "DEFEAT"):
                                game.retry_current_level()

            if not running:
                break

            # Update & Draw
            game.update(dt)
            game.draw(screen, mouse_pos)

            # Flip Buffer
            pygame.display.flip()

    finally:
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    main()
