"""
randomizer.py - 7-Bag Randomizer and Next-Piece Preview Queue.
"""

import random
from collections import deque
from src.engine.tetromino import Tetromino


class SevenBagRandomizer:
    PIECES = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']

    def __init__(self, cols=10, buffer_rows=4, preview_size=5):
        self.cols = cols
        self.buffer_rows = buffer_rows
        self.preview_size = preview_size
        self.bag = deque()
        self.preview_queue = deque()
        self._fill_preview_queue()

    def _generate_bag(self):
        bag = list(self.PIECES)
        random.shuffle(bag)
        return bag

    def _fill_preview_queue(self):
        while len(self.preview_queue) < self.preview_size + 7:
            if not self.bag:
                self.bag.extend(self._generate_bag())
            self.preview_queue.append(self.bag.popleft())

    def get_spawn_coords(self, kind):
        # Guideline: Spawn horizontally centered, in buffer rows 2-3
        size = 4 if kind == 'I' else (2 if kind == 'O' else 3)
        spawn_x = (self.cols - size) // 2
        # Center I and O properly
        spawn_y = self.buffer_rows - (2 if kind in ('I', 'O') else 2)
        return spawn_x, spawn_y

    def pop_next(self):
        self._fill_preview_queue()
        kind = self.preview_queue.popleft()
        spawn_x, spawn_y = self.get_spawn_coords(kind)
        return Tetromino(kind, spawn_x, spawn_y, rotation=0)

    def peek_next(self, count=5):
        self._fill_preview_queue()
        return list(self.preview_queue)[:count]

    def reset(self):
        self.bag.clear()
        self.preview_queue.clear()
        self._fill_preview_queue()
