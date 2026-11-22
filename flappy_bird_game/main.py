#!/usr/bin/env python3
"""
main.py - Entry Point for KFlapper // The OG Classic Flappy Bird (HD Edition).
"""

import os
import sys

# Ensure local source directory is available on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game import KFlapperGame


def main():
    game = KFlapperGame()
    game.run()


if __name__ == "__main__":
    main()
