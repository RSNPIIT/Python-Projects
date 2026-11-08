"""Main application window orchestrating navigation, themes, keyboard routing & views."""

from __future__ import annotations

import signal
import sys
import tkinter as tk
from typing import Dict, Optional

try:
    import termios as _termios
except ImportError:
    _termios = None

from . import __app_name__, __version__
from .theme import THEME_ORDER, THEMES, FontSet
from .views.converter_view import ConverterView
from .views.grapher_view import GrapherView
from .views.programmer_view import ProgrammerView
from .views.scientific_view import ScientificView
from .views.tools_view import ToolsView
from .widgets import RoundedButton, SegmentedBar


class PrismCalcApp(tk.Tk):
    """PRISM CALC — Scientific Calculator, Measuring Converter & Engineering Suite."""

    def __init__(self) -> None:
        super().__init__()
        self.theme_idx = 0
        self.theme_name = THEME_ORDER[self.theme_idx]
        self.palette: Dict[str, str] = THEMES[self.theme_name]

        self.title(f"{__app_name__}  ·  Scientific Calculator & Measuring Converter")
        self.configure(bg=self.palette["bg"])
        self.minsize(940, 640)
        self._center_window(1100, 720)

        self.fonts = FontSet()
        self.active_mode = "scientific"
        self._tty_fd: Optional[int] = None
        if _termios is not None:
            try:
                if sys.stdin and sys.stdin.isatty():
                    self._tty_fd = sys.stdin.fileno()
            except Exception:
                self._tty_fd = None

        self._build_shell()
        self.bind_all("<Key>", self._on_global_key)

        # Ignore terminal Ctrl+C / Ctrl+\ / Ctrl+Z signals while app is running
        for sig_name in ("SIGINT", "SIGQUIT", "SIGTSTP", "SIGBREAK"):
            sig = getattr(signal, sig_name, None)
            if sig is not None:
                try:
                    signal.signal(sig, signal.SIG_IGN)
                except (OSError, ValueError):
                    pass
        self.after(350, self._tty_flush_heartbeat)

        # Bring window cleanly to front & force initial layout pass on macOS
        self.update_idletasks()
        self.deiconify()
        self.lift()
        try:
            self.attributes("-topmost", True)
            self.after(150, lambda: self.attributes("-topmost", False))
        except Exception:
            pass
        self.focus_force()

        # macOS Dock click support
        try:
            self.createcommand("tk::mac::ReopenApplication", self.deiconify)
        except Exception:
            pass

    def report_callback_exception(self, exc, val, tb) -> None:
        """Prevent raw callback tracebacks from corrupting the stty-guarded terminal."""
        return

    def _tty_flush_heartbeat(self) -> None:
        """Periodically discard any unread terminal keystrokes (Ctrl+C/X/D, exit, quit)."""
        if self._tty_fd is not None and _termios is not None:
            try:
                _termios.tcflush(self._tty_fd, _termios.TCIFLUSH)
            except Exception:
                pass
        try:
            if self.winfo_exists():
                self.after(350, self._tty_flush_heartbeat)
        except Exception:
            pass

    def _center_window(self, w: int, h: int) -> None:
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(20, (sw - w) // 2)
        y = max(20, (sh - h) // 2 - 20)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_shell(self) -> None:
        p = self.palette
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Top Header Bar
        self.header = tk.Frame(self, bg=p["bg"], padx=18, pady=12)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(0, weight=0)
        self.header.grid_columnconfigure(1, weight=1)
        self.header.grid_columnconfigure(2, weight=0)

        # Brand Emblem + Title
        self.brand_frame = tk.Frame(self.header, bg=p["bg"])
        self.brand_frame.grid(row=0, column=0, sticky="w", padx=(0, 16))

        self.logo_canvas = tk.Canvas(
            self.brand_frame,
            width=34,
            height=34,
            bg=p["bg"],
            bd=0,
            highlightthickness=0,
        )
        self.logo_canvas.pack(side="left", padx=(0, 10))
        self._draw_prism_logo()

        self.title_stack = tk.Frame(self.brand_frame, bg=p["bg"])
        self.title_stack.pack(side="left")
        self.brand_lbl = tk.Label(
            self.title_stack,
            text="PRISM CALC",
            anchor="w",
            bg=p["bg"],
            fg=p["text"],
            font=self.fonts.ui(14, "bold"),
        )
        self.brand_lbl.pack(fill="x")
        self.sub_lbl = tk.Label(
            self.title_stack,
            text=f"Scientific · Converter · Suite  v{__version__}",
            anchor="w",
            bg=p["bg"],
            fg=p["text_muted"],
            font=self.fonts.ui(9),
        )
        self.sub_lbl.pack(fill="x")

        # Mode Navigation Bar
        self.nav_bar = SegmentedBar(
            self.header,
            [
                ("scientific", "Scientific"),
                ("converter", "Converter"),
                ("programmer", "Programmer"),
                ("grapher", "Grapher"),
                ("tools", "Math Tools"),
            ],
            selected="scientific",
            on_change=self.switch_mode,
            fonts=self.fonts,
            palette=p,
            parent_bg=p["bg"],
            height=38,
            font_size=11,
        )
        self.nav_bar.grid(row=0, column=1, sticky="ew", padx=8)

        # Theme Cycle Button (wide enough for full theme label)
        self.theme_btn = RoundedButton(
            self.header,
            f"◐  {self.theme_name}",
            command=self.cycle_theme,
            kind="ghost",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["bg"],
            width=192,
            height=38,
            radius=19,
            font_size=11,
        )
        self.theme_btn.grid(row=0, column=2, sticky="e", padx=(12, 0))

        # Content Stage
        self.stage = tk.Frame(self, bg=p["bg"], padx=18)
        self.stage.grid(row=1, column=0, sticky="nsew", pady=(0, 16))
        self.stage.grid_columnconfigure(0, weight=1)
        self.stage.grid_rowconfigure(0, weight=1)

        # Instantiate all 5 views so state persists across tab switches
        self.scientific_view = ScientificView(
            self.stage,
            fonts=self.fonts,
            palette=p,
            on_send_to_converter=self._handoff_to_converter,
        )
        self.converter_view = ConverterView(
            self.stage,
            fonts=self.fonts,
            palette=p,
            on_send_to_calc=self._handoff_to_scientific,
        )
        self.programmer_view = ProgrammerView(self.stage, fonts=self.fonts, palette=p)
        self.grapher_view = GrapherView(self.stage, fonts=self.fonts, palette=p)
        self.tools_view = ToolsView(self.stage, fonts=self.fonts, palette=p)

        self._views = {
            "scientific": self.scientific_view,
            "converter": self.converter_view,
            "programmer": self.programmer_view,
            "grapher": self.grapher_view,
            "tools": self.tools_view,
        }
        self.scientific_view.grid(row=0, column=0, sticky="nsew")

    def _draw_prism_logo(self) -> None:
        c = self.logo_canvas
        c.delete("all")
        p = self.palette
        c.configure(bg=p["bg"])
        c.create_polygon(17, 3, 31, 29, 3, 29, fill=p["accent"], outline="")
        c.create_polygon(17, 3, 31, 29, 17, 23, fill=p["secondary"], outline="")
        c.create_polygon(17, 23, 31, 29, 3, 29, fill=p["op_btn"], outline="")
        c.create_line(17, 3, 31, 29, 3, 29, 17, 3, fill=p["text"], width=1)

    def switch_mode(self, mode_key: str) -> None:
        if mode_key not in self._views or mode_key == self.active_mode:
            return
        self._views[self.active_mode].grid_forget()
        self.active_mode = mode_key
        self._views[mode_key].grid(row=0, column=0, sticky="nsew")
        self.nav_bar.set_selected(mode_key)
        if mode_key in ("scientific", "programmer"):
            self.focus_set()

    def _handoff_to_converter(self, val: float) -> None:
        self.converter_view.set_external_value(val)
        self.switch_mode("converter")

    def _handoff_to_scientific(self, val: float) -> None:
        self.scientific_view.insert_external_value(val)
        self.switch_mode("scientific")

    def cycle_theme(self) -> None:
        self.theme_idx = (self.theme_idx + 1) % len(THEME_ORDER)
        self.theme_name = THEME_ORDER[self.theme_idx]
        self.palette = THEMES[self.theme_name]
        p = self.palette

        self.configure(bg=p["bg"])
        self.header.configure(bg=p["bg"])
        self.brand_frame.configure(bg=p["bg"])
        self.title_stack.configure(bg=p["bg"])
        self.brand_lbl.configure(bg=p["bg"], fg=p["text"])
        self.sub_lbl.configure(bg=p["bg"], fg=p["text_muted"])
        self._draw_prism_logo()

        self.nav_bar.apply_theme(p, p["bg"])
        self.theme_btn.set_text(f"◐  {self.theme_name}")
        self.theme_btn.apply_theme(p, p["bg"])
        self.stage.configure(bg=p["bg"])

        for view in self._views.values():
            view.apply_theme(p)

    def _on_global_key(self, event: tk.Event) -> None:
        # Ignore Ctrl+C / Ctrl+X / Ctrl+D shortcuts
        if (event.state & 0x4) and event.keysym.lower() in ("c", "x", "d", "z", "q"):
            return

        # Quick mode switching with Cmd/Ctrl + 1..5
        if (event.state & 0x4) or (event.state & 0x8):
            shortcut_map = {
                "1": "scientific",
                "2": "converter",
                "3": "programmer",
                "4": "grapher",
                "5": "tools",
            }
            if event.keysym in shortcut_map:
                self.switch_mode(shortcut_map[event.keysym])
                return

        focused = self.focus_get()
        if isinstance(focused, tk.Entry):
            return

        if self.active_mode == "scientific":
            self.scientific_view.handle_key(event)
        elif self.active_mode == "programmer":
            self.programmer_view.handle_key(event)
