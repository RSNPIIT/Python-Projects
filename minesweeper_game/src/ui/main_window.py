"""
main_window.py - Top-Level Application Window Coordinator.
Integrates Board, ThemeManager, LCDDisplays, FaceButton, Solver, and SoundEngine.
"""

import os
import time
import tkinter as tk
from tkinter import messagebox
from typing import Optional

from ..core.board import Board
from ..core.cell import CellState
from ..core.game_state import Difficulty, GameMode, GameStats, GameStatus
from ..core.solver import Solver
from ..audio.sound_engine import SoundEngine
from .dialogs import CustomGameDialog, StatsDialog, VictoryDialog
from .face_button import FaceButton, FaceState
from .grid_canvas import GridCanvas
from .lcd_display import LCDDisplay
from .themes import THEMES


class MainWindow(tk.Tk):
    """Main window coordinator for Minesweeper OOP game."""

    def __init__(self):
        super().__init__()
        self.title("MINESWEEPER // TACTICAL EDITION")
        self.resizable(False, False)

        # Base Paths & Subsystems
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        asset_dir = os.path.join(base_dir, "assets")

        self.sound = SoundEngine(asset_dir)
        self.stats = GameStats()

        # State Variables
        self.current_theme_name = "Cyber Dark"
        self.theme = THEMES[self.current_theme_name]

        self.difficulty = Difficulty.BEGINNER
        self.custom_settings = (10, 10, 15)  # (r, c, m)
        self.game_mode = GameMode.CLASSIC

        self.shields_remaining = 0
        self.status = GameStatus.READY
        self.start_time: Optional[float] = None
        self.elapsed_time: float = 0.0
        self.clicks_count = 0
        self.timer_job = None

        # Instantiate Board
        self.board = Board(
            rows=self.difficulty.rows,
            cols=self.difficulty.cols,
            mines=self.difficulty.mines,
            safe_opening=True
        )

        # Build GUI
        self._setup_window_styling()
        self._build_menu()
        self._build_header_panel()
        self._build_board_panel()
        self._build_bottom_toolbar()

        # Global Hotkeys
        self.bind("<F2>", lambda e: self.start_new_game())
        self.bind("<r>", lambda e: self.start_new_game())
        self.bind("<R>", lambda e: self.start_new_game())
        self.bind("<h>", lambda e: self.trigger_hint())
        self.bind("<H>", lambda e: self.trigger_hint())
        self.bind("<m>", lambda e: self.toggle_sound())
        self.bind("<M>", lambda e: self.toggle_sound())
        self.bind("<p>", lambda e: self.toggle_pause())
        self.bind("<P>", lambda e: self.toggle_pause())
        self.bind("<Escape>", lambda e: self.grid_canvas.clear_hint())

        self.start_new_game()

    def _setup_window_styling(self):
        self.configure(bg=self.theme["bg_main"])

    def _build_menu(self):
        menubar = tk.Menu(self)

        # --- Game Menu ---
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="New Game (F2 / R)", command=self.start_new_game)
        game_menu.add_separator()
        game_menu.add_command(label="Beginner (9x9 - 10 Mines)", command=lambda: self.set_difficulty(Difficulty.BEGINNER))
        game_menu.add_command(label="Intermediate (16x16 - 40 Mines)", command=lambda: self.set_difficulty(Difficulty.INTERMEDIATE))
        game_menu.add_command(label="Expert (16x30 - 99 Mines)", command=lambda: self.set_difficulty(Difficulty.EXPERT))
        game_menu.add_command(label="Master (20x30 - 130 Mines)", command=lambda: self.set_difficulty(Difficulty.MASTER))
        game_menu.add_command(label="Custom Field...", command=self.open_custom_dialog)
        game_menu.add_separator()
        game_menu.add_command(label="Career Records & Stats", command=self.open_stats_dialog)
        game_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="Game", menu=game_menu)

        # --- Game Modes ---
        mode_menu = tk.Menu(menubar, tearoff=0)
        mode_menu.add_command(label="Classic Rules (1 Life)", command=lambda: self.set_mode(GameMode.CLASSIC))
        mode_menu.add_command(label="Shield Mode (+1 Defusal Shield)", command=lambda: self.set_mode(GameMode.SHIELD))
        menubar.add_cascade(label="Mode", menu=mode_menu)

        # --- Themes ---
        theme_menu = tk.Menu(menubar, tearoff=0)
        for t_name in THEMES.keys():
            theme_menu.add_command(label=t_name, command=lambda tn=t_name: self.switch_theme(tn))
        menubar.add_cascade(label="Themes", menu=theme_menu)

        # --- Assistance / Tools ---
        tool_menu = tk.Menu(menubar, tearoff=0)
        tool_menu.add_command(label="Smart Logical Hint (H)", command=self.trigger_hint)
        tool_menu.add_command(label="Toggle Audio (M)", command=self.toggle_sound)
        tool_menu.add_separator()
        tool_menu.add_command(label="Controls & Rules", command=self.show_help)
        menubar.add_cascade(label="Help", menu=tool_menu)

        self.config(menu=menubar)

    def _build_header_panel(self):
        """Dashboard containing Mine Counter LCD, Face Button, and Timer LCD."""
        self.header_frame = tk.Frame(
            self,
            bg=self.theme["bg_panel"],
            padx=14,
            pady=10,
            bd=1,
            relief="ridge"
        )
        self.header_frame.pack(fill="x", padx=10, pady=(10, 6))

        # 1. Left: Mines Remaining Counter
        self.lcd_mines = LCDDisplay(
            self.header_frame,
            value=self.board.total_mines,
            bg_color=self.theme["lcd_bg"],
            fg_color=self.theme["lcd_fg"],
            off_color=self.theme["lcd_off"]
        )
        self.lcd_mines.pack(side="left", padx=6)

        # 2. Center: Face Button Mascot
        self.face_btn = FaceButton(
            self.header_frame,
            command=self.start_new_game,
            size=42
        )
        self.face_btn.set_theme(self.theme["bg_panel"], self.theme["tile_border"])
        self.face_btn.pack(side="left", expand=True)

        # 3. Right: Elapsed Timer LCD
        self.lcd_timer = LCDDisplay(
            self.header_frame,
            value=0,
            bg_color=self.theme["lcd_bg"],
            fg_color=self.theme["lcd_fg"],
            off_color=self.theme["lcd_off"]
        )
        self.lcd_timer.pack(side="right", padx=6)

    def _build_board_panel(self):
        """Container for the interactive canvas."""
        self.board_container = tk.Frame(
            self,
            bg=self.theme["bg_main"],
            padx=10,
            pady=4
        )
        self.board_container.pack()

        # Canvas cell size: scales appropriately for large grids
        cell_size = 28 if self.board.cols > 25 else 32

        self.grid_canvas = GridCanvas(
            self.board_container,
            board=self.board,
            theme=self.theme,
            cell_size=cell_size,
            on_reveal=self.handle_reveal,
            on_flag=self.handle_flag,
            on_chord=self.handle_chord,
            on_suspense_start=lambda: self.face_btn.set_face_state(FaceState.SUSPENSE) if self.status in (GameStatus.READY, GameStatus.PLAYING) else None,
            on_suspense_end=lambda: self.face_btn.set_face_state(FaceState.NORMAL) if self.status in (GameStatus.READY, GameStatus.PLAYING) else None
        )
        self.grid_canvas.pack()

    def _build_bottom_toolbar(self):
        """Footer dashboard with mode badge, smart hint button, sound toggle."""
        self.footer_frame = tk.Frame(
            self,
            bg=self.theme["bg_main"],
            padx=12,
            pady=8
        )
        self.footer_frame.pack(fill="x")

        # Difficulty & Shield Badge
        self.lbl_badge = tk.Label(
            self.footer_frame,
            text=f"{self.difficulty.display_name.upper()} • {self.board.total_mines} MINES",
            font=("Helvetica", 9, "bold"),
            fg="#94a3b8",
            bg=self.theme["bg_main"]
        )
        self.lbl_badge.pack(side="left", padx=4)

        # Action Buttons
        self.btn_sound = tk.Button(
            self.footer_frame,
            text="🔊 SFX: ON",
            font=("Helvetica", 9),
            bg=self.theme["bg_panel"],
            fg="#e2e8f0",
            relief="flat",
            padx=8,
            pady=2,
            command=self.toggle_sound
        )
        self.btn_sound.pack(side="right", padx=4)

        self.btn_hint = tk.Button(
            self.footer_frame,
            text="💡 HINT (H)",
            font=("Helvetica", 9, "bold"),
            bg="#38bdf8",
            fg="#0f172a",
            activebackground="#0284c7",
            relief="flat",
            padx=10,
            pady=2,
            command=self.trigger_hint
        )
        self.btn_hint.pack(side="right", padx=6)

        # Shield indicator if active
        self.lbl_shield = tk.Label(
            self.footer_frame,
            text="",
            font=("Helvetica", 9, "bold"),
            fg="#38bdf8",
            bg=self.theme["bg_main"]
        )
        self.lbl_shield.pack(side="right", padx=8)

    # --- Game Loop & Logic Handlers ---

    def start_new_game(self):
        """Resets board, timer, face, and statistics for a fresh round."""
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None

        if self.difficulty == Difficulty.CUSTOM:
            r, c, m = self.custom_settings
            self.board.reset(rows=r, cols=c, mines=m)
        else:
            self.board.reset(
                rows=self.difficulty.rows,
                cols=self.difficulty.cols,
                mines=self.difficulty.mines
            )

        self.status = GameStatus.READY
        self.start_time = None
        self.elapsed_time = 0.0
        self.clicks_count = 0
        self.shields_remaining = 1 if self.game_mode == GameMode.SHIELD else 0

        # UI Reset
        self.face_btn.set_face_state(FaceState.NORMAL)
        self.lcd_mines.set_value(self.board.remaining_mines)
        self.lcd_timer.set_value(0)
        self.grid_canvas.stop_confetti()
        self.grid_canvas.clear_hint()

        # Update sizing
        cell_size = 28 if self.board.cols > 25 else 32
        self.grid_canvas.cell_size = cell_size
        self.grid_canvas.update_dimensions()

        self._update_badges()
        self.sound.play("click")

    def _update_badges(self):
        mode_str = f" • [{self.game_mode.value.upper()}]" if self.game_mode != GameMode.CLASSIC else ""
        self.lbl_badge.configure(text=f"{self.difficulty.display_name.upper()}{mode_str} • {self.board.total_mines} MINES")

        if self.game_mode == GameMode.SHIELD:
            self.lbl_shield.configure(text=f"🛡️ SHIELD: {'READY' if self.shields_remaining > 0 else 'DEPLETED'}")
        else:
            self.lbl_shield.configure(text="")

    def _start_timer_if_needed(self):
        if self.status == GameStatus.READY:
            self.status = GameStatus.PLAYING
            self.start_time = time.time()
            self._timer_tick()

    def _timer_tick(self):
        if self.status == GameStatus.PLAYING and self.start_time is not None:
            self.elapsed_time = time.time() - self.start_time
            display_sec = min(999, int(self.elapsed_time))
            self.lcd_timer.set_value(display_sec)
            self.timer_job = self.after(200, self._timer_tick)

    def handle_reveal(self, row: int, col: int):
        if self.status in (GameStatus.WON, GameStatus.LOST, GameStatus.PAUSED):
            return

        self._start_timer_if_needed()
        self.clicks_count += 1
        self.grid_canvas.clear_hint()

        hit_mine, revealed = self.board.reveal_cell(row, col)

        if hit_mine:
            # Check shield protection
            if self.shields_remaining > 0:
                self.shields_remaining -= 0
                self.shields_remaining = 0
                cell = self.board.get_cell(row, col)
                if cell:
                    cell.is_mine = False  # Neutralize defused mine
                    cell.shield_saved = True
                    cell.neighbor_mines = sum(1 for n in self.board.get_neighbors(row, col) if n.is_mine)
                    self.sound.play("shield")
                    self.face_btn.set_face_state(FaceState.SHIELD)
                    self._update_badges()
                    self.grid_canvas.redraw()
                    return

            # Defeat
            self._handle_defeat()
            return

        if len(revealed) > 1:
            self.sound.play("cascade")
        else:
            self.sound.play("click")

        # Check Win
        if self.board.check_win():
            self._handle_victory()
        else:
            self.grid_canvas.redraw()

    def handle_flag(self, row: int, col: int):
        if self.status in (GameStatus.WON, GameStatus.LOST, GameStatus.PAUSED):
            return

        cell = self.board.get_cell(row, col)
        if not cell or cell.is_revealed:
            return

        new_state = cell.toggle_flag(allow_question=True)
        if new_state == CellState.FLAGGED:
            self.sound.play("flag")
        else:
            self.sound.play("unflag")

        self.lcd_mines.set_value(self.board.remaining_mines)
        self.grid_canvas.redraw()

    def handle_chord(self, row: int, col: int):
        if self.status in (GameStatus.WON, GameStatus.LOST, GameStatus.PAUSED):
            return

        self._start_timer_if_needed()
        self.clicks_count += 1

        hit_mine, revealed = self.board.chord(row, col)

        if hit_mine:
            # Check shield
            if self.shields_remaining > 0:
                self.shields_remaining = 0
                self.sound.play("shield")
                self.face_btn.set_face_state(FaceState.SHIELD)
                self._update_badges()
                self.grid_canvas.redraw()
                return

            self._handle_defeat()
            return

        if revealed:
            self.sound.play("chord")

        if self.board.check_win():
            self._handle_victory()
        else:
            self.grid_canvas.redraw()

    def _handle_defeat(self):
        self.status = GameStatus.LOST
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None

        self.board.reveal_all_on_loss()
        self.face_btn.set_face_state(FaceState.LOST)
        self.sound.play("explode")
        self.stats.record_game(self.difficulty.display_name, False, self.elapsed_time)
        self.grid_canvas.redraw()

    def _handle_victory(self):
        self.status = GameStatus.WON
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None

        self.board.auto_flag_all_mines()
        self.lcd_mines.set_value(0)
        self.face_btn.set_face_state(FaceState.WON)
        self.sound.play("win")

        b_3bv = self.board.calculate_3bv()
        is_new_best, _ = self.stats.record_game(self.difficulty.display_name, True, self.elapsed_time)

        self.grid_canvas.start_confetti()

        # Show celebration modal
        self.after(600, lambda: VictoryDialog(
            self,
            time_seconds=self.elapsed_time,
            clicks=self.clicks_count,
            b_3bv=b_3bv,
            is_new_record=is_new_best,
            diff_name=self.difficulty.display_name,
            on_play_again=self.start_new_game
        ))

    # --- Tool Actions ---

    def trigger_hint(self):
        """Computes logical safe move or mine deduction and displays explanation."""
        if self.status in (GameStatus.WON, GameStatus.LOST):
            return

        hint = Solver.get_hint(self.board)
        if hint:
            self.grid_canvas.set_hint(hint.row, hint.col)
            action_type = "SAFE TILE" if hint.is_safe else "MINE IDENTIFIED"
            messagebox.showinfo(
                f"Tactical Hint [{action_type}]",
                f"Target Tile: Row {hint.row + 1}, Col {hint.col + 1}\n\n{hint.explanation}",
                parent=self
            )
        else:
            messagebox.showinfo("Hint", "All available tiles require guessing; no deterministic deduction found.", parent=self)

    def toggle_sound(self):
        active = self.sound.toggle_sound()
        self.btn_sound.configure(text="🔊 SFX: ON" if active else "🔇 SFX: OFF")

    def toggle_pause(self):
        if self.status == GameStatus.PLAYING:
            self.status = GameStatus.PAUSED
            if self.timer_job:
                self.after_cancel(self.timer_job)
                self.timer_job = None
            messagebox.showinfo("Game Paused", "Game is paused. Press OK to resume.", parent=self)
            self.status = GameStatus.PLAYING
            self._timer_tick()

    def set_difficulty(self, diff: Difficulty):
        self.difficulty = diff
        self.start_new_game()

    def set_mode(self, mode: GameMode):
        self.game_mode = mode
        self.start_new_game()

    def switch_theme(self, theme_name: str):
        if theme_name in THEMES:
            self.current_theme_name = theme_name
            self.theme = THEMES[theme_name]

            # Apply colors to widgets
            self.configure(bg=self.theme["bg_main"])
            self.header_frame.configure(bg=self.theme["bg_panel"])
            self.board_container.configure(bg=self.theme["bg_main"])
            self.footer_frame.configure(bg=self.theme["bg_main"])
            self.lbl_badge.configure(bg=self.theme["bg_main"])
            self.lbl_shield.configure(bg=self.theme["bg_main"])

            self.lcd_mines.set_theme(self.theme["lcd_bg"], self.theme["lcd_fg"], self.theme["lcd_off"])
            self.lcd_timer.set_theme(self.theme["lcd_bg"], self.theme["lcd_fg"], self.theme["lcd_off"])
            self.face_btn.set_theme(self.theme["bg_panel"], self.theme["tile_border"])
            self.btn_sound.configure(bg=self.theme["bg_panel"])

            self.grid_canvas.set_theme(self.theme)

    def open_custom_dialog(self):
        def _apply_custom(r, c, m):
            self.custom_settings = (r, c, m)
            self.difficulty = Difficulty.CUSTOM
            self.start_new_game()

        CustomGameDialog(
            self,
            initial_rows=self.custom_settings[0],
            initial_cols=self.custom_settings[1],
            initial_mines=self.custom_settings[2],
            on_apply=_apply_custom
        )

    def open_stats_dialog(self):
        StatsDialog(self, self.stats)

    def show_help(self):
        msg = (
            "MINESWEEPER CONTROLS & TACTICS\n\n"
            "• Left Click: Probe & Reveal hidden tile\n"
            "• Right Click / Two-Finger Tap: Place Flag (🚩) or Question (❓)\n"
            "• Double Click / Middle Click: Chord revealed number (reveals neighbors if flags match)\n"
            "• F2 / R / Mascot Button: New Game\n"
            "• H Key: Smart Logical Hint (zero guessing deduction)\n"
            "• M Key: Toggle 8-bit Sound Effects\n"
            "• P Key: Pause / Resume timer\n\n"
            "FIRST CLICK GUARANTEE:\n"
            "The initial click is mathematically guaranteed safe and will always trigger an opening cascade."
        )
        messagebox.showinfo("Minesweeper Guide", msg, parent=self)
