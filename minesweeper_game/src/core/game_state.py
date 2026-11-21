"""
game_state.py - State Machine, Difficulty Profiles, and High Score Telemetry.
Manages time tracking, shield lives, game modes, and JSON record persistence.
"""

import json
import os
import time
from enum import Enum, auto
from typing import Any, Dict, Optional, Tuple


class GameStatus(Enum):
    READY = auto()
    PLAYING = auto()
    PAUSED = auto()
    WON = auto()
    LOST = auto()


class Difficulty(Enum):
    BEGINNER = ("Beginner", 9, 9, 10)
    INTERMEDIATE = ("Intermediate", 16, 16, 40)
    EXPERT = ("Expert", 16, 30, 99)
    MASTER = ("Master", 20, 30, 130)
    CUSTOM = ("Custom", 10, 10, 15)

    def __init__(self, display_name: str, rows: int, cols: int, mines: int):
        self.display_name = display_name
        self.rows = rows
        self.cols = cols
        self.mines = mines


class GameMode(Enum):
    CLASSIC = "Classic"         # 1 Life - pure rules
    SHIELD = "Shield Mode"      # 1 Shield prevents first lethal detonation
    TIME_ATTACK = "Time Attack" # Clear before countdown clock expires


class GameStats:
    """Tracks high scores, win streaks, and 3BV efficiency across sessions."""

    RECORDS_FILE = os.path.expanduser("~/.minesweeper_records.json")

    def __init__(self):
        self.records: Dict[str, Any] = self._load_records()

    def _default_records(self) -> Dict[str, Any]:
        return {
            "Beginner": {"best_time": None, "played": 0, "won": 0, "streak": 0, "best_streak": 0},
            "Intermediate": {"best_time": None, "played": 0, "won": 0, "streak": 0, "best_streak": 0},
            "Expert": {"best_time": None, "played": 0, "won": 0, "streak": 0, "best_streak": 0},
            "Master": {"best_time": None, "played": 0, "won": 0, "streak": 0, "best_streak": 0},
            "Custom": {"best_time": None, "played": 0, "won": 0, "streak": 0, "best_streak": 0},
        }

    def _load_records(self) -> Dict[str, Any]:
        if os.path.exists(self.RECORDS_FILE):
            try:
                with open(self.RECORDS_FILE, "r") as f:
                    data = json.load(f)
                    defaults = self._default_records()
                    for k, v in defaults.items():
                        if k not in data:
                            data[k] = v
                    return data
            except Exception:
                pass
        return self._default_records()

    def save_records(self) -> None:
        try:
            with open(self.RECORDS_FILE, "w") as f:
                json.dump(self.records, f, indent=2)
        except Exception:
            pass

    def record_game(self, diff_name: str, won: bool, elapsed_seconds: float) -> Tuple[bool, Optional[float]]:
        """
        Updates statistics for difficulty preset.
        Returns:
            (is_new_best: bool, previous_best: Optional[float])
        """
        if diff_name not in self.records:
            self.records[diff_name] = {"best_time": None, "played": 0, "won": 0, "streak": 0, "best_streak": 0}

        entry = self.records[diff_name]
        entry["played"] += 1
        is_new_best = False
        prev_best = entry.get("best_time")

        if won:
            entry["won"] += 1
            entry["streak"] = entry.get("streak", 0) + 1
            entry["best_streak"] = max(entry["streak"], entry.get("best_streak", 0))

            if prev_best is None or elapsed_seconds < prev_best:
                entry["best_time"] = round(elapsed_seconds, 2)
                is_new_best = True
        else:
            entry["streak"] = 0

        self.save_records()
        return is_new_best, prev_best

    def get_stats(self, diff_name: str) -> Dict[str, Any]:
        return self.records.get(diff_name, {"best_time": None, "played": 0, "won": 0, "streak": 0, "best_streak": 0})

    def reset_stats(self) -> None:
        self.records = self._default_records()
        self.save_records()
