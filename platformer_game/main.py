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
import sys


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="THORNSPIRE — a procedural climbing platformer")
    parser.add_argument("--mode", choices=("loop", "trial"), default="loop",
                        help="mode highlighted on the title screen / used by autoplay")
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
    args = parse_args(argv)
    if args.headless:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    # Import after the SDL environment is set so pygame sees the dummy drivers.
    from game.game import Game

    game = Game(seed=args.seed, mode=args.mode, headless=args.headless,
                mute=args.mute, autoplay=args.autoplay, god=args.god)
    if args.autoplay:
        game.start_run(args.mode, seed=args.seed)
    if args.fullscreen:
        game.toggle_fullscreen()
    game.run(max_seconds=args.max_seconds)
    return 0


if __name__ == "__main__":
    sys.exit(main())
