#!/usr/bin/env python3
"""NOVA STRIKE: ECLIPSE PROTOCOL

A complete DOOM-style superhero FPS built with raylib for Python.
"""

from __future__ import annotations

import sys

from game.game import Game


def main() -> int:
    game: Game | None = None
    try:
        game = Game()
        game.run()
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception:
        if game is not None:
            try:
                game.shutdown()
            except Exception:
                pass
        raise


if __name__ == "__main__":
    sys.exit(main())
