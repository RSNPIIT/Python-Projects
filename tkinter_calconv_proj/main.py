#!/usr/bin/env python3
"""Entry point for PRISM CALC — Scientific Calculator & Measuring Converter."""

from __future__ import annotations

import argparse
import os
import signal
import sys

os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")

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
        return exc_type in (KeyboardInterrupt, EOFError)


def main(argv=None) -> int:
    _ignore_terminal_signals()
    parser = argparse.ArgumentParser(
        description="PRISM CALC — Tkinter Scientific Calculator, Measuring Converter & Suite"
    )
    parser.add_argument(
        "--mode",
        choices=("scientific", "converter", "programmer", "grapher", "tools"),
        default="scientific",
        help="initial tab to open",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run non-GUI mathematical & converter verification suite and exit",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        from tests.test_suite import run_all_tests

        run_all_tests()
        return 0

    try:
        import tkinter as tk
    except ModuleNotFoundError:
        sys.stderr.write(
            "Error: Python's tkinter module is not installed for this interpreter.\n"
            "Launch with ./run.sh (auto-installs modern python-tk via Homebrew),\n"
            "or run:  brew install python-tk\n"
        )
        return 1

    if sys.platform == "darwin" and float(tk.TkVersion) < 8.6:
        sys.stderr.write(
            f"Error: Running under Apple's deprecated system Tk {tk.TkVersion} ({sys.executable}),\n"
            "which renders blank windows on modern macOS.\n"
            "Please run ./run.sh so Homebrew's modern Tcl/Tk (8.6+ / 9.0) is used!\n"
        )
        return 1

    with _TerminalGuard():
        from calconv.app import PrismCalcApp

        app = PrismCalcApp()
        if args.mode != "scientific":
            app.switch_mode(args.mode)
        while True:
            try:
                app.mainloop()
                break
            except (KeyboardInterrupt, EOFError):
                continue
    return 0


if __name__ == "__main__":
    sys.exit(main())
