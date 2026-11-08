#!/usr/bin/env python3
"""THORNSPIRE entry point.

Examples:
    python main.py                     # play
    python main.py --mode trial        # boot straight into a time trial intent
    python main.py --autoplay --god    # attract-mode demo
    python main.py --headless --autoplay --max-seconds 5
"""

from __future__ import annotations

import argparse
import os
import signal
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_HINT_NO_SIGNAL_HANDLERS", "1")

try:
    import termios as _termios
except ImportError:
    _termios = None


def _ignore_terminal_signals() -> None:
    """Ignore Ctrl+C (SIGINT), Ctrl+\\ (SIGQUIT), Ctrl+Z (SIGTSTP), and Ctrl+Break."""
    for sig_name in ("SIGINT", "SIGQUIT", "SIGTSTP", "SIGBREAK"):
        sig = getattr(signal, sig_name, None)
        if sig is not None:
            try:
                signal.signal(sig, signal.SIG_IGN)
            except (OSError, ValueError):
                pass


class _TerminalGuard:
    """Silence and discard terminal Ctrl+C, Ctrl+X, Ctrl+D, 'exit', and 'quit' while running."""

    def __init__(self) -> None:
        self._fd: int | None = None
        self._saved_attrs = None

    def __enter__(self) -> _TerminalGuard:
        _ignore_terminal_signals()
        if _termios is None:
            return self
        try:
            if not sys.stdin or not sys.stdin.isatty():
                return self
            fd = sys.stdin.fileno()
            saved = _termios.tcgetattr(fd)
            attrs = _termios.tcgetattr(fd)
            # Disable terminal signal generation, canonical line buffering, and echo
            lflag_mask = _termios.ECHO | _termios.ECHONL | _termios.ICANON | _termios.ISIG
            if hasattr(_termios, "IEXTEN"):
                lflag_mask |= _termios.IEXTEN
            attrs[3] &= ~lflag_mask

            try:
                vdisable_int = os.fpathconf(fd, "PC_VDISABLE")
            except (AttributeError, OSError, ValueError):
                vdisable_int = 255 if sys.platform == "darwin" else 0

            cc = attrs[6]
            sample = cc[0] if cc else b"\x00"
            vdisable = bytes([vdisable_int]) if isinstance(sample, (bytes, bytearray)) else vdisable_int
            for cc_name in ("VINTR", "VQUIT", "VEOF", "VSUSP", "VDSUSP", "VEOL", "VEOL2"):
                idx = getattr(_termios, cc_name, None)
                if idx is not None and 0 <= idx < len(cc):
                    cc[idx] = vdisable
            if hasattr(_termios, "VMIN") and _termios.VMIN < len(cc):
                cc[_termios.VMIN] = 1
            if hasattr(_termios, "VTIME") and _termios.VTIME < len(cc):
                cc[_termios.VTIME] = 0

            _termios.tcsetattr(fd, _termios.TCSANOW, attrs)
            self._fd = fd
            self._saved_attrs = saved
        except Exception:
            self._fd = None
            self._saved_attrs = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if _termios is not None and self._fd is not None:
            try:
                _termios.tcflush(self._fd, _termios.TCIFLUSH)
            except Exception:
                pass
            if self._saved_attrs is not None:
                try:
                    _termios.tcsetattr(self._fd, _termios.TCSADRAIN, self._saved_attrs)
                except Exception:
                    pass
        # Suppress any stray KeyboardInterrupt / EOFError
        return exc_type in (KeyboardInterrupt, EOFError)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="THORNSPIRE — a procedural climbing platformer")
    parser.add_argument("--mode", choices=("levels", "loop", "trial"), default="levels",
                        help="game mode (levels, loop, trial)")
    parser.add_argument("--difficulty", choices=("easy", "medium", "hard"), default=None,
                        help="difficulty mode (easy, medium, hard)")
    parser.add_argument("--customize", action="store_true",
                        help="launch directly into hero customization screen")
    parser.add_argument("--level-select", action="store_true",
                        help="launch directly into the 100-level select browser")
    parser.add_argument("--level", type=int, default=None,
                        help="level number to launch directly (1 to 100)")
    parser.add_argument("--seed", type=int, default=None, help="world seed")
    parser.add_argument("--autoplay", action="store_true", help="start a bot-driven demo")
    parser.add_argument("--god", action="store_true", help="disable damage (debug/capture)")
    parser.add_argument("--mute", action="store_true", help="start muted")
    parser.add_argument("--headless", action="store_true", help="use dummy SDL drivers")
    parser.add_argument("--max-seconds", type=float, default=None,
                        help="quit automatically after N seconds")
    parser.add_argument("--fullscreen", action="store_true", help="start fullscreen")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    _ignore_terminal_signals()
    args = parse_args(argv)
    if args.headless:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    with _TerminalGuard():
        # Import after SDL environment and signal guards are set.
        from game.game import Game

        game = Game(seed=args.seed, mode=args.mode, headless=args.headless,
                    mute=args.mute, autoplay=args.autoplay, god=args.god)
        _ignore_terminal_signals()
        if args.difficulty:
            game.difficulty_mode = args.difficulty
        if args.customize:
            game.state = "customize"
        elif args.level_select:
            game.state = "level_select"
            game.selected_level = min(100, int(game.save.get("unlocked_level", 1)))
            game.level_page = (game.selected_level - 1) // 20
        elif args.level is not None:
            game.start_level(args.level)
        elif args.autoplay:
            if args.mode == "levels":
                game.start_level(1)
            else:
                game.start_run(args.mode, seed=args.seed)
        if args.fullscreen:
            game.toggle_fullscreen()
        game.run(max_seconds=args.max_seconds)
    return 0


if __name__ == "__main__":
    sys.exit(main())
