#!/usr/bin/env python3
"""Entry point for PRISM CALC — Scientific Calculator & Measuring Converter."""

from __future__ import annotations

import argparse
import os
import sys

os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")


def main(argv=None) -> int:
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

    from calconv.app import PrismCalcApp

    app = PrismCalcApp()
    if args.mode != "scientific":
        app.switch_mode(args.mode)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
