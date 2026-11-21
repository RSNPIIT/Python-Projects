"""
main.py - Main Entry Point for Reimagined Tetris.
OOP Engine, Super Rotation System, Glassmorphic UI & ModernGL Post-Processing Shaders.
"""

import os
import sys
import argparse
import signal
import atexit
import time

# Suppress Pygame-CE startup message
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# Terminal Guard: Ignore Ctrl+C, Ctrl+X, Ctrl+D in terminal while game is active
try:
    import termios
except ImportError:
    termios = None


class TerminalGuard:
    def __init__(self):
        self.fd = None
        self.saved_attr = None

    def activate(self):
        for sig_name in ("SIGINT", "SIGQUIT", "SIGTSTP"):
            sig = getattr(signal, sig_name, None)
            if sig is not None:
                try:
                    signal.signal(sig, signal.SIG_IGN)
                except Exception:
                    pass

        if termios is None:
            return

        try:
            if sys.stdin and sys.stdin.isatty():
                self.fd = sys.stdin.fileno()
            else:
                self.fd = os.open("/dev/tty", os.O_RDWR)
        except Exception:
            self.fd = None

        if self.fd is None:
            return

        try:
            self.saved_attr = termios.tcgetattr(self.fd)
            new_attr = termios.tcgetattr(self.fd)
            new_attr[0] &= ~(termios.IXON | termios.IXOFF | termios.BRKINT | termios.IGNBRK)
            new_attr[3] &= ~(termios.ISIG | termios.ICANON | termios.ECHO | termios.IEXTEN)
            cc = new_attr[6]
            vdisable = getattr(termios, "_POSIX_VDISABLE", 0)
            for idx_name in ("VINTR", "VQUIT", "VEOF", "VSUSP", "VSTART", "VSTOP"):
                idx = getattr(termios, idx_name, None)
                if idx is not None and idx < len(cc):
                    cc[idx] = vdisable
            termios.tcsetattr(self.fd, termios.TCSANOW, new_attr)
            atexit.register(self.restore)
        except Exception:
            pass

    def restore(self):
        if self.fd is not None and self.saved_attr is not None and termios is not None:
            try:
                termios.tcflush(self.fd, termios.TCIFLUSH)
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.saved_attr)
            except Exception:
                pass
            self.saved_attr = None


_TERM_GUARD = TerminalGuard()
_TERM_GUARD.activate()

import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE
from src.audio.sound_manager import SoundManager
from src.graphics.shader_manager import ShaderManager
from src.graphics.renderer import GameRenderer
from src.engine.game_state import GameState
from src.states.menu_state import MenuState
from src.states.modals import PauseModal, GameOverModal


class TetrisApp:
    def __init__(self, use_shaders=True, start_mode='marathon'):
        pygame.init()
        pygame.font.init()

        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.use_shaders = use_shaders
        self.current_mode = start_mode

        # Display Setup
        if self.use_shaders:
            try:
                pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
                pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
                pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
                pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
                self.window = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF)
                self.render_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            except Exception as e:
                print(f"[TetrisApp] OpenGL window mode warning: {e}. Falling back to software display.")
                self.use_shaders = False
                self.window = pygame.display.set_mode((self.width, self.height))
                self.render_surf = self.window
        else:
            self.window = pygame.display.set_mode((self.width, self.height))
            self.render_surf = self.window

        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Subsystems
        self.sound_mgr = SoundManager()
        self.shader_mgr = ShaderManager(self.width, self.height, use_opengl=self.use_shaders)
        self.renderer = GameRenderer(self.render_surf, self.width, self.height)

        # App State
        self.app_state = 'MENU'  # 'MENU', 'PLAYING', 'PAUSED', 'GAMEOVER'
        self.game = None
        self.menu = MenuState(self.sound_mgr, self.shader_mgr, self.start_game)
        self.pause_modal = None
        self.game_over_modal = None

        self.start_time = time.time()
        self.running = True

    def start_game(self, mode):
        self.current_mode = mode
        self.game = GameState(self.sound_mgr, self.shader_mgr, mode=mode)
        self.pause_modal = PauseModal(
            resume_cb=self.resume_game,
            restart_cb=lambda: self.start_game(self.current_mode),
            menu_cb=self.return_to_menu
        )
        self.app_state = 'PLAYING'

    def resume_game(self):
        if self.game:
            self.game.is_paused = False
        self.app_state = 'PLAYING'
        self.sound_mgr.play('ui_click')

    def return_to_menu(self):
        self.app_state = 'MENU'
        self.sound_mgr.play('ui_click')

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            time_sec = time.time() - self.start_time
            mouse_pos = pygame.mouse.get_pos()

            # Event Loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                if event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                    # Quick toggle for scanlines
                    self.shader_mgr.enable_scanlines = not self.shader_mgr.enable_scanlines
                    self.sound_mgr.play('ui_click')

                if self.app_state == 'MENU':
                    self.menu.handle_event(event)

                elif self.app_state == 'PLAYING':
                    if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.app_state = 'PAUSED'
                        self.sound_mgr.play('ui_click')
                    else:
                        self.game.handle_event(event)

                elif self.app_state == 'PAUSED':
                    if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.resume_game()
                    else:
                        self.pause_modal.handle_event(event)

                elif self.app_state == 'GAMEOVER':
                    self.game_over_modal.handle_event(event)

            # Update & Draw
            if self.app_state == 'MENU':
                self.menu.update(mouse_pos, dt)
                self.menu.draw(self.render_surf, time_sec)

            elif self.app_state in ('PLAYING', 'PAUSED', 'GAMEOVER'):
                if self.app_state == 'PLAYING':
                    self.game.update(dt)

                    # Check for transition to game over / victory
                    if self.game.is_game_over or self.game.is_victory:
                        self.app_state = 'GAMEOVER'
                        self.game_over_modal = GameOverModal(
                            is_victory=self.game.is_victory,
                            score_mgr=self.game.score_mgr,
                            elapsed_time=self.game.elapsed_time,
                            restart_cb=lambda: self.start_game(self.current_mode),
                            menu_cb=self.return_to_menu
                        )

                self.renderer.render_game_scene(self.render_surf, self.game, time_sec)

                if self.app_state == 'PAUSED':
                    self.pause_modal.update(mouse_pos, dt)
                    self.pause_modal.draw(self.render_surf)

                elif self.app_state == 'GAMEOVER':
                    self.game_over_modal.update(mouse_pos, dt)
                    self.game_over_modal.draw(self.render_surf)

            # Shader post-processing pass
            self.shader_mgr.update(dt)
            self.shader_mgr.render(self.render_surf, time_sec=time_sec)

        self.cleanup()

    def cleanup(self):
        pygame.quit()
        _TERM_GUARD.restore()
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Reimagined Tetris // Cyber Matrix")
    parser.add_argument('--no-shader', action='store_true', help="Disable OpenGL post-processing shaders and run in software mode")
    parser.add_argument('--mode', type=str, default='marathon', choices=['marathon', 'sprint', 'ultra', 'wide'], help="Initial game mode")
    args = parser.parse_args()

    app = TetrisApp(use_shaders=(not args.no_shader), start_mode=args.mode)
    app.run()


if __name__ == '__main__':
    main()
