#!/usr/bin/env python3
"""
main.py - Entry Point for Modern Minesweeper in Python Tkinter (OOP).
"""

import os
import sys

# Silence macOS Tkinter deprecation warning
os.environ["TK_SILENCE_DEPRECATION"] = "1"

# Ensure package directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.main_window import MainWindow


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
