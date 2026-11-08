"""Interactive 2D Function Grapher with pan/zoom, crosshair tracer & definite integral."""

from __future__ import annotations

import math
import tkinter as tk
from typing import Dict, List, Optional, Tuple

from ..evaluator import CalcError, build_functions, format_number, tokenize, _Parser, CONSTANTS_MAP
from ..theme import FontSet, blend_hex
from ..widgets import RoundedButton, RoundedCard, StyledEntry


class _CompiledFunc:
    """Pre-tokenized expression for fast 400-point curve sampling."""

    def __init__(self, expr: str) -> None:
        self.funcs = build_functions("RAD")
        self.tokens = tokenize(expr, set(self.funcs.keys()))
        self.base_vars = dict(CONSTANTS_MAP)

    def __call__(self, x: float) -> Optional[float]:
        v = dict(self.base_vars)
        v["x"] = x
        v["X"] = x
        try:
            res = _Parser(self.tokens, self.funcs, v).parse()
            if math.isnan(res) or math.isinf(res):
                return None
            return res
        except CalcError:
            return None


class GrapherView(tk.Frame):
    """Multi-curve 2D function plotter with live hover tracer & Simpson integration."""

    def __init__(self, parent: tk.Widget, *, fonts: FontSet, palette: Dict[str, str]) -> None:
        super().__init__(parent, bg=palette["bg"], bd=0, highlightthickness=0)
        self.fonts = fonts
        self.palette = palette

        # Viewport in math coordinates
        self.x_min: float = -10.0
        self.x_max: float = 10.0
        self.y_min: float = -6.5
        self.y_max: float = 6.5

        self._drag_last: Optional[Tuple[int, int]] = None
        self._hover_px: Optional[Tuple[int, int]] = None
        self._compiled: List[Optional[_CompiledFunc]] = [None, None, None]
        self._shade_bounds: Optional[Tuple[float, float]] = None

        self._buttons: List[Tuple[RoundedButton, str]] = []
        self._entries: List[Tuple[StyledEntry, str]] = []

        self._build_ui()
        self._compile_and_draw()

    def _build_ui(self) -> None:
        p = self.palette
        self.grid_columnconfigure(0, weight=0, minsize=296)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Controls & Calculus Inspector Card
        self.ctrl_card = RoundedCard(
            self,
            palette=p,
            parent_bg=p["bg"],
            fill_key="surface",
            border_key="card_border",
            radius=16,
            pad_x=14,
            pad_y=12,
        )
        self.ctrl_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        cb = self.ctrl_card.body
        cb.grid_columnconfigure(0, weight=1)

        self.fn_hdr = tk.Label(
            cb,
            text="FUNCTIONS  (variable x, radians)",
            anchor="w",
            bg=p["surface"],
            fg=p["text_sub"],
            font=self.fonts.ui(10, "bold"),
        )
        self.fn_hdr.pack(fill="x", pady=(0, 6))

        defaults = ["sin(x) * cos(0.5*x)", "0.15*x^2 - 2", ""]
        labels = [("f(x) =", "plot_1"), ("g(x) =", "plot_2"), ("h(x) =", "plot_3")]
        self.fn_entries: List[StyledEntry] = []
        self.fn_badges: List[Tuple[tk.Frame, tk.Label]] = []

        for idx, ((lbl_txt, col_key), dflt) in enumerate(zip(labels, defaults)):
            row = tk.Frame(cb, bg=p["surface"])
            row.pack(fill="x", pady=3)
            tag = tk.Label(
                row,
                text=lbl_txt,
                width=5,
                anchor="w",
                bg=p["surface"],
                fg=p[col_key],
                font=self.fonts.mono(11, "bold"),
            )
            tag.pack(side="left")
            ent = StyledEntry(
                row,
                fonts=self.fonts,
                palette=p,
                parent_bg=p["surface"],
                initial=dflt,
                font_size=12,
                mono=True,
                height=36,
                on_change=lambda _s: self._compile_and_draw(),
            )
            ent.pack(side="left", fill="x", expand=True)
            self.fn_entries.append(ent)
            self.fn_badges.append((row, tag))
            self._entries.append((ent, "surface"))

        # Presets row
        self.preset_hdr = tk.Label(
            cb,
            text="PRESET CURVES",
            anchor="w",
            bg=p["surface"],
            fg=p["text_muted"],
            font=self.fonts.ui(9, "bold"),
        )
        self.preset_hdr.pack(fill="x", pady=(10, 4))

        self.preset_row = tk.Frame(cb, bg=p["surface"])
        self.preset_row.pack(fill="x")
        presets = [
            ("Waves", ("sin(x)", "cos(2*x)", "")),
            ("Cubic", ("0.1*x^3 - 0.8*x", "0.5*x", "")),
            ("Bell", ("4*exp(-0.25*x^2)", "cos(x)", "")),
            ("Asymp", ("tan(0.5*x)", "2/x", "")),
        ]
        for pname, ptuple in presets:
            b = RoundedButton(
                self.preset_row,
                pname,
                command=lambda tup=ptuple: self._load_preset(tup),
                kind="fn",
                fonts=self.fonts,
                palette=p,
                parent_bg=p["surface"],
                width=60,
                height=30,
                radius=8,
                font_size=10,
            )
            b.pack(side="left", expand=True, fill="x", padx=2)
            self._buttons.append((b, "surface"))

        # Viewport Zoom / Reset Row
        self.zoom_row = tk.Frame(cb, bg=p["surface"])
        self.zoom_row.pack(fill="x", pady=(10, 8))
        for zlbl, zcmd in (
            ("Zoom +", lambda: self._zoom(0.75)),
            ("Zoom −", lambda: self._zoom(1.3333)),
            ("Reset View", self._reset_view),
        ):
            zb = RoundedButton(
                self.zoom_row,
                zlbl,
                command=zcmd,
                kind="op" if "Reset" not in zlbl else "ghost",
                fonts=self.fonts,
                palette=p,
                parent_bg=p["surface"],
                width=74,
                height=32,
                radius=8,
                font_size=10,
            )
            zb.pack(side="left", expand=True, fill="x", padx=2)
            self._buttons.append((zb, "surface"))

        # Calculus Inspector for f(x)
        self.calc_hdr = tk.Label(
            cb,
            text="CALCULUS INSPECTOR ON f(x)",
            anchor="w",
            bg=p["surface"],
            fg=p["text_sub"],
            font=self.fonts.ui(10, "bold"),
        )
        self.calc_hdr.pack(fill="x", pady=(8, 4))

        self.x0_row = tk.Frame(cb, bg=p["surface"])
        self.x0_row.pack(fill="x", pady=2)
        self.x0_lbl = tk.Label(self.x0_row, text="At x₀ =", bg=p["surface"], fg=p["text_sub"], font=self.fonts.mono(10))
        self.x0_lbl.pack(side="left", padx=(0, 6))
        self.x0_entry = StyledEntry(
            self.x0_row,
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            initial="1.0",
            font_size=11,
            height=32,
            on_change=lambda _s: self._update_calculus(),
        )
        self.x0_entry.pack(side="left", fill="x", expand=True)
        self._entries.append((self.x0_entry, "surface"))

        self.ab_row = tk.Frame(cb, bg=p["surface"])
        self.ab_row.pack(fill="x", pady=3)
        self.a_lbl = tk.Label(self.ab_row, text="∫ a..b:", bg=p["surface"], fg=p["text_sub"], font=self.fonts.mono(10))
        self.a_lbl.pack(side="left", padx=(0, 6))
        self.int_a = StyledEntry(
            self.ab_row,
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            initial="0",
            font_size=11,
            height=32,
            on_change=lambda _s: self._update_calculus(),
        )
        self.int_a.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.int_b = StyledEntry(
            self.ab_row,
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            initial="3.14159",
            font_size=11,
            height=32,
            on_change=lambda _s: self._update_calculus(),
        )
        self.int_b.pack(side="left", fill="x", expand=True)
        self._entries.append((self.int_a, "surface"))
        self._entries.append((self.int_b, "surface"))

        self.shade_btn = RoundedButton(
            cb,
            "Shade Definite Integral ∫ f(x) dx",
            command=self._toggle_shade,
            kind="secondary",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            height=32,
            radius=8,
            font_size=10,
        )
        self.shade_btn.pack(fill="x", pady=(4, 6))
        self._buttons.append((self.shade_btn, "surface"))

        self.calc_out = tk.Label(
            cb,
            text="",
            justify="left",
            anchor="nw",
            bg=p["display_bg"],
            fg=p["text"],
            font=self.fonts.mono(10),
            padx=10,
            pady=8,
        )
        self.calc_out.pack(fill="both", expand=True, pady=(2, 0))

        # Right Plot Canvas Card
        self.plot_card = RoundedCard(
            self,
            palette=p,
            parent_bg=p["bg"],
            fill_key="display_bg",
            border_key="display_border",
            radius=16,
            pad_x=8,
            pad_y=8,
        )
        self.plot_card.grid(row=0, column=1, sticky="nsew")
        pb = self.plot_card.body
        pb.grid_columnconfigure(0, weight=1)
        pb.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(pb, bg=p["display_bg"], bd=0, highlightthickness=0, cursor="crosshair")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas.bind("<Configure>", lambda _e: self._redraw_plot())
        self.canvas.bind("<ButtonPress-1>", self._on_pan_start)
        self.canvas.bind("<B1-Motion>", self._on_pan_move)
        self.canvas.bind("<ButtonRelease-1>", lambda _e: setattr(self, "_drag_last", None))
        self.canvas.bind("<Motion>", self._on_hover)
        self.canvas.bind("<Leave>", self._on_leave_canvas)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", lambda e: self._zoom_at(0.85, e.x, e.y))
        self.canvas.bind("<Button-5>", lambda e: self._zoom_at(1.18, e.x, e.y))

    # ------------------------------------------------------------------
    # Coordinate transforms & Calculus
    # ------------------------------------------------------------------
    def _to_px(self, x: float, y: float, w: int, h: int) -> Tuple[float, float]:
        px = (x - self.x_min) / (self.x_max - self.x_min) * w
        py = h - (y - self.y_min) / (self.y_max - self.y_min) * h
        return px, py

    def _to_math(self, px: float, py: float, w: int, h: int) -> Tuple[float, float]:
        x = self.x_min + (px / max(1, w)) * (self.x_max - self.x_min)
        y = self.y_min + ((h - py) / max(1, h)) * (self.y_max - self.y_min)
        return x, y

    def _nice_step(self, span: float) -> float:
        raw = max(1e-9, span / 8.0)
        exp = math.floor(math.log10(raw))
        frac = raw / (10.0 ** exp)
        if frac < 1.5:
            nice = 1.0
        elif frac < 3.5:
            nice = 2.0
        elif frac < 7.5:
            nice = 5.0
        else:
            nice = 10.0
        return nice * (10.0 ** exp)

    def _load_preset(self, exprs: Tuple[str, str, str]) -> None:
        for ent, ex in zip(self.fn_entries, exprs):
            ent.set(ex)
        self._compile_and_draw()

    def _reset_view(self) -> None:
        self.x_min, self.x_max = -10.0, 10.0
        self.y_min, self.y_max = -6.5, 6.5
        self._redraw_plot()

    def _zoom(self, factor: float) -> None:
        cx = 0.5 * (self.x_min + self.x_max)
        cy = 0.5 * (self.y_min + self.y_max)
        hx = max(1e-5, min(1e6, 0.5 * (self.x_max - self.x_min) * factor))
        hy = max(1e-5, min(1e6, 0.5 * (self.y_max - self.y_min) * factor))
        self.x_min, self.x_max = cx - hx, cx + hx
        self.y_min, self.y_max = cy - hy, cy + hy
        self._redraw_plot()

    def _zoom_at(self, factor: float, px: int, py: int) -> None:
        w = max(10, self.canvas.winfo_width())
        h = max(10, self.canvas.winfo_height())
        mx, my = self._to_math(px, py, w, h)
        self.x_min = mx + (self.x_min - mx) * factor
        self.x_max = mx + (self.x_max - mx) * factor
        self.y_min = my + (self.y_min - my) * factor
        self.y_max = my + (self.y_max - my) * factor
        self._redraw_plot()

    def _on_wheel(self, event: tk.Event) -> None:
        factor = 0.85 if event.delta > 0 else 1.18
        self._zoom_at(factor, event.x, event.y)

    def _on_pan_start(self, event: tk.Event) -> None:
        self._drag_last = (event.x, event.y)

    def _on_pan_move(self, event: tk.Event) -> None:
        if self._drag_last is None:
            return
        w = max(10, self.canvas.winfo_width())
        h = max(10, self.canvas.winfo_height())
        dx_px = event.x - self._drag_last[0]
        dy_px = event.y - self._drag_last[1]
        self._drag_last = (event.x, event.y)

        dx = -dx_px / w * (self.x_max - self.x_min)
        dy = dy_px / h * (self.y_max - self.y_min)
        self.x_min += dx
        self.x_max += dx
        self.y_min += dy
        self.y_max += dy
        self._redraw_plot()

    def _on_hover(self, event: tk.Event) -> None:
        self._hover_px = (event.x, event.y)
        self._redraw_plot()

    def _on_leave_canvas(self, _e: tk.Event) -> None:
        self._hover_px = None
        self._redraw_plot()

    def _toggle_shade(self) -> None:
        if self._shade_bounds is not None:
            self._shade_bounds = None
            self.shade_btn.set_active(False)
        else:
            self.shade_btn.set_active(True)
            self._update_calculus()
        self._redraw_plot()

    def _compile_and_draw(self) -> None:
        for i, ent in enumerate(self.fn_entries):
            raw = ent.get().strip()
            if not raw:
                self._compiled[i] = None
                continue
            try:
                self._compiled[i] = _CompiledFunc(raw)
            except CalcError:
                self._compiled[i] = None
        self._update_calculus()
        self._redraw_plot()

    def _update_calculus(self) -> None:
        f = self._compiled[0]
        if f is None:
            self.calc_out.configure(text="Enter f(x) above to inspect\nf(x₀), derivative f'(x₀),\nand definite integral.")
            return

        lines: List[str] = []
        try:
            x0 = float(self.x0_entry.get().strip())
            y0 = f(x0)
            h_step = 1e-6 * max(1.0, abs(x0))
            yp, ym = f(x0 + h_step), f(x0 - h_step)
            deriv = ((yp - ym) / (2.0 * h_step)) if (yp is not None and ym is not None) else None
            lines.append(f"f({format_number(x0, precision=5)})  = {format_number(y0, precision=8) if y0 is not None else 'undef'}")
            lines.append(f"f'({format_number(x0, precision=5)}) = {format_number(deriv, precision=8) if deriv is not None else 'undef'}")
        except ValueError:
            lines.append("x₀: enter valid number")

        try:
            a = float(self.int_a.get().strip())
            b = float(self.int_b.get().strip())
            if self.shade_btn.active:
                self._shade_bounds = (a, b)
            # Composite Simpson's rule (N=200)
            n = 200
            step = (b - a) / n
            acc = 0.0
            valid = True
            for i in range(n + 1):
                yv = f(a + i * step)
                if yv is None:
                    valid = False
                    break
                w = 1 if (i == 0 or i == n) else (4 if i % 2 == 1 else 2)
                acc += w * yv
            integral_val = (step / 3.0) * acc if valid else None
            lines.append(f"∫[{format_number(a, precision=4)}..{format_number(b, precision=4)}] = {format_number(integral_val, precision=8) if integral_val is not None else 'undef'}")
        except ValueError:
            lines.append("∫ a..b: enter valid bounds")

        self.calc_out.configure(text="\n".join(lines))
        if self.shade_btn.active:
            self._redraw_plot()

    def _redraw_plot(self) -> None:
        c = self.canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 30 or h < 30:
            return
        p = self.palette

        # Gridlines
        step_x = self._nice_step(self.x_max - self.x_min)
        step_y = self._nice_step(self.y_max - self.y_min)

        gx = math.floor(self.x_min / step_x) * step_x
        while gx <= self.x_max:
            px, _ = self._to_px(gx, 0.0, w, h)
            c.create_line(px, 0, px, h, fill=p["grid_major"])
            if abs(gx) > step_x * 1e-4:
                _, ay = self._to_px(0.0, 0.0, w, h)
                lbl_y = min(h - 12, max(12, ay + 12))
                c.create_text(px, lbl_y, text=f"{gx:g}", fill=p["text_muted"], font=self.fonts.mono(9))
            gx += step_x

        gy = math.floor(self.y_min / step_y) * step_y
        while gy <= self.y_max:
            _, py = self._to_px(0.0, gy, w, h)
            c.create_line(0, py, w, py, fill=p["grid_major"])
            if abs(gy) > step_y * 1e-4:
                ax, _ = self._to_px(0.0, 0.0, w, h)
                lbl_x = min(w - 22, max(22, ax - 16))
                c.create_text(lbl_x, py, text=f"{gy:g}", fill=p["text_muted"], font=self.fonts.mono(9))
            gy += step_y

        # Primary axes
        ax, ay = self._to_px(0.0, 0.0, w, h)
        if 0 <= ax <= w:
            c.create_line(ax, 0, ax, h, fill=p["axis"], width=2)
        if 0 <= ay <= h:
            c.create_line(0, ay, w, ay, fill=p["axis"], width=2)

        # Optional shaded definite integral under f(x)
        if self._shade_bounds is not None and self._compiled[0] is not None:
            a, b = sorted(self._shade_bounds)
            f0 = self._compiled[0]
            lo = max(a, self.x_min)
            hi = min(b, self.x_max)
            if hi > lo:
                steps = 90
                poly: List[float] = []
                p_start_x, p_zero_y = self._to_px(lo, 0.0, w, h)
                poly.extend([p_start_x, p_zero_y])
                ok = True
                for i in range(steps + 1):
                    xv = lo + (hi - lo) * (i / steps)
                    yv = f0(xv)
                    if yv is None:
                        ok = False
                        break
                    px, py = self._to_px(xv, yv, w, h)
                    poly.extend([px, max(-200.0, min(h + 200.0, py))])
                p_end_x, _ = self._to_px(hi, 0.0, w, h)
                poly.extend([p_end_x, p_zero_y])
                if ok and len(poly) >= 6:
                    shade_col = blend_hex(p["display_bg"], p["plot_1"], 0.28)
                    c.create_polygon(poly, fill=shade_col, outline=p["plot_1"], width=1)

        # Curves
        colors = [p["plot_1"], p["plot_2"], p["plot_3"]]
        samples = max(280, min(650, w))
        y_span = max(1e-9, self.y_max - self.y_min)

        for fn, col in zip(self._compiled, colors):
            if fn is None:
                continue
            segment: List[float] = []
            prev_y: Optional[float] = None
            for s in range(samples + 1):
                xv = self.x_min + (self.x_max - self.x_min) * (s / samples)
                yv = fn(xv)
                if yv is None or abs(yv - self.y_min) > y_span * 25 and abs(yv - self.y_max) > y_span * 25:
                    if len(segment) >= 4:
                        c.create_line(*segment, fill=col, width=2, smooth=False)
                    segment = []
                    prev_y = None
                    continue
                # Break across vertical asymptote jumps
                if prev_y is not None and abs(yv - prev_y) > y_span * 1.6:
                    if len(segment) >= 4:
                        c.create_line(*segment, fill=col, width=2, smooth=False)
                    segment = []
                px, py = self._to_px(xv, yv, w, h)
                segment.extend([px, py])
                prev_y = yv
            if len(segment) >= 4:
                c.create_line(*segment, fill=col, width=2, smooth=False)

        # Hover crosshair & snapped function values
        if self._hover_px is not None:
            hx, hy = self._hover_px
            mx, my = self._to_math(hx, hy, w, h)
            c.create_line(hx, 0, hx, h, fill=p["card_border"], dash=(4, 4))
            c.create_line(0, hy, w, hy, fill=p["card_border"], dash=(4, 4))

            readouts = [f"x = {mx:.4g},  y = {my:.4g}"]
            names = ["f", "g", "h"]
            for nm, fn, col in zip(names, self._compiled, colors):
                if fn is None:
                    continue
                yv = fn(mx)
                if yv is not None:
                    _, cy = self._to_px(mx, yv, w, h)
                    if 0 <= cy <= h:
                        c.create_oval(hx - 4, cy - 4, hx + 4, cy + 4, fill=col, outline=p["display_bg"], width=2)
                    readouts.append(f"{nm}(x) = {yv:.5g}")

            c.create_text(
                w - 12,
                12,
                text="   ·   ".join(readouts),
                anchor="ne",
                fill=p["text"],
                font=self.fonts.mono(10, "bold"),
            )
        else:
            c.create_text(
                w - 12,
                12,
                text="Drag to pan  ·  Scroll to zoom  ·  Hover to trace",
                anchor="ne",
                fill=p["text_muted"],
                font=self.fonts.ui(10),
            )

    def apply_theme(self, palette: Dict[str, str]) -> None:
        self.palette = palette
        p = palette
        self.configure(bg=p["bg"])
        self.ctrl_card.apply_theme(p, p["bg"])
        self.fn_hdr.configure(bg=p["surface"], fg=p["text_sub"])
        self.preset_hdr.configure(bg=p["surface"], fg=p["text_muted"])
        self.preset_row.configure(bg=p["surface"])
        self.zoom_row.configure(bg=p["surface"])
        self.calc_hdr.configure(bg=p["surface"], fg=p["text_sub"])
        self.x0_row.configure(bg=p["surface"])
        self.x0_lbl.configure(bg=p["surface"], fg=p["text_sub"])
        self.ab_row.configure(bg=p["surface"])
        self.a_lbl.configure(bg=p["surface"], fg=p["text_sub"])
        self.calc_out.configure(bg=p["display_bg"], fg=p["text"])

        col_keys = ["plot_1", "plot_2", "plot_3"]
        for (row, tag), ck in zip(self.fn_badges, col_keys):
            row.configure(bg=p["surface"])
            tag.configure(bg=p["surface"], fg=p[ck])

        for ent, bg_key in self._entries:
            ent.apply_theme(p, p[bg_key])
        for btn, bg_key in self._buttons:
            btn.apply_theme(p, p[bg_key])

        self.plot_card.apply_theme(p, p["bg"])
        self.canvas.configure(bg=p["display_bg"])
        self._redraw_plot()
