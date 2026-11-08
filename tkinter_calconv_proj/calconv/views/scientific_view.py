"""Scientific Calculator view with live preview, 2nd-shift pad, constants popover & tape."""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Dict, List, Optional, Tuple

from ..evaluator import (
    PHYSICAL_CONSTANTS,
    CalcError,
    evaluate,
    format_number,
    format_plain,
)
from ..theme import FontSet
from ..widgets import RoundedButton, RoundedCard, ScrollableFrame, SegmentedBar


class ScientificView(tk.Frame):
    """Flagship Scientific Calculator tab."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        fonts: FontSet,
        palette: Dict[str, str],
        on_send_to_converter: Callable[[float], None],
    ) -> None:
        super().__init__(parent, bg=palette["bg"], bd=0, highlightthickness=0)
        self.fonts = fonts
        self.palette = palette
        self.on_send_to_converter = on_send_to_converter

        # State
        self.expr: str = ""
        self.last_formula: str = "Ready"
        self.ans: float = 0.0
        self.memory: float = 0.0
        self.angle_mode: str = "DEG"
        self.sci_notation: bool = False
        self.second_mode: bool = False
        self.just_evaluated: bool = False
        self.history: List[Tuple[str, float, str]] = []
        self._const_popup: Optional[tk.Toplevel] = None

        self._buttons: List[Tuple[RoundedButton, str]] = []
        self._shiftable_specs: List[Tuple[RoundedButton, Tuple[str, str, Callable[[], None]], Tuple[str, str, Callable[[], None]]]] = []

        self._build_ui()
        self._refresh_display()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        p = self.palette
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=3, minsize=250)
        self.grid_rowconfigure(0, weight=1)

        # Left calculator stack
        self.left_col = tk.Frame(self, bg=p["bg"], bd=0, highlightthickness=0)
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_col.grid_columnconfigure(0, weight=1)
        self.left_col.grid_rowconfigure(0, weight=0, minsize=142)
        self.left_col.grid_rowconfigure(1, weight=0)
        self.left_col.grid_rowconfigure(2, weight=1)

        # 1) Display Card
        self.display_card = RoundedCard(
            self.left_col,
            palette=p,
            parent_bg=p["bg"],
            fill_key="display_bg",
            border_key="display_border",
            radius=16,
            pad_x=18,
            pad_y=12,
        )
        self.display_card.configure(height=144)
        self.display_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        db = self.display_card.body
        db.grid_columnconfigure(0, weight=1)

        self.top_meta = tk.Frame(db, bg=p["display_bg"])
        self.top_meta.grid(row=0, column=0, sticky="ew")

        self.badge_lbl = tk.Label(
            self.top_meta,
            text="DEG  ·  STD",
            bg=p["display_bg"],
            fg=p["accent"],
            font=self.fonts.mono(10, "bold"),
        )
        self.badge_lbl.pack(side="left")

        self.mem_lbl = tk.Label(
            self.top_meta,
            text="",
            bg=p["display_bg"],
            fg=p["tertiary"],
            font=self.fonts.mono(10, "bold"),
            padx=10,
        )
        self.mem_lbl.pack(side="left")

        self.send_conv_btn = RoundedButton(
            self.top_meta,
            "→ Converter",
            command=self._send_current_to_converter,
            kind="ghost",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["display_bg"],
            width=96,
            height=24,
            radius=8,
            font_size=10,
        )
        self.send_conv_btn.pack(side="right", padx=(6, 0))
        self._buttons.append((self.send_conv_btn, "display_bg"))

        self.copy_btn = RoundedButton(
            self.top_meta,
            "Copy",
            command=self._copy_result,
            kind="ghost",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["display_bg"],
            width=60,
            height=24,
            radius=8,
            font_size=10,
        )
        self.copy_btn.pack(side="right")
        self._buttons.append((self.copy_btn, "display_bg"))

        self.formula_lbl = tk.Label(
            db,
            text="Ready",
            anchor="e",
            bg=p["display_bg"],
            fg=p["text_muted"],
            font=self.fonts.mono(12),
        )
        self.formula_lbl.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        self.main_lbl = tk.Label(
            db,
            text="0",
            anchor="e",
            bg=p["display_bg"],
            fg=p["text"],
            font=self.fonts.mono(28, "bold"),
        )
        self.main_lbl.grid(row=2, column=0, sticky="ew", pady=(2, 0))

        self.preview_lbl = tk.Label(
            db,
            text="",
            anchor="e",
            bg=p["display_bg"],
            fg=p["secondary"],
            font=self.fonts.mono(12),
        )
        self.preview_lbl.grid(row=3, column=0, sticky="ew")

        # 2) Control & Memory Ribbon Card
        self.ribbon_card = RoundedCard(
            self.left_col,
            palette=p,
            parent_bg=p["bg"],
            fill_key="surface",
            border_key="card_border",
            radius=14,
            pad_x=12,
            pad_y=8,
        )
        self.ribbon_card.configure(height=54)
        self.ribbon_card.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        rb = self.ribbon_card.body

        self.angle_bar = SegmentedBar(
            rb,
            [("DEG", "DEG"), ("RAD", "RAD"), ("GRAD", "GRAD")],
            selected="DEG",
            on_change=self._set_angle_mode,
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            height=34,
            font_size=10,
        )
        self.angle_bar.configure(width=168)
        self.angle_bar.pack(side="left", padx=(0, 8))

        self.btn_2nd = RoundedButton(
            rb,
            "2nd",
            command=self._toggle_second,
            kind="ghost",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            width=52,
            height=34,
            radius=9,
            font_size=11,
        )
        self.btn_2nd.pack(side="left", padx=3)
        self._buttons.append((self.btn_2nd, "surface"))

        self.btn_fe = RoundedButton(
            rb,
            "F-E",
            command=self._toggle_sci_notation,
            kind="ghost",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            width=52,
            height=34,
            radius=9,
            font_size=11,
        )
        self.btn_fe.pack(side="left", padx=3)
        self._buttons.append((self.btn_fe, "surface"))

        self.btn_consts = RoundedButton(
            rb,
            "Constants ▾",
            command=self._toggle_constants_popup,
            kind="secondary",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            width=102,
            height=34,
            radius=9,
            font_size=11,
        )
        self.btn_consts.pack(side="left", padx=(3, 8))
        self._buttons.append((self.btn_consts, "surface"))

        for m_lbl, m_cmd in (
            ("MS", self._mem_store),
            ("M-", lambda: self._mem_add(-1.0)),
            ("M+", lambda: self._mem_add(1.0)),
            ("MR", self._mem_recall),
            ("MC", self._mem_clear),
        ):
            b = RoundedButton(
                rb,
                m_lbl,
                command=m_cmd,
                kind="fn",
                fonts=self.fonts,
                palette=p,
                parent_bg=p["surface"],
                width=42,
                height=34,
                radius=9,
                font_size=10,
                mono=True,
            )
            b.pack(side="right", padx=2)
            self._buttons.append((b, "surface"))

        # 3) Main 6x8 Keypad Card
        self.pad_card = RoundedCard(
            self.left_col,
            palette=p,
            parent_bg=p["bg"],
            fill_key="surface",
            border_key="card_border",
            radius=16,
            pad_x=12,
            pad_y=12,
        )
        self.pad_card.grid(row=2, column=0, sticky="nsew")
        pad = self.pad_card.body
        for c in range(8):
            pad.grid_columnconfigure(c, weight=1, uniform="scicol")
        for r in range(6):
            pad.grid_rowconfigure(r, weight=1, uniform="scirow")

        def _add_btn(
            r: int,
            c: int,
            text: str,
            cmd: Callable[[], None],
            *,
            kind: str = "fn",
            colspan: int = 1,
            subtext: str = "",
            alt: Optional[Tuple[str, Callable[[], None]]] = None,
        ) -> RoundedButton:
            b = RoundedButton(
                pad,
                text,
                command=cmd,
                kind=kind,
                fonts=self.fonts,
                palette=p,
                parent_bg=p["surface"],
                radius=11,
                subtext=subtext,
            )
            b.grid(row=r, column=c, columnspan=colspan, sticky="nsew", padx=3, pady=3)
            self._buttons.append((b, "surface"))
            if alt is not None:
                alt_lbl, alt_cmd = alt
                self._shiftable_specs.append((b, (text, alt_lbl, cmd), (alt_lbl, text, alt_cmd)))
            return b

        # Row 0
        _add_btn(0, 0, "sin", lambda: self._insert_fn("sin("), subtext="asin", alt=("asin", lambda: self._insert_fn("asin(")))
        _add_btn(0, 1, "cos", lambda: self._insert_fn("cos("), subtext="acos", alt=("acos", lambda: self._insert_fn("acos(")))
        _add_btn(0, 2, "tan", lambda: self._insert_fn("tan("), subtext="atan", alt=("atan", lambda: self._insert_fn("atan(")))
        _add_btn(0, 3, "π", lambda: self._insert_token("π"), subtext="τ", alt=("τ", lambda: self._insert_token("τ")))
        _add_btn(0, 4, "AC", self.clear_all, kind="danger")
        _add_btn(0, 5, "⌫", self.backspace, kind="danger")
        _add_btn(0, 6, "(", lambda: self._insert_token("("), kind="fn")
        _add_btn(0, 7, ")", lambda: self._insert_token(")"), kind="fn")

        # Row 1
        _add_btn(1, 0, "sinh", lambda: self._insert_fn("sinh("), subtext="asinh", alt=("asinh", lambda: self._insert_fn("asinh(")))
        _add_btn(1, 1, "cosh", lambda: self._insert_fn("cosh("), subtext="acosh", alt=("acosh", lambda: self._insert_fn("acosh(")))
        _add_btn(1, 2, "tanh", lambda: self._insert_fn("tanh("), subtext="atanh", alt=("atanh", lambda: self._insert_fn("atanh(")))
        _add_btn(1, 3, "e", lambda: self._insert_token("e"), subtext="φ", alt=("φ", lambda: self._insert_token("φ")))
        _add_btn(1, 4, "7", lambda: self._insert_digit("7"), kind="num")
        _add_btn(1, 5, "8", lambda: self._insert_digit("8"), kind="num")
        _add_btn(1, 6, "9", lambda: self._insert_digit("9"), kind="num")
        _add_btn(1, 7, "÷", lambda: self._insert_op("÷"), kind="op")

        # Row 2
        _add_btn(2, 0, "x²", lambda: self._insert_postfix("^2"), subtext="x³", alt=("x³", lambda: self._insert_postfix("^3")))
        _add_btn(2, 1, "√x", lambda: self._insert_fn("√("), subtext="∛x", alt=("∛x", lambda: self._insert_fn("∛(")))
        _add_btn(2, 2, "xʸ", lambda: self._insert_op("^"), subtext="ʸ√x", alt=("ʸ√x", lambda: self._insert_op(" yroot ")))
        _add_btn(2, 3, "1/x", self._reciprocal)
        _add_btn(2, 4, "4", lambda: self._insert_digit("4"), kind="num")
        _add_btn(2, 5, "5", lambda: self._insert_digit("5"), kind="num")
        _add_btn(2, 6, "6", lambda: self._insert_digit("6"), kind="num")
        _add_btn(2, 7, "×", lambda: self._insert_op("×"), kind="op")

        # Row 3
        _add_btn(3, 0, "ln", lambda: self._insert_fn("ln("), subtext="eˣ", alt=("eˣ", lambda: self._insert_fn("exp(")))
        _add_btn(3, 1, "log", lambda: self._insert_fn("log10("), subtext="10ˣ", alt=("10ˣ", lambda: self._insert_token("10^")))
        _add_btn(3, 2, "log₂", lambda: self._insert_fn("log2("), subtext="2ˣ", alt=("2ˣ", lambda: self._insert_token("2^")))
        _add_btn(3, 3, "n!", lambda: self._insert_postfix("!"))
        _add_btn(3, 4, "1", lambda: self._insert_digit("1"), kind="num")
        _add_btn(3, 5, "2", lambda: self._insert_digit("2"), kind="num")
        _add_btn(3, 6, "3", lambda: self._insert_digit("3"), kind="num")
        _add_btn(3, 7, "−", lambda: self._insert_op("−"), kind="op")

        # Row 4
        _add_btn(4, 0, "|x|", lambda: self._insert_fn("abs("), subtext="⌊x⌋", alt=("⌊x⌋", lambda: self._insert_fn("floor(")))
        _add_btn(4, 1, "nCr", lambda: self._insert_op(" nCr "), subtext="gcd", alt=("gcd", lambda: self._insert_fn("gcd(")))
        _add_btn(4, 2, "nPr", lambda: self._insert_op(" nPr "), subtext="lcm", alt=("lcm", lambda: self._insert_fn("lcm(")))
        _add_btn(4, 3, "mod", lambda: self._insert_op(" mod "), subtext="⌈x⌉", alt=("⌈x⌉", lambda: self._insert_fn("ceil(")))
        _add_btn(4, 4, "±", self._negate_current, kind="num")
        _add_btn(4, 5, "0", lambda: self._insert_digit("0"), kind="num")
        _add_btn(4, 6, ".", lambda: self._insert_digit("."), kind="num")
        _add_btn(4, 7, "+", lambda: self._insert_op("+"), kind="op")

        # Row 5
        _add_btn(5, 0, "sec", lambda: self._insert_fn("sec("), subtext="csc", alt=("csc", lambda: self._insert_fn("csc(")))
        _add_btn(5, 1, "cot", lambda: self._insert_fn("cot("), subtext="rand", alt=("rand", lambda: self._insert_token("rand()")))
        _add_btn(5, 2, "EXP", lambda: self._insert_token("e"), subtext=",", alt=(",", lambda: self._insert_token(",")))
        _add_btn(5, 3, "%", lambda: self._insert_postfix("%"))
        _add_btn(5, 4, "Ans", lambda: self._insert_token("Ans"), kind="secondary")
        _add_btn(5, 5, ",", lambda: self._insert_token(","), kind="fn")
        _add_btn(5, 6, "=", self.evaluate_now, kind="eq", colspan=2)

        # Right column: Calculation Tape / History Card
        self.hist_card = RoundedCard(
            self,
            palette=p,
            parent_bg=p["bg"],
            fill_key="surface",
            border_key="card_border",
            radius=16,
            pad_x=12,
            pad_y=12,
        )
        self.hist_card.grid(row=0, column=1, sticky="nsew")
        hb = self.hist_card.body
        hb.grid_columnconfigure(0, weight=1)
        hb.grid_rowconfigure(1, weight=1)

        self.hist_hdr = tk.Frame(hb, bg=p["surface"])
        self.hist_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.hist_title = tk.Label(
            self.hist_hdr,
            text="CALCULATION TAPE",
            bg=p["surface"],
            fg=p["text_sub"],
            font=self.fonts.ui(10, "bold"),
        )
        self.hist_title.pack(side="left")

        self.clear_hist_btn = RoundedButton(
            self.hist_hdr,
            "Clear",
            command=self._clear_history,
            kind="ghost",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            width=54,
            height=24,
            radius=7,
            font_size=10,
        )
        self.clear_hist_btn.pack(side="right")
        self._buttons.append((self.clear_hist_btn, "surface"))

        self.hist_scroll = ScrollableFrame(hb, bg=p["surface"])
        self.hist_scroll.grid(row=1, column=0, sticky="nsew")
        self._render_history()

    # ------------------------------------------------------------------
    # Actions & Expression Editing
    # ------------------------------------------------------------------
    def _set_angle_mode(self, mode: str) -> None:
        self.angle_mode = mode
        self._refresh_display()

    def _toggle_sci_notation(self) -> None:
        self.sci_notation = not self.sci_notation
        self.btn_fe.set_active(self.sci_notation)
        self._refresh_display()

    def _toggle_second(self) -> None:
        self.second_mode = not self.second_mode
        self.btn_2nd.set_active(self.second_mode)
        for btn, primary_spec, shifted_spec in self._shiftable_specs:
            lbl, sub, cmd = shifted_spec if self.second_mode else primary_spec
            btn.command = cmd
            btn.set_text(lbl, sub)

    def _insert_digit(self, ch: str) -> None:
        if self.just_evaluated:
            self.expr = ""
            self.just_evaluated = False
        if ch == ".":
            # Prevent double decimal in current trailing number token
            tail = ""
            for c in reversed(self.expr):
                if c.isdigit() or c == ".":
                    tail = c + tail
                else:
                    break
            if "." in tail:
                return
            if not tail:
                self.expr += "0"
        self.expr += ch
        self._refresh_display()

    def _insert_token(self, tok: str) -> None:
        if self.just_evaluated and tok not in ("^2", "^3", "%", "!"):
            if tok in ("+", "−", "×", "÷", "^"):
                self.expr = format_plain(self.ans)
            else:
                self.expr = ""
            self.just_evaluated = False
        self.expr += tok
        self._refresh_display()

    def _insert_fn(self, fn_prefix: str) -> None:
        if self.just_evaluated:
            # Wrap previous answer if user hits a function right after '='?
            # Cleanest calculator UX: start fresh expression with function, Ans is available
            self.expr = ""
            self.just_evaluated = False
        self.expr += fn_prefix
        self._refresh_display()

    def _insert_op(self, op_str: str) -> None:
        if self.just_evaluated:
            self.expr = format_plain(self.ans)
            self.just_evaluated = False
        elif not self.expr:
            if op_str in ("−", "-"):
                self.expr = "-"
                self._refresh_display()
                return
            self.expr = format_plain(self.ans)
        # Replace trailing binary operator if user changes mind
        stripped = self.expr.rstrip()
        if stripped and stripped[-1] in "+−×÷^*/-" and op_str.strip() in ("+", "−", "×", "÷", "^"):
            self.expr = stripped[:-1] + op_str
        else:
            self.expr += op_str
        self._refresh_display()

    def _insert_postfix(self, post: str) -> None:
        if self.just_evaluated:
            self.expr = format_plain(self.ans)
            self.just_evaluated = False
        elif not self.expr:
            self.expr = "0"
        self.expr += post
        self._refresh_display()

    def _reciprocal(self) -> None:
        target = self.expr if self.expr else format_plain(self.ans)
        self.expr = f"1/({target})"
        self.just_evaluated = False
        self.evaluate_now()

    def _negate_current(self) -> None:
        if self.just_evaluated:
            self.ans = -self.ans
            self.expr = format_plain(self.ans)
            self._refresh_display()
            return
        if not self.expr:
            self.expr = "-"
        elif self.expr.startswith("-"):
            self.expr = self.expr[1:]
        else:
            self.expr = f"-({self.expr})"
        self._refresh_display()

    def clear_all(self) -> None:
        self.expr = ""
        self.last_formula = "Cleared"
        self.just_evaluated = False
        self._refresh_display()

    def backspace(self) -> None:
        if self.just_evaluated:
            self.just_evaluated = False
        if not self.expr:
            return
        # Remove multi-char tokens cleanly
        for suffix in (" nCr ", " nPr ", " mod ", " yroot ", "asinh(", "acosh(", "atanh(", "log10(", "floor(", "sinh(", "cosh(", "tanh(", "asin(", "acos(", "atan(", "log2(", "sqrt(", "cbrt(", "ceil(", "sin(", "cos(", "tan(", "sec(", "csc(", "cot(", "exp(", "abs(", "gcd(", "lcm(", "ln(", "Ans"):
            if self.expr.endswith(suffix):
                self.expr = self.expr[: -len(suffix)]
                self._refresh_display()
                return
        self.expr = self.expr[:-1]
        self._refresh_display()

    def evaluate_now(self) -> None:
        target = self.expr.strip()
        if not target:
            return
        try:
            val = evaluate(target, angle_mode=self.angle_mode, ans=self.ans)
        except CalcError as exc:
            self.preview_lbl.configure(text=str(exc), fg=self.palette["danger"])
            return

        formatted = format_number(val, sci_notation=self.sci_notation)
        self.last_formula = f"{target} ="
        self.ans = val
        self.history.insert(0, (target, val, formatted))
        if len(self.history) > 60:
            self.history.pop()
        self.expr = format_plain(val)
        self.just_evaluated = True
        self._refresh_display()
        self._render_history()

    # ------------------------------------------------------------------
    # Memory & Clipboard & Constants Popover
    # ------------------------------------------------------------------
    def _current_numeric_value(self) -> Optional[float]:
        if not self.expr.strip():
            return self.ans
        try:
            return evaluate(self.expr, angle_mode=self.angle_mode, ans=self.ans)
        except CalcError:
            return None

    def _mem_clear(self) -> None:
        self.memory = 0.0
        self._refresh_display()

    def _mem_recall(self) -> None:
        if self.just_evaluated:
            self.expr = ""
            self.just_evaluated = False
        self.expr += format_plain(self.memory)
        self._refresh_display()

    def _mem_store(self) -> None:
        val = self._current_numeric_value()
        if val is not None:
            self.memory = val
            self._refresh_display()

    def _mem_add(self, sign: float) -> None:
        val = self._current_numeric_value()
        if val is not None:
            self.memory += sign * val
            self._refresh_display()

    def _copy_result(self) -> None:
        val = self._current_numeric_value()
        txt = format_plain(val) if val is not None else self.expr
        self.clipboard_clear()
        self.clipboard_append(txt)
        self.copy_btn.set_text("Copied ✓")
        self.after(1100, lambda: self.copy_btn.set_text("Copy"))

    def _send_current_to_converter(self) -> None:
        val = self._current_numeric_value()
        if val is not None:
            self.on_send_to_converter(val)

    def insert_external_value(self, val: float) -> None:
        self.expr = format_plain(val)
        self.ans = val
        self.just_evaluated = False
        self._refresh_display()

    def _toggle_constants_popup(self) -> None:
        if self._const_popup is not None:
            try:
                self._const_popup.destroy()
            except Exception:
                pass
            self._const_popup = None
            return

        p = self.palette
        pop = tk.Toplevel(self)
        pop.wm_overrideredirect(True)
        pop.configure(bg=p["accent"])
        try:
            pop.attributes("-topmost", True)
        except Exception:
            pass
        self._const_popup = pop

        wrap = tk.Frame(pop, bg=p["surface"], padx=8, pady=8)
        wrap.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(
            wrap,
            text="PHYSICAL & MATHEMATICAL CONSTANTS",
            bg=p["surface"],
            fg=p["text_sub"],
            font=self.fonts.ui(10, "bold"),
            anchor="w",
        ).pack(fill="x", padx=6, pady=(0, 6))

        sf = ScrollableFrame(wrap, bg=p["surface"])
        sf.configure(width=360, height=280)
        sf.pack(fill="both", expand=True)

        for cinfo in PHYSICAL_CONSTANTS:
            row = tk.Frame(sf.inner, bg=p["surface"], padx=8, pady=5, cursor="hand2")
            row.pack(fill="x", pady=1)

            sym = tk.Label(
                row,
                text=cinfo.symbol,
                width=4,
                anchor="w",
                bg=p["surface"],
                fg=p["accent"],
                font=self.fonts.mono(12, "bold"),
            )
            sym.pack(side="left")

            desc = tk.Label(
                row,
                text=cinfo.name,
                anchor="w",
                bg=p["surface"],
                fg=p["text"],
                font=self.fonts.ui(11),
            )
            desc.pack(side="left", fill="x", expand=True)

            val_txt = f"{cinfo.value:.6g} {cinfo.unit}".strip()
            vlbl = tk.Label(
                row,
                text=val_txt,
                anchor="e",
                bg=p["surface"],
                fg=p["text_muted"],
                font=self.fonts.mono(10),
            )
            vlbl.pack(side="right")

            def _pick(_e: tk.Event, k: str = cinfo.key) -> None:
                if self._const_popup is not None:
                    self._const_popup.destroy()
                    self._const_popup = None
                self._insert_token(k)

            def _hover_in(_e: tk.Event, widgets=(row, sym, desc, vlbl)) -> None:
                for w in widgets:
                    w.configure(bg=p["surface_hi"])

            def _hover_out(_e: tk.Event, widgets=(row, sym, desc, vlbl)) -> None:
                for w in widgets:
                    w.configure(bg=p["surface"])

            for w in (row, sym, desc, vlbl):
                w.bind("<Enter>", _hover_in)
                w.bind("<Leave>", _hover_out)
                w.bind("<ButtonRelease-1>", _pick)

        pop.update_idletasks()
        bx = self.btn_consts.winfo_rootx()
        by = self.btn_consts.winfo_rooty() + self.btn_consts.winfo_height() + 4
        pop.geometry(f"390x325+{bx}+{by}")
        pop.focus_force()
        pop.bind("<Escape>", lambda _e: self._toggle_constants_popup())
        pop.bind("<FocusOut>", lambda _e: self.after(100, self._close_consts_if_unfocused))

    def _close_consts_if_unfocused(self) -> None:
        if self._const_popup is None:
            return
        try:
            f = self._const_popup.focus_get()
            if f is None or not str(f).startswith(str(self._const_popup)):
                self._const_popup.destroy()
                self._const_popup = None
        except Exception:
            self._const_popup = None

    # ------------------------------------------------------------------
    # Rendering Display & History
    # ------------------------------------------------------------------
    def _refresh_display(self) -> None:
        p = self.palette
        not_tag = "SCI" if self.sci_notation else "STD"
        self.badge_lbl.configure(text=f"{self.angle_mode}  ·  {not_tag}")
        self.mem_lbl.configure(
            text=f"MEM {format_number(self.memory, precision=6)}" if abs(self.memory) > 1e-15 else ""
        )
        self.formula_lbl.configure(text=self.last_formula)

        shown = self.expr if self.expr else "0"
        if self.just_evaluated:
            try:
                shown = format_number(float(self.expr), sci_notation=self.sci_notation)
            except ValueError:
                pass

        # Dynamic font scaling for long expressions
        length = len(shown)
        fsize = 28 if length <= 18 else (22 if length <= 26 else (17 if length <= 36 else 14))
        self.main_lbl.configure(text=shown, font=self.fonts.mono(fsize, "bold"))

        # Live instant preview when typing compound expressions
        if self.expr and not self.just_evaluated:
            try:
                val = evaluate(self.expr, angle_mode=self.angle_mode, ans=self.ans)
                prev_str = format_number(val, sci_notation=self.sci_notation)
                if prev_str.replace(",", "") != self.expr.strip():
                    self.preview_lbl.configure(text=f"= {prev_str}", fg=p["secondary"])
                else:
                    self.preview_lbl.configure(text="")
            except CalcError:
                self.preview_lbl.configure(text="")
        else:
            self.preview_lbl.configure(text="")

    def _clear_history(self) -> None:
        self.history.clear()
        self._render_history()

    def _render_history(self) -> None:
        p = self.palette
        for child in self.hist_scroll.inner.winfo_children():
            child.destroy()

        if not self.history:
            tk.Label(
                self.hist_scroll.inner,
                text="Evaluated expressions\nappear here.\n\nClick any entry to\nreuse its formula or result.",
                justify="center",
                bg=p["surface"],
                fg=p["text_muted"],
                font=self.fonts.ui(11),
                pady=36,
            ).pack(fill="x")
            return

        for expr_str, val, fmt_val in self.history:
            item = tk.Frame(
                self.hist_scroll.inner,
                bg=p["surface_alt"],
                padx=10,
                pady=7,
                cursor="hand2",
            )
            item.pack(fill="x", pady=3, padx=2)

            elbl = tk.Label(
                item,
                text=f"{expr_str} =",
                anchor="e",
                bg=p["surface_alt"],
                fg=p["text_sub"],
                font=self.fonts.mono(10),
            )
            elbl.pack(fill="x")

            rlbl = tk.Label(
                item,
                text=fmt_val,
                anchor="e",
                bg=p["surface_alt"],
                fg=p["text"],
                font=self.fonts.mono(13, "bold"),
            )
            rlbl.pack(fill="x")

            def _load_expr(_e: tk.Event, ex: str = expr_str) -> None:
                self.expr = ex
                self.just_evaluated = False
                self._refresh_display()

            def _load_val(_e: tk.Event, v: float = val) -> None:
                if self.just_evaluated or not self.expr:
                    self.expr = format_plain(v)
                else:
                    self.expr += format_plain(v)
                self.just_evaluated = False
                self._refresh_display()

            elbl.bind("<ButtonRelease-1>", _load_expr)
            rlbl.bind("<ButtonRelease-1>", _load_val)
            item.bind("<ButtonRelease-1>", _load_val)

    # ------------------------------------------------------------------
    # Keyboard & Theme
    # ------------------------------------------------------------------
    def handle_key(self, event: tk.Event) -> None:
        keysym = event.keysym
        ch = event.char

        if (event.state & 0x4) or (event.state & 0x8):  # Ctrl or Cmd
            if keysym.lower() == "c":
                self._copy_result()
                return
            if keysym.lower() == "v":
                try:
                    clip = self.clipboard_get().strip()
                    if clip:
                        self._insert_token(clip)
                except Exception:
                    pass
                return

        if keysym in ("Return", "KP_Enter", "equal"):
            self.evaluate_now()
        elif keysym == "BackSpace":
            self.backspace()
        elif keysym in ("Escape", "Delete"):
            self.clear_all()
        elif ch and ch in "0123456789.":
            self._insert_digit(ch)
        elif ch == "+":
            self._insert_op("+")
        elif ch == "-":
            self._insert_op("−")
        elif ch == "*":
            self._insert_op("×")
        elif ch == "/":
            self._insert_op("÷")
        elif ch in ("^", "(", ")", ","):
            self._insert_token(ch)
        elif ch in ("!", "%"):
            self._insert_postfix(ch)
        elif ch and ch.isalpha():
            self._insert_token(ch)

    def apply_theme(self, palette: Dict[str, str]) -> None:
        self.palette = palette
        p = palette
        self.configure(bg=p["bg"])
        self.left_col.configure(bg=p["bg"])

        self.display_card.apply_theme(p, p["bg"])
        self.top_meta.configure(bg=p["display_bg"])
        self.badge_lbl.configure(bg=p["display_bg"], fg=p["accent"])
        self.mem_lbl.configure(bg=p["display_bg"], fg=p["tertiary"])
        self.formula_lbl.configure(bg=p["display_bg"], fg=p["text_muted"])
        self.main_lbl.configure(bg=p["display_bg"], fg=p["text"])
        self.preview_lbl.configure(bg=p["display_bg"], fg=p["secondary"])

        self.ribbon_card.apply_theme(p, p["bg"])
        self.angle_bar.apply_theme(p, p["surface"])
        self.pad_card.apply_theme(p, p["bg"])
        self.hist_card.apply_theme(p, p["bg"])
        self.hist_hdr.configure(bg=p["surface"])
        self.hist_title.configure(bg=p["surface"], fg=p["text_sub"])
        self.hist_scroll.apply_bg(p["surface"])

        for btn, bg_key in self._buttons:
            btn.apply_theme(p, p[bg_key])
        self._render_history()
        self._refresh_display()
