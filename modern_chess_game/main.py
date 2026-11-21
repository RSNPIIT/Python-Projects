"""Modern Chess Game - Main Application Entry Point"""
import os
import sys
import signal
from pathlib import Path

# 1. Suppress all terminal output & pygame banner
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# 2. Lock the terminal by completely ignoring terminal interrupt and suspend signals
# Ctrl+C (SIGINT), Ctrl+Z (SIGTSTP), Ctrl+\ (SIGQUIT)
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
import moderngl

# Ensure package directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from graphics.renderer import ModernRenderer
from audio.sound_manager import SoundManager
from game import ChessGame

def main():
    # 3. Initialize Pygame with OpenGL Core Profile 3.3
    pygame.init()
    pygame.display.set_caption("Modern Chess • OpenGL & ModernGL")

    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)

    # Enable High-DPI support on macOS
    flags = pygame.OPENGL | pygame.DOUBLEBUF
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)

    # 4. Initialize ModernGL Context (Silent, no print output)
    ctx = moderngl.create_context()
    fb_w, fb_h = pygame.display.get_surface().get_size()
    ctx.viewport = (0, 0, fb_w, fb_h)

    # 5. Initialize Audio & Graphics
    assets_dir = BASE_DIR / "assets"
    sound_mgr = SoundManager()
    renderer = ModernRenderer(ctx, assets_dir)
    game = ChessGame(renderer, sound_mgr)

    # 6. Main Game Loop (Only exits when the GUI window is closed)
    clock = pygame.time.Clock()
    running = True

    try:
        while running:
            dt = clock.tick(60) / 1000.0  # Delta time in seconds (capped at 60 FPS)
            time_sec = pygame.time.get_ticks() / 1000.0

            # Handle Pygame Events
            for event in pygame.event.get():
                # Only the GUI window close event or Cmd+Q/Alt+F4 terminates the game
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    game.handle_mouse_down(event.pos, event.button)
                elif event.type == pygame.MOUSEMOTION:
                    game.handle_mouse_move(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    game.handle_mouse_up(event.pos, event.button)
                elif event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_q and (event.mod & (pygame.KMOD_CTRL | pygame.KMOD_META))) or \
                       (event.key == pygame.K_F4 and (event.mod & pygame.KMOD_ALT)):
                        running = False
                    elif event.key == pygame.K_ESCAPE:
                        game.selected_sq = None
                        game.valid_moves.clear()
                    else:
                        game.handle_key_down(event)

            if not running:
                break

            # Update animations
            renderer.update_animations(dt)

            # Clear and Render
            ctx.clear(0.10, 0.11, 0.14)
            game.render(time_sec)

            # Swap Double Buffers
            pygame.display.flip()

    finally:
        # Clean up resources safely and silently
        try:
            renderer.texture_mgr.release_all()
        except Exception:
            pass
        try:
            pygame.quit()
        except Exception:
            pass
        sys.exit(0)

if __name__ == "__main__":
    main()
