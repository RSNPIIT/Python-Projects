"""2048 Game - Application Main Entry Point with Signal Locks and 60 FPS Loop"""
import os
import signal
import sys

# Suppress Pygame welcoming splash prompt
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game import Game2048

def setup_signal_handlers(game: Game2048):
    """Intercepts Ctrl+C (SIGINT) and terminal suspend (SIGTSTP) for graceful exit dialog."""
    def sig_handler(sig, frame):
        game.show_quit_dialog = True

    try:
        signal.signal(signal.SIGINT, sig_handler)
    except Exception:
        pass

    try:
        if hasattr(signal, "SIGTSTP"):
            signal.signal(signal.SIGTSTP, sig_handler)
    except Exception:
        pass

def main():
    pygame.init()
    pygame.display.set_caption("2048")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    game = Game2048()
    setup_signal_handlers(game)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        # Guard against large dt hiccups on window blur
        dt = min(dt, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.show_quit_dialog = True

            elif event.type == pygame.KEYDOWN:
                # Cmd+Q (Mac) or Alt+F4 (Windows/Linux)
                is_mac_cmd_q = (event.key == pygame.K_q and (event.mod & pygame.KMOD_META))
                is_alt_f4 = (event.key == pygame.K_F4 and (event.mod & pygame.KMOD_ALT))
                if is_mac_cmd_q or is_alt_f4:
                    game.show_quit_dialog = True
                else:
                    game.handle_keydown(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    game.handle_mouse_down(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    game.handle_mouse_up(event.pos)

        if game.should_exit:
            running = False
            break

        game.update(dt)
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
