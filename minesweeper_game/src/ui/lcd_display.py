"""
lcd_display.py - Authentic 7-Segment Digital LED Display Widget.
Renders glowing 3-digit score & timer meters on a Tkinter Canvas.
"""

import tkinter as tk
from typing import Dict, List, Tuple


class LCDDisplay(tk.Canvas):
    """3-digit 7-segment digital counter widget."""

    # 7-Segment mappings: A(top), B(top-right), C(bottom-right), D(bottom), E(bottom-left), F(top-left), G(middle)
    SEGMENTS_MAP: Dict[str, Tuple[bool, ...]] = {
        '0': (True,  True,  True,  True,  True,  True,  False),
        '1': (False, True,  True,  False, False, False, False),
        '2': (True,  True,  False, True,  True,  False, True),
        '3': (True,  True,  True,  True,  False, False, True),
        '4': (False, True,  True,  False, False, True,  True),
        '5': (True,  False, True,  True,  False, True,  True),
        '6': (True,  False, True,  True,  True,  True,  True),
        '7': (True,  True,  True,  False, False, False, False),
        '8': (True,  True,  True,  True,  True,  True,  True),
        '9': (True,  True,  True,  True,  False, True,  True),
        '-': (False, False, False, False, False, False, True),
        ' ': (False, False, False, False, False, False, False),
    }

    def __init__(self, parent, value: int = 0, bg_color: str = "#020617", fg_color: str = "#38bdf8", off_color: str = "#0c4a6e", **kwargs):
        super().__init__(parent, width=74, height=38, bg=bg_color, highlightthickness=2, highlightbackground="#334155", **kwargs)
        self.value = value
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.off_color = off_color
        self.draw_digits()

    def set_theme(self, bg_color: str, fg_color: str, off_color: str):
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.off_color = off_color
        self.configure(bg=bg_color)
        self.draw_digits()

    def set_value(self, val: int):
        # Clamp to 3-digit display limits (-99 to 999)
        self.value = max(-99, min(999, val))
        self.draw_digits()

    def _draw_segment_digit(self, x_offset: int, char: str):
        segs = self.SEGMENTS_MAP.get(char, self.SEGMENTS_MAP[' '])

        # Digit layout dimensions
        w = 16
        h = 28
        t = 3.5  # Segment thickness
        y_offset = 5

        # Points for 7 segments (A, B, C, D, E, F, G)
        # A: top horizontal
        p_a = [x_offset + 2, y_offset, x_offset + w - 2, y_offset, x_offset + w - 4, y_offset + t, x_offset + 4, y_offset + t]
        # B: top right vertical
        p_b = [x_offset + w, y_offset + 2, x_offset + w, y_offset + h/2 - 1, x_offset + w - t, y_offset + h/2 - 2, x_offset + w - t, y_offset + 4]
        # C: bottom right vertical
        p_c = [x_offset + w, y_offset + h/2 + 1, x_offset + w, y_offset + h - 2, x_offset + w - t, y_offset + h - 4, x_offset + w - t, y_offset + h/2 + 2]
        # D: bottom horizontal
        p_d = [x_offset + 2, y_offset + h, x_offset + w - 2, y_offset + h, x_offset + w - 4, y_offset + h - t, x_offset + 4, y_offset + h - t]
        # E: bottom left vertical
        p_e = [x_offset, y_offset + h/2 + 1, x_offset, y_offset + h - 2, x_offset + t, y_offset + h - 4, x_offset + t, y_offset + h/2 + 2]
        # F: top left vertical
        p_f = [x_offset, y_offset + 2, x_offset, y_offset + h/2 - 1, x_offset + t, y_offset + h/2 - 2, x_offset + t, y_offset + 4]
        # G: middle horizontal
        p_g = [x_offset + 2, y_offset + h/2, x_offset + 4, y_offset + h/2 - t/2, x_offset + w - 4, y_offset + h/2 - t/2,
               x_offset + w - 2, y_offset + h/2, x_offset + w - 4, y_offset + h/2 + t/2, x_offset + 4, y_offset + h/2 + t/2]

        all_polys = [p_a, p_b, p_c, p_d, p_e, p_f, p_g]

        for i, is_on in enumerate(segs):
            color = self.fg_color if is_on else self.off_color
            self.create_polygon(all_polys[i], fill=color, outline="")

    def draw_digits(self):
        self.delete("all")
        # Format string
        if self.value < 0:
            text = f"-{abs(self.value):02d}"
        else:
            text = f"{self.value:03d}"

        # 3 Digits
        spacing = 23
        start_x = 5
        for i, ch in enumerate(text[-3:]):
            self._draw_segment_digit(start_x + i * spacing, ch)
