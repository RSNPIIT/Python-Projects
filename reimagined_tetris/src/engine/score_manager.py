"""
score_manager.py - Guideline Scoring, Combos, Back-to-Back, Level Progression & High Scores.
"""

import json
import os
from config import HIGHSCORES_FILE, SCORE_TABLE


class ScoreManager:
    def __init__(self, mode='marathon'):
        self.mode = mode
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = -1
        self.b2b = False
        self.max_combo = 0

        # Detailed stats
        self.singles = 0
        self.doubles = 0
        self.triples = 0
        self.tetrises = 0
        self.tspins = 0
        self.perfect_clears = 0

        self.high_score = self.load_high_score()

    @property
    def gravity_interval(self):
        # Guideline gravity formula (in seconds per drop step)
        lvl = max(1, min(self.level, 20))
        seconds_per_step = (0.8 - ((lvl - 1) * 0.007)) ** (lvl - 1)
        return max(0.016, seconds_per_step)

    def add_soft_drop_points(self, rows_dropped):
        self.score += rows_dropped * SCORE_TABLE['soft_drop']

    def add_hard_drop_points(self, rows_dropped):
        self.score += rows_dropped * SCORE_TABLE['hard_drop']

    def register_lock_without_clear(self):
        self.combo = -1

    def register_line_clear(self, lines_cleared, tspin_type='none', is_perfect_clear=False):
        if lines_cleared <= 0 and tspin_type == 'none':
            self.combo = -1
            return None

        self.combo += 1
        if self.combo > self.max_combo:
            self.max_combo = self.combo

        is_difficult = (lines_cleared == 4) or (tspin_type in ('mini', 'regular') and lines_cleared > 0)
        action_name = ""
        pts = 0

        # T-Spin Scoring
        if tspin_type == 'mini':
            self.tspins += 1
            if lines_cleared == 0:
                action_name = "T-SPIN MINI"
                pts = SCORE_TABLE['tspin_mini'] * self.level
            elif lines_cleared == 1:
                action_name = "T-SPIN MINI SINGLE"
                pts = (SCORE_TABLE['b2b_tetris'] if self.b2b else 200) * self.level
        elif tspin_type == 'regular':
            self.tspins += 1
            if lines_cleared == 0:
                action_name = "T-SPIN"
                pts = 400 * self.level
            elif lines_cleared == 1:
                action_name = "T-SPIN SINGLE"
                pts = (1200 if self.b2b else SCORE_TABLE['tspin_single']) * self.level
            elif lines_cleared == 2:
                action_name = "T-SPIN DOUBLE"
                pts = (SCORE_TABLE['b2b_tspin_double'] if self.b2b else SCORE_TABLE['tspin_double']) * self.level
            elif lines_cleared == 3:
                action_name = "T-SPIN TRIPLE"
                pts = (SCORE_TABLE['b2b_tspin_triple'] if self.b2b else SCORE_TABLE['tspin_triple']) * self.level
        else:
            # Standard Line Clears
            if lines_cleared == 1:
                self.singles += 1
                action_name = "SINGLE"
                pts = SCORE_TABLE['single'] * self.level
            elif lines_cleared == 2:
                self.doubles += 1
                action_name = "DOUBLE"
                pts = SCORE_TABLE['double'] * self.level
            elif lines_cleared == 3:
                self.triples += 1
                action_name = "TRIPLE"
                pts = SCORE_TABLE['triple'] * self.level
            elif lines_cleared == 4:
                self.tetrises += 1
                action_name = "TETRIS!"
                pts = (SCORE_TABLE['b2b_tetris'] if self.b2b else SCORE_TABLE['tetris']) * self.level

        # Back-to-Back state update
        b2b_applied = False
        if is_difficult:
            if self.b2b:
                b2b_applied = True
            self.b2b = True
        elif lines_cleared > 0:
            self.b2b = False

        # Combo bonus: 50 * combo * level
        combo_bonus = 0
        if self.combo > 0:
            combo_bonus = 50 * self.combo * self.level
            pts += combo_bonus

        # Perfect Clear (All Clear) bonus
        if is_perfect_clear:
            self.perfect_clears += 1
            pc_pts = 0
            if lines_cleared == 1:
                pc_pts = SCORE_TABLE['all_clear_single'] * self.level
            elif lines_cleared == 2:
                pc_pts = SCORE_TABLE['all_clear_double'] * self.level
            elif lines_cleared == 3:
                pc_pts = SCORE_TABLE['all_clear_triple'] * self.level
            elif lines_cleared == 4:
                pc_pts = (SCORE_TABLE['b2b_all_clear_tetris'] if b2b_applied else SCORE_TABLE['all_clear_tetris']) * self.level
            pts += pc_pts

        self.score += pts
        self.lines += lines_cleared

        # Level up every 10 lines (in Marathon mode)
        new_level = 1 + (self.lines // 10)
        level_up = (new_level > self.level)
        self.level = new_level

        if self.score > self.high_score:
            self.high_score = self.score

        return {
            'action_name': action_name,
            'points': pts,
            'lines': lines_cleared,
            'combo': self.combo,
            'b2b': b2b_applied,
            'level_up': level_up,
            'is_perfect_clear': is_perfect_clear,
        }

    def load_high_score(self):
        if not os.path.exists(HIGHSCORES_FILE):
            return 0
        try:
            with open(HIGHSCORES_FILE, 'r') as f:
                data = json.load(f)
                return data.get(self.mode, 0)
        except Exception:
            return 0

    def save_high_score(self):
        os.makedirs(os.path.dirname(HIGHSCORES_FILE), exist_ok=True)
        data = {}
        if os.path.exists(HIGHSCORES_FILE):
            try:
                with open(HIGHSCORES_FILE, 'r') as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data[self.mode] = max(data.get(self.mode, 0), self.score)
        try:
            with open(HIGHSCORES_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[ScoreManager] Failed to save high scores: {e}")
