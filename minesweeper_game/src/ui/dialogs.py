"""
dialogs.py - Custom Board Setup, Statistics Records, and Victory Summary Modals.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Optional, Tuple


class CustomGameDialog(tk.Toplevel):
    """Modal dialog for defining custom rows, columns, and mine counts."""

    def __init__(self, parent, initial_rows: int = 16, initial_cols: int = 16, initial_mines: int = 40, on_apply: Optional[Callable[[int, int, int], None]] = None):
        super().__init__(parent)
        self.title("Custom Board Setup")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_apply = on_apply
        self.result: Optional[Tuple[int, int, int]] = None

        self.configure(bg="#0f172a", padx=24, pady=20)

        # Title Header
        lbl_title = tk.Label(self, text="CUSTOM MINEFIELD", font=("Helvetica", 14, "bold"), fg="#38bdf8", bg="#0f172a")
        lbl_title.grid(row=0, column=0, columnspan=2, pady=(0, 16))

        # Rows (Height)
        tk.Label(self, text="Rows (Height: 8 - 40):", font=("Helvetica", 11), fg="#e2e8f0", bg="#0f172a").grid(row=1, column=0, sticky="w", pady=6)
        self.spin_rows = tk.Spinbox(self, from_=8, to=40, width=8, font=("Helvetica", 11), justify="center")
        self.spin_rows.delete(0, "end")
        self.spin_rows.insert(0, str(initial_rows))
        self.spin_rows.grid(row=1, column=1, sticky="e", pady=6)

        # Columns (Width)
        tk.Label(self, text="Columns (Width: 8 - 50):", font=("Helvetica", 11), fg="#e2e8f0", bg="#0f172a").grid(row=2, column=0, sticky="w", pady=6)
        self.spin_cols = tk.Spinbox(self, from_=8, to=50, width=8, font=("Helvetica", 11), justify="center")
        self.spin_cols.delete(0, "end")
        self.spin_cols.insert(0, str(initial_cols))
        self.spin_cols.grid(row=2, column=1, sticky="e", pady=6)

        # Mines
        tk.Label(self, text="Mines (10 - 500):", font=("Helvetica", 11), fg="#e2e8f0", bg="#0f172a").grid(row=3, column=0, sticky="w", pady=6)
        self.spin_mines = tk.Spinbox(self, from_=10, to=500, width=8, font=("Helvetica", 11), justify="center")
        self.spin_mines.delete(0, "end")
        self.spin_mines.insert(0, str(initial_mines))
        self.spin_mines.grid(row=3, column=1, sticky="e", pady=6)

        # Action Buttons
        btn_frame = tk.Frame(self, bg="#0f172a")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))

        btn_ok = tk.Button(btn_frame, text="Generate Board", font=("Helvetica", 11, "bold"), bg="#38bdf8", fg="#0f172a", activebackground="#0284c7", padx=12, pady=6, command=self._validate_and_apply)
        btn_ok.pack(side="left", padx=6)

        btn_cancel = tk.Button(btn_frame, text="Cancel", font=("Helvetica", 11), bg="#334155", fg="#e2e8f0", activebackground="#475569", padx=12, pady=6, command=self.destroy)
        btn_cancel.pack(side="left", padx=6)

        # Center on parent window
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(0, px)}+{max(0, py)}")

    def _validate_and_apply(self):
        try:
            r = int(self.spin_rows.get())
            c = int(self.spin_cols.get())
            m = int(self.spin_mines.get())

            if not (8 <= r <= 50):
                messagebox.showerror("Invalid Dimensions", "Rows must be between 8 and 50.", parent=self)
                return
            if not (8 <= c <= 60):
                messagebox.showerror("Invalid Dimensions", "Columns must be between 8 and 60.", parent=self)
                return

            max_mines = (r * c) - 9  # Guarantee safe first click zone
            if m < 1 or m > max_mines:
                messagebox.showerror("Invalid Mine Count", f"Mines must be between 1 and {max_mines}.", parent=self)
                return

            self.result = (r, c, m)
            if self.on_apply:
                self.on_apply(r, c, m)
            self.destroy()

        except ValueError:
            messagebox.showerror("Format Error", "Please enter valid whole numbers.", parent=self)


class StatsDialog(tk.Toplevel):
    """Displays win-rate, streaks, and best clear times."""

    def __init__(self, parent, stats_manager):
        super().__init__(parent)
        self.title("Minesweeper Records & Statistics")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.stats = stats_manager
        self.configure(bg="#0f172a", padx=24, pady=20)

        lbl_title = tk.Label(self, text="CAREER TELEMETRY", font=("Helvetica", 14, "bold"), fg="#38bdf8", bg="#0f172a")
        lbl_title.pack(pady=(0, 16))

        # Table container
        table_frame = tk.Frame(self, bg="#1e293b", bd=1, relief="solid")
        table_frame.pack(fill="x", pady=8)

        # Header
        headers = ["Difficulty", "Best Time", "Played", "Won", "Win Rate", "Streak"]
        for col_idx, h in enumerate(headers):
            lbl = tk.Label(table_frame, text=h, font=("Helvetica", 10, "bold"), fg="#94a3b8", bg="#1e293b", padx=10, pady=6)
            lbl.grid(row=0, column=col_idx, sticky="w")

        # Rows
        presets = ["Beginner", "Intermediate", "Expert", "Master", "Custom"]
        for row_idx, diff in enumerate(presets, start=1):
            data = self.stats.get_stats(diff)
            best_time = f"{data.get('best_time', 0):.1f}s" if data.get("best_time") is not None else "--"
            played = data.get("played", 0)
            won = data.get("won", 0)
            win_rate = f"{(won / played * 100):.0f}%" if played > 0 else "0%"
            streak = f"{data.get('streak', 0)} (max {data.get('best_streak', 0)})"

            row_bg = "#0f172a" if row_idx % 2 == 0 else "#1e293b"

            vals = [diff, best_time, str(played), str(won), win_rate, streak]
            for col_idx, val in enumerate(vals):
                fg = "#38bdf8" if col_idx == 1 and val != "--" else "#e2e8f0"
                lbl = tk.Label(table_frame, text=val, font=("Helvetica", 10), fg=fg, bg=row_bg, padx=10, pady=5)
                lbl.grid(row=row_idx, column=col_idx, sticky="w")

        # Buttons
        btn_frame = tk.Frame(self, bg="#0f172a")
        btn_frame.pack(pady=(16, 0))

        btn_close = tk.Button(btn_frame, text="Close", font=("Helvetica", 11, "bold"), bg="#38bdf8", fg="#0f172a", padx=16, pady=4, command=self.destroy)
        btn_close.pack(side="left", padx=8)

        btn_reset = tk.Button(btn_frame, text="Reset Statistics", font=("Helvetica", 10), bg="#ef4444", fg="#ffffff", padx=10, pady=4, command=self._confirm_reset)
        btn_reset.pack(side="left", padx=8)

        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(0, px)}+{max(0, py)}")

    def _confirm_reset(self):
        if messagebox.askyesno("Reset Records", "Are you sure you want to erase all best times and game stats?", parent=self):
            self.stats.reset_stats()
            self.destroy()


class VictoryDialog(tk.Toplevel):
    """Celebratory modal summarizing victory metrics and 3BV score."""

    def __init__(self, parent, time_seconds: float, clicks: int, b_3bv: int, is_new_record: bool, diff_name: str, on_play_again: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.title("Victory!")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_play_again = on_play_again
        self.configure(bg="#0f172a", padx=28, pady=24)

        # Trophy & Banner
        lbl_trophy = tk.Label(self, text="🏆", font=("Helvetica", 36), bg="#0f172a")
        lbl_trophy.pack()

        lbl_win = tk.Label(self, text="MINEFIELD CLEARED!", font=("Helvetica", 16, "bold"), fg="#4ade80", bg="#0f172a")
        lbl_win.pack(pady=(4, 4))

        if is_new_record:
            lbl_rec = tk.Label(self, text="★ NEW PERSONAL BEST TIME! ★", font=("Helvetica", 11, "bold"), fg="#facc15", bg="#0f172a")
            lbl_rec.pack(pady=(0, 10))

        # Metrics Card
        card = tk.Frame(self, bg="#1e293b", bd=1, relief="solid", padx=16, pady=12)
        card.pack(fill="x", pady=8)

        # Efficiency calculation
        eff_3bv_s = (b_3bv / time_seconds) if time_seconds > 0 else 0.0

        stats_lines = [
            ("Difficulty", diff_name),
            ("Time Elapsed", f"{time_seconds:.2f} seconds"),
            ("Clicks Made", str(clicks)),
            ("3BV Benchmark", str(b_3bv)),
            ("3BV / Second", f"{eff_3bv_s:.2f}"),
        ]

        for idx, (label, val) in enumerate(stats_lines):
            tk.Label(card, text=label, font=("Helvetica", 10), fg="#94a3b8", bg="#1e293b").grid(row=idx, column=0, sticky="w", pady=3)
            tk.Label(card, text=val, font=("Helvetica", 10, "bold"), fg="#38bdf8", bg="#1e293b").grid(row=idx, column=1, sticky="e", padx=(24, 0), pady=3)

        # Buttons
        btn_frame = tk.Frame(self, bg="#0f172a")
        btn_frame.pack(pady=(16, 0))

        btn_play = tk.Button(btn_frame, text="Play Again", font=("Helvetica", 11, "bold"), bg="#38bdf8", fg="#0f172a", padx=14, pady=6, command=self._play_again)
        btn_play.pack(side="left", padx=8)

        btn_close = tk.Button(btn_frame, text="Close", font=("Helvetica", 11), bg="#334155", fg="#e2e8f0", padx=14, pady=6, command=self.destroy)
        btn_close.pack(side="left", padx=8)

        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(0, px)}+{max(0, py)}")

    def _play_again(self):
        self.destroy()
        if self.on_play_again:
            self.on_play_again()
