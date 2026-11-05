"""Tiny compatibility shims for raylib's strict CFFI integer signatures.

The game naturally computes many screen coordinates as floats.  Raylib's
DrawRectangle family expects C ints, so these wrappers cast at the boundary
instead of forcing every call site to remember.
"""

from __future__ import annotations

import raylib as rl

_orig_rect = rl.DrawRectangle
_orig_rect_lines = rl.DrawRectangleLines
_orig_gradient_v = rl.DrawRectangleGradientV
_orig_gradient_h = rl.DrawRectangleGradientH
_orig_circle = rl.DrawCircle
_orig_circle_lines = rl.DrawCircleLines


def draw_rectangle(x, y, w, h, color) -> None:
    _orig_rect(int(x), int(y), int(w), int(h), color)


def draw_rectangle_lines(x, y, w, h, color) -> None:
    _orig_rect_lines(int(x), int(y), int(w), int(h), color)


def draw_rectangle_gradient_v(x, y, w, h, top, bottom) -> None:
    _orig_gradient_v(int(x), int(y), int(w), int(h), top, bottom)


def draw_rectangle_gradient_h(x, y, w, h, left, right) -> None:
    _orig_gradient_h(int(x), int(y), int(w), int(h), left, right)


def draw_circle(cx, cy, radius, color) -> None:
    _orig_circle(int(cx), int(cy), float(radius), color)


def draw_circle_lines(cx, cy, radius, color) -> None:
    _orig_circle_lines(int(cx), int(cy), float(radius), color)


rl.DrawRectangle = draw_rectangle
rl.DrawRectangleLines = draw_rectangle_lines
rl.DrawRectangleGradientV = draw_rectangle_gradient_v
rl.DrawRectangleGradientH = draw_rectangle_gradient_h
rl.DrawCircle = draw_circle
rl.DrawCircleLines = draw_circle_lines
