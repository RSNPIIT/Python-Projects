"""
grid_canvas.py - Interactive High-Performance Minesweeper Board Canvas.
Features procedural vector tiles, hover glow, flag rendering, explosion effects, and confetti.
"""

import math
import random
import tkinter as tk
from typing import Callable, Dict, List, Optional, Set, Tuple
from ..core.board import Board
from ..core.cell import Cell, CellState


class GridCanvas(tk.Canvas):
    """Renders the Minesweeper grid and translates user mouse inputs into game events."""

    def __init__(
        self,
        parent,
        board: Board,
        theme: Dict[str, any],
        cell_size: int = 30,
        on_reveal: Optional[Callable[[int, int], None]] = None,
        on_flag: Optional[Callable[[int, int], None]] = None,
        on_chord: Optional[Callable[[int, int], None]] = None,
        on_suspense_start: Optional[Callable[[], None]] = None,
        on_suspense_end: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        self.board = board
        self.theme = theme
        self.cell_size = cell_size

        self.on_reveal = on_reveal
        self.on_flag = on_flag
        self.on_chord = on_chord
        self.on_suspense_start = on_suspense_start
        self.on_suspense_end = on_suspense_end

        self.hover_cell: Optional[Tuple[int, int]] = None
        self.pressed_cell: Optional[Tuple[int, int]] = None
        self.hint_cell: Optional[Tuple[int, int]] = None

        # Victory Confetti particles
        self.confetti_particles: List[Dict[str, float]] = []
        self.confetti_active = False

        width = self.board.cols * self.cell_size
        height = self.board.rows * self.cell_size

        super().__init__(
            parent,
            width=width,
            height=height,
            bg=self.theme["bg_board"],
            highlightthickness=0,
            **kwargs
        )

        # Mouse Event Bindings (Cross-platform Mac / Linux / Windows)
        self.bind("<Motion>", self._on_motion)
        self.bind("<Leave>", self._on_leave)

        # Left Click (Reveal)
        self.bind("<Button-1>", self._on_left_press)
        self.bind("<ButtonRelease-1>", self._on_left_release)

        # Right Click (Flag) - handles Button-2 on Mac, Button-3 on standard X11/Win
        self.bind("<Button-2>", self._on_right_click)
        self.bind("<Button-3>", self._on_right_click)
        self.bind("<Control-Button-1>", self._on_right_click)

        # Middle Click or Double Click (Chord)
        self.bind("<Double-Button-1>", self._on_chord_event)
        self.bind("<Button-2>", self._on_right_click)  # Tkinter on Mac maps 2 to right click usually

    def update_dimensions(self):
        """Resizes canvas to match current board rows & cols."""
        width = self.board.cols * self.cell_size
        height = self.board.rows * self.cell_size
        self.configure(width=width, height=height, bg=self.theme["bg_board"])
        self.redraw()

    def set_theme(self, new_theme: Dict[str, any]):
        self.theme = new_theme
        self.configure(bg=self.theme["bg_board"])
        self.redraw()

    def set_hint(self, row: int, col: int):
        self.hint_cell = (row, col)
        self.redraw()

    def clear_hint(self):
        self.hint_cell = None
        self.redraw()

    def _get_cell_at_pixel(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        c = x // self.cell_size
        r = y // self.cell_size
        if 0 <= r < self.board.rows and 0 <= c < self.board.cols:
            return r, c
        return None

    def _on_motion(self, event):
        coords = self._get_cell_at_pixel(event.x, event.y)
        if coords != self.hover_cell:
            self.hover_cell = coords
            self.redraw()

    def _on_leave(self, _):
        if self.hover_cell is not None:
            self.hover_cell = None
            if self.pressed_cell is not None:
                self.pressed_cell = None
                if self.on_suspense_end:
                    self.on_suspense_end()
            self.redraw()

    def _on_left_press(self, event):
        coords = self._get_cell_at_pixel(event.x, event.y)
        if coords:
            self.pressed_cell = coords
            if self.on_suspense_start:
                self.on_suspense_start()
            self.redraw()

    def _on_left_release(self, event):
        coords = self._get_cell_at_pixel(event.x, event.y)
        if self.on_suspense_end:
            self.on_suspense_end()

        if coords and coords == self.pressed_cell:
            r, c = coords
            cell = self.board.get_cell(r, c)
            if cell:
                if cell.is_revealed and cell.neighbor_mines > 0:
                    # Chording on revealed numbered tile
                    if self.on_chord:
                        self.on_chord(r, c)
                elif cell.is_hidden:
                    # Reveal unrevealed tile
                    if self.on_reveal:
                        self.on_reveal(r, c)

        self.pressed_cell = None
        self.redraw()

    def _on_right_click(self, event):
        coords = self._get_cell_at_pixel(event.x, event.y)
        if coords:
            r, c = coords
            if self.on_flag:
                self.on_flag(r, c)
            self.redraw()

    def _on_chord_event(self, event):
        coords = self._get_cell_at_pixel(event.x, event.y)
        if coords:
            r, c = coords
            if self.on_chord:
                self.on_chord(r, c)
            self.redraw()

    # --- Drawing Helpers ---

    def _draw_flag(self, x: int, y: int, s: int):
        pad = s * 0.22
        pole_x = x + pad + 3
        pole_y_top = y + pad
        pole_y_bot = y + s - pad

        # Metallic Pole
        self.create_line(pole_x, pole_y_top, pole_x, pole_y_bot, fill=self.theme["flag_pole"], width=2)
        # Triangular Flag Fabric
        flag_w = s * 0.38
        flag_h = s * 0.28
        self.create_polygon(
            [pole_x, pole_y_top, pole_x + flag_w, pole_y_top + flag_h / 2, pole_x, pole_y_top + flag_h],
            fill=self.theme["flag_fabric"],
            outline=""
        )
        # Sturdy Base
        base_w = s * 0.32
        self.create_line(pole_x - base_w / 2, pole_y_bot, pole_x + base_w / 2, pole_y_bot, fill=self.theme["flag_base"], width=2.5)

    def _draw_mine(self, x: int, y: int, s: int, is_exploded: bool = False):
        cx = x + s // 2
        cy = y + s // 2
        r = s * 0.28

        # If exploded, draw danger background aura
        if is_exploded:
            self.create_rectangle(x + 1, y + 1, x + s - 1, y + s - 1, fill="#dc2626", outline="")

        # Mine Spikes (8 radial spikes)
        spike_len = s * 0.38
        for angle_deg in (0, 45, 90, 135, 180, 225, 270, 315):
            rad = math.radians(angle_deg)
            sx = cx + spike_len * math.cos(rad)
            sy = cy + spike_len * math.sin(rad)
            self.create_line(cx, cy, sx, sy, fill=self.theme["mine_spike"], width=2.5)

        # Central Mine Sphere
        self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=self.theme["mine_body"], outline="")

        # Highlight Glint
        glint_r = r * 0.35
        gx = cx - r * 0.35
        gy = cy - r * 0.35
        self.create_oval(gx - glint_r, gy - glint_r, gx + glint_r, gy + glint_r, fill="#ffffff", outline="")

    def redraw(self):
        """Renders every cell in the grid."""
        self.delete("all")
        s = self.cell_size

        for r in range(self.board.rows):
            for c in range(self.board.cols):
                cell = self.board.grid[r][c]
                x1 = c * s
                y1 = r * s
                x2 = x1 + s
                y2 = y1 + s

                is_hovered = (self.hover_cell == (r, c))
                is_pressed = (self.pressed_cell == (r, c))
                is_hinted = (self.hint_cell == (r, c))

                if cell.is_revealed:
                    # Revealed Tile
                    bg = self.theme["tile_revealed"]
                    if cell.is_mine and cell.exploded:
                        bg = "#b91c1c"
                    self.create_rectangle(x1, y1, x2, y2, fill=bg, outline=self.theme["grid_line"], width=1)

                    if cell.is_mine:
                        self._draw_mine(x1, y1, s, is_exploded=cell.exploded)
                    elif cell.neighbor_mines > 0:
                        # Draw Number
                        num_color = self.theme["numbers"].get(cell.neighbor_mines, "#ffffff")
                        font_size = max(9, int(s * 0.48))
                        self.create_text(
                            (x1 + x2) // 2,
                            (y1 + y2) // 2,
                            text=str(cell.neighbor_mines),
                            fill=num_color,
                            font=("Helvetica", font_size, "bold")
                        )

                else:
                    # Hidden Tile
                    tile_bg = self.theme["tile_hidden"]
                    if is_pressed:
                        tile_bg = self.theme["tile_pressed"]
                    elif is_hovered:
                        tile_bg = self.theme["tile_hidden_hover"]

                    self.create_rectangle(x1, y1, x2, y2, fill=tile_bg, outline=self.theme["tile_border"], width=1)

                    # Subtle 3D Bevel highlight line
                    if not is_pressed:
                        self.create_line(x1 + 1, y1 + 1, x2 - 1, y1 + 1, fill="#ffffff", width=1)
                        self.create_line(x1 + 1, y1 + 1, x1 + 1, y2 - 1, fill="#ffffff", width=1)

                    # Markings (Flag, Question mark)
                    if cell.is_flagged:
                        self._draw_flag(x1, y1, s)
                        if cell.wrong_flag:
                            # False Flag Red X
                            self.create_line(x1 + 4, y1 + 4, x2 - 4, y2 - 4, fill="#dc2626", width=3)
                            self.create_line(x2 - 4, y1 + 4, x1 + 4, y2 - 4, fill="#dc2626", width=3)
                    elif cell.is_question:
                        font_size = max(10, int(s * 0.50))
                        self.create_text(
                            (x1 + x2) // 2,
                            (y1 + y2) // 2,
                            text="?",
                            fill=self.theme["question_mark"],
                            font=("Helvetica", font_size, "bold")
                        )

                # Hint Glowing Aura
                if is_hinted:
                    self.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, outline=self.theme["hint_highlight"], width=3)

        # Draw active confetti if game is won
        if self.confetti_active:
            self._render_confetti()

    # --- Victory Confetti FX ---

    def start_confetti(self):
        """Spawns 60 animated confetti particles celebrating victory."""
        self.confetti_particles = []
        width = self.board.cols * self.cell_size
        colors = ["#38bdf8", "#4ade80", "#f43f5e", "#fbbf24", "#c084fc", "#ffffff"]

        for _ in range(65):
            self.confetti_particles.append({
                "x": random.uniform(0, width),
                "y": random.uniform(-100, 0),
                "size": random.uniform(4, 9),
                "vy": random.uniform(2.5, 6.0),
                "vx": random.uniform(-1.5, 1.5),
                "color": random.choice(colors),
                "rotation": random.uniform(0, 360),
                "vrot": random.uniform(-6, 6)
            })

        self.confetti_active = True
        self._update_confetti_step()

    def _update_confetti_step(self):
        if not self.confetti_active:
            return

        height = self.board.rows * self.cell_size
        all_fallen = True

        for p in self.confetti_particles:
            p["y"] += p["vy"]
            p["x"] += p["vx"]
            p["rotation"] += p["vrot"]
            if p["y"] < height + 20:
                all_fallen = False

        self.redraw()

        if not all_fallen:
            self.after(25, self._update_confetti_step)
        else:
            self.confetti_active = False

    def _render_confetti(self):
        for p in self.confetti_particles:
            x, y, s = p["x"], p["y"], p["size"]
            rad = math.radians(p["rotation"])
            dx = math.cos(rad) * s
            dy = math.sin(rad) * s
            self.create_line(x - dx, y - dy, x + dx, y + dy, fill=p["color"], width=3)

    def stop_confetti(self):
        self.confetti_active = False
        self.confetti_particles = []
