"""Programmer Calculator: live HEX / DEC / OCT / BIN, bitwise ops & clickable bit grid."""

from __future__ import annotations

import tkinter as tk
from typing import Dict, List, Optional, Tuple

from ..theme import FontSet
from ..widgets import RoundedButton, RoundedCard, SegmentedBar


class ProgrammerView(tk.Frame):
    """Integer base converter, bitwise expression evaluator & interactive bit toggle board."""

    def __init__(self, parent: tk.Widget, *, fonts: FontSet, palette: Dict[str, str]) -> None:
        super().__init__(parent, bg=palette["bg"], bd=0, highlightthickness=0)
        self.fonts = fonts
        self.palette = palette

        self.word_bits: int = 32  # 8, 16, 32, 64
        self.signed: bool = True
        self.active_base: int = 10  # 16, 10, 8, 2
        self.current_val: int = 0
        self.pending_op: Optional[str] = None
        self.accumulator: Optional[int] = None
        self.entering_new: bool = True

        self._buttons: List[Tuple[RoundedButton, str]] = []
        self._hex_digit_btns: Dict[int, RoundedButton] = {}
        self._base_rows: Dict[int, Tuple[tk.Frame, tk.Label, tk.Label]] = {}
        self._bit_labels: List[tk.Label] = []
        self._bit_hdr_labels: List[tk.Label] = []

        self._build_ui()
        self._refresh_all()

    # ------------------------------------------------------------------
    # Word masking helpers
    # ------------------------------------------------------------------
    def _mask(self) -> int:
        return (1 << self.word_bits) - 1

    def _clamp(self, val: int) -> int:
        u = val & self._mask()
        if self.signed and (u & (1 << (self.word_bits - 1))):
            return u - (1 << self.word_bits)
        return u

    def _unsigned(self, val: int) -> int:
        return val & self._mask()

    # ------------------------------------------------------------------
    # UI Layout
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        p = self.palette
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Top Multi-Base Readout Card (spans both columns)
        self.readout_card = RoundedCard(
            self,
            palette=p,
            parent_bg=p["bg"],
            fill_key="display_bg",
            border_key="display_border",
            radius=16,
            pad_x=16,
            pad_y=12,
        )
        self.readout_card.configure(height=202)
        self.readout_card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        rb = self.readout_card.body
        rb.grid_columnconfigure(0, weight=1)

        # Top control bar inside readout
        self.top_ctrl = tk.Frame(rb, bg=p["display_bg"])
        self.top_ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.word_bar = SegmentedBar(
            self.top_ctrl,
            [("64", "QWORD 64"), ("32", "DWORD 32"), ("16", "WORD 16"), ("8", "BYTE 8")],
            selected="32",
            on_change=self._on_word_size,
            fonts=self.fonts,
            palette=p,
            parent_bg=p["display_bg"],
            height=30,
            font_size=10,
        )
        self.word_bar.configure(width=330)
        self.word_bar.pack(side="left")

        self.sign_btn = RoundedButton(
            self.top_ctrl,
            "Signed (2's)",
            command=self._toggle_signed,
            kind="ghost",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["display_bg"],
            width=102,
            height=30,
            radius=8,
            font_size=10,
            active=True,
        )
        self.sign_btn.pack(side="left", padx=8)
        self._buttons.append((self.sign_btn, "display_bg"))

        self.expr_status = tk.Label(
            self.top_ctrl,
            text="Click HEX / DEC / OCT / BIN to switch active input base",
            anchor="e",
            bg=p["display_bg"],
            fg=p["text_muted"],
            font=self.fonts.mono(10),
        )
        self.expr_status.pack(side="right")

        for idx, (base, tag) in enumerate(((16, "HEX"), (10, "DEC"), (8, "OCT"), (2, "BIN")), start=1):
            row = tk.Frame(rb, bg=p["display_bg"], padx=8, pady=3, cursor="hand2")
            row.grid(row=idx, column=0, sticky="ew", pady=1)
            tlbl = tk.Label(
                row,
                text=tag,
                width=5,
                anchor="w",
                bg=p["display_bg"],
                fg=p["accent"],
                font=self.fonts.mono(11, "bold"),
            )
            tlbl.pack(side="left")
            vlbl = tk.Label(
                row,
                text="0",
                anchor="e",
                bg=p["display_bg"],
                fg=p["text"],
                font=self.fonts.mono(13, "bold"),
            )
            vlbl.pack(side="right", fill="x", expand=True)

            def _pick_base(_e: tk.Event, b: int = base) -> None:
                self.active_base = b
                self.entering_new = True
                self._refresh_all()

            for w in (row, tlbl, vlbl):
                w.bind("<ButtonRelease-1>", _pick_base)
            self._base_rows[base] = (row, tlbl, vlbl)

        # Bottom Left: Interactive Bit Toggle Matrix Card
        self.bit_card = RoundedCard(
            self,
            palette=p,
            parent_bg=p["bg"],
            fill_key="surface",
            border_key="card_border",
            radius=16,
            pad_x=14,
            pad_y=12,
        )
        self.bit_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        bb = self.bit_card.body
        bb.grid_columnconfigure(0, weight=1)

        self.bit_title = tk.Label(
            bb,
            text="INTERACTIVE BIT INSPECTOR  ·  CLICK ANY BIT TO FLIP",
            anchor="w",
            bg=p["surface"],
            fg=p["text_sub"],
            font=self.fonts.ui(10, "bold"),
        )
        self.bit_title.pack(fill="x", pady=(0, 10))

        self.bit_grid_frame = tk.Frame(bb, bg=p["surface"])
        self.bit_grid_frame.pack(fill="both", expand=True)
        self._build_bit_cells()

        # Quick bit-shift / clear bar at bottom of bit card
        self.bit_footer = tk.Frame(bb, bg=p["surface"])
        self.bit_footer.pack(fill="x", pady=(8, 0))
        for lbl, cmd in (
            ("Invert ~x", self._op_not),
            ("<< 1", lambda: self._shift_by(1, left=True)),
            (">> 1", lambda: self._shift_by(1, left=False)),
            ("RoL", lambda: self._rotate(left=True)),
            ("RoR", lambda: self._rotate(left=False)),
            ("Zero", self._clear_all),
        ):
            b = RoundedButton(
                self.bit_footer,
                lbl,
                command=cmd,
                kind="fn",
                fonts=self.fonts,
                palette=p,
                parent_bg=p["surface"],
                width=62,
                height=34,
                radius=9,
                font_size=10,
                mono=True,
            )
            b.pack(side="left", expand=True, fill="x", padx=2)
            self._buttons.append((b, "surface"))

        # Bottom Right: Hex & Bitwise Keypad Card
        self.pad_card = RoundedCard(
            self,
            palette=p,
            parent_bg=p["bg"],
            fill_key="surface",
            border_key="card_border",
            radius=16,
            pad_x=12,
            pad_y=12,
        )
        self.pad_card.grid(row=1, column=1, sticky="nsew")
        pad = self.pad_card.body
        for c in range(5):
            pad.grid_columnconfigure(c, weight=1, uniform="pcol")
        for r in range(5):
            pad.grid_rowconfigure(r, weight=1, uniform="prow")

        def _pbtn(r: int, c: int, txt: str, cmd, kind: str = "num", digit_val: Optional[int] = None) -> RoundedButton:
            b = RoundedButton(
                pad,
                txt,
                command=cmd,
                kind=kind,
                fonts=self.fonts,
                palette=p,
                parent_bg=p["surface"],
                radius=10,
                mono=True,
            )
            b.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
            self._buttons.append((b, "surface"))
            if digit_val is not None:
                self._hex_digit_btns[digit_val] = b
            return b

        # Row 0
        _pbtn(0, 0, "A", lambda: self._press_digit(10), kind="fn", digit_val=10)
        _pbtn(0, 1, "B", lambda: self._press_digit(11), kind="fn", digit_val=11)
        _pbtn(0, 2, "AND", lambda: self._set_bin_op("AND"), kind="op")
        _pbtn(0, 3, "AC", self._clear_all, kind="danger")
        _pbtn(0, 4, "⌫", self._backspace, kind="danger")
        # Row 1
        _pbtn(1, 0, "C", lambda: self._press_digit(12), kind="fn", digit_val=12)
        _pbtn(1, 1, "7", lambda: self._press_digit(7), digit_val=7)
        _pbtn(1, 2, "8", lambda: self._press_digit(8), digit_val=8)
        _pbtn(1, 3, "9", lambda: self._press_digit(9), digit_val=9)
        _pbtn(1, 4, "÷", lambda: self._set_bin_op("DIV"), kind="op")
        # Row 2
        _pbtn(2, 0, "D", lambda: self._press_digit(13), kind="fn", digit_val=13)
        _pbtn(2, 1, "4", lambda: self._press_digit(4), digit_val=4)
        _pbtn(2, 2, "5", lambda: self._press_digit(5), digit_val=5)
        _pbtn(2, 3, "6", lambda: self._press_digit(6), digit_val=6)
        _pbtn(2, 4, "×", lambda: self._set_bin_op("MUL"), kind="op")
        # Row 3
        _pbtn(3, 0, "E", lambda: self._press_digit(14), kind="fn", digit_val=14)
        _pbtn(3, 1, "1", lambda: self._press_digit(1), digit_val=1)
        _pbtn(3, 2, "2", lambda: self._press_digit(2), digit_val=2)
        _pbtn(3, 3, "3", lambda: self._press_digit(3), digit_val=3)
        _pbtn(3, 4, "−", lambda: self._set_bin_op("SUB"), kind="op")
        # Row 4
        _pbtn(4, 0, "F", lambda: self._press_digit(15), kind="fn", digit_val=15)
        _pbtn(4, 1, "OR", lambda: self._set_bin_op("OR"), kind="op")
        _pbtn(4, 2, "0", lambda: self._press_digit(0), digit_val=0)
        _pbtn(4, 3, "XOR", lambda: self._set_bin_op("XOR"), kind="op")
        _pbtn(4, 4, "+", lambda: self._set_bin_op("ADD"), kind="op")

        # Row 5 for '=', <<, >>, MOD, ±
        pad.grid_rowconfigure(5, weight=1, uniform="prow")
        _pbtn(5, 0, "LSH", lambda: self._set_bin_op("LSH"), kind="op")
        _pbtn(5, 1, "RSH", lambda: self._set_bin_op("RSH"), kind="op")
        _pbtn(5, 2, "MOD", lambda: self._set_bin_op("MOD"), kind="op")
        _pbtn(5, 3, "±", self._negate, kind="fn")
        _pbtn(5, 4, "=", self._equals, kind="eq")

    def _build_bit_cells(self) -> None:
        p = self.palette
        for child in self.bit_grid_frame.winfo_children():
            child.destroy()
        self._bit_labels.clear()
        self._bit_hdr_labels.clear()

        # 4 rows of 16 bits (bits 63..0)
        for c in range(16):
            self.bit_grid_frame.grid_columnconfigure(c, weight=1)

        for row_idx in range(4):
            high_bit = 63 - row_idx * 16
            low_bit = high_bit - 15
            hdr = tk.Label(
                self.bit_grid_frame,
                text=f"Bits {high_bit} .. {low_bit}",
                anchor="w",
                bg=p["surface"],
                fg=p["text_muted"],
                font=self.fonts.mono(9),
            )
            hdr.grid(row=row_idx * 2, column=0, columnspan=16, sticky="w", pady=(4, 1))
            self._bit_hdr_labels.append(hdr)

            for col_idx in range(16):
                bit_pos = high_bit - col_idx
                lbl = tk.Label(
                    self.bit_grid_frame,
                    text="0",
                    width=2,
                    pady=5,
                    bg=p["surface_alt"],
                    fg=p["text_sub"],
                    font=self.fonts.mono(11, "bold"),
                    cursor="hand2",
                )
                padx_right = 5 if col_idx % 4 == 3 and col_idx != 15 else 1
                lbl.grid(row=row_idx * 2 + 1, column=col_idx, sticky="ew", padx=(1, padx_right), pady=2)
                lbl.bind("<ButtonRelease-1>", lambda _e, bp=bit_pos: self._toggle_bit(bp))
                self._bit_labels.append(lbl)  # index 0 = bit 63, index 63 = bit 0

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------
    def _on_word_size(self, key: str) -> None:
        self.word_bits = int(key)
        self.current_val = self._clamp(self.current_val)
        if self.accumulator is not None:
            self.accumulator = self._clamp(self.accumulator)
        self._refresh_all()

    def _toggle_signed(self) -> None:
        self.signed = not self.signed
        self.sign_btn.set_active(self.signed)
        self.sign_btn.set_text("Signed (2's)" if self.signed else "Unsigned")
        self.current_val = self._clamp(self.current_val)
        self._refresh_all()

    def _toggle_bit(self, bit_pos: int) -> None:
        if bit_pos >= self.word_bits:
            return
        u = self._unsigned(self.current_val) ^ (1 << bit_pos)
        self.current_val = self._clamp(u)
        self.entering_new = False
        self._refresh_all()

    def _press_digit(self, d: int) -> None:
        if d >= self.active_base:
            return
        if self.entering_new:
            self.current_val = 0
            self.entering_new = False
        if self.active_base == 10 and self.signed and self.current_val < 0:
            nxt = self.current_val * 10 - d
        else:
            u = self._unsigned(self.current_val) if self.active_base != 10 else self.current_val
            nxt = u * self.active_base + d
        self.current_val = self._clamp(nxt)
        self._refresh_all()

    def _backspace(self) -> None:
        if self.entering_new:
            return
        if self.active_base == 10 and self.signed:
            self.current_val = int(self.current_val / 10)
        else:
            self.current_val = self._clamp(self._unsigned(self.current_val) // self.active_base)
        self._refresh_all()

    def _clear_all(self) -> None:
        self.current_val = 0
        self.accumulator = None
        self.pending_op = None
        self.entering_new = True
        self._refresh_all()

    def _negate(self) -> None:
        self.current_val = self._clamp(-self.current_val)
        self._refresh_all()

    def _op_not(self) -> None:
        self.current_val = self._clamp(~self._unsigned(self.current_val))
        self.entering_new = True
        self._refresh_all()

    def _shift_by(self, n: int, *, left: bool) -> None:
        u = self._unsigned(self.current_val)
        res = (u << n) if left else (u >> n)
        self.current_val = self._clamp(res)
        self.entering_new = True
        self._refresh_all()

    def _rotate(self, *, left: bool) -> None:
        u = self._unsigned(self.current_val)
        w = self.word_bits
        if left:
            res = ((u << 1) & self._mask()) | (u >> (w - 1))
        else:
            res = (u >> 1) | ((u & 1) << (w - 1))
        self.current_val = self._clamp(res)
        self.entering_new = True
        self._refresh_all()

    def _apply_pending(self, a: int, op: str, b: int) -> int:
        ua, ub = self._unsigned(a), self._unsigned(b)
        if op == "ADD":
            return self._clamp(a + b)
        if op == "SUB":
            return self._clamp(a - b)
        if op == "MUL":
            return self._clamp(a * b)
        if op == "DIV":
            return self._clamp(int(a / b)) if b != 0 else 0
        if op == "MOD":
            return self._clamp(a % b) if b != 0 else 0
        if op == "AND":
            return self._clamp(ua & ub)
        if op == "OR":
            return self._clamp(ua | ub)
        if op == "XOR":
            return self._clamp(ua ^ ub)
        if op == "LSH":
            return self._clamp(ua << max(0, min(64, ub)))
        if op == "RSH":
            return self._clamp(ua >> max(0, min(64, ub)))
        return b

    def _set_bin_op(self, op: str) -> None:
        if self.accumulator is not None and not self.entering_new and self.pending_op is not None:
            self.current_val = self._apply_pending(self.accumulator, self.pending_op, self.current_val)
        self.accumulator = self.current_val
        self.pending_op = op
        self.entering_new = True
        self._refresh_all()

    def _equals(self) -> None:
        if self.accumulator is not None and self.pending_op is not None:
            self.current_val = self._apply_pending(self.accumulator, self.pending_op, self.current_val)
            self.accumulator = None
            self.pending_op = None
            self.entering_new = True
            self._refresh_all()

    def _format_grouped(self, s: str, group: int, sep: str = " ") -> str:
        rem = len(s) % group
        chunks = [s[:rem]] if rem else []
        chunks.extend(s[i : i + group] for i in range(rem, len(s), group))
        return sep.join(chunks) if chunks else "0"

    def _refresh_all(self) -> None:
        p = self.palette
        u = self._unsigned(self.current_val)

        hex_str = self._format_grouped(f"{u:X}", 4)
        dec_str = f"{self.current_val:,}"
        oct_str = self._format_grouped(f"{u:o}", 3)
        bin_raw = f"{u:b}"
        pad_len = max(4, ((len(bin_raw) + 3) // 4) * 4)
        bin_str = self._format_grouped(bin_raw.zfill(pad_len), 4)

        values = {16: hex_str, 10: dec_str, 8: oct_str, 2: bin_str}
        for base, (row, tlbl, vlbl) in self._base_rows.items():
            is_act = base == self.active_base
            bg = p["op_btn"] if is_act else p["display_bg"]
            row.configure(bg=bg)
            tlbl.configure(bg=bg, fg=p["accent_hover"] if is_act and p["bg"].startswith("#0") else p["accent"])
            vlbl.configure(
                text=values[base],
                bg=bg,
                fg=p["text"] if is_act else p["text_sub"],
                font=self.fonts.mono(13 if base != 2 else 11, "bold" if is_act else "normal"),
            )

        if self.pending_op and self.accumulator is not None:
            self.expr_status.configure(text=f"{self.accumulator}  {self.pending_op}  …", fg=p["secondary"])
        else:
            self.expr_status.configure(
                text=f"Active Base {self.active_base}  ·  {self.word_bits}-bit",
                fg=p["text_muted"],
            )

        # Update bit matrix
        for idx, lbl in enumerate(self._bit_labels):
            bit_pos = 63 - idx
            if bit_pos >= self.word_bits:
                lbl.configure(text="·", bg=p["surface"], fg=p["card_border"], cursor="arrow")
            else:
                bit_on = bool((u >> bit_pos) & 1)
                lbl.configure(
                    text="1" if bit_on else "0",
                    bg=p["accent"] if bit_on else p["surface_alt"],
                    fg=p["eq_text"] if bit_on else p["text_sub"],
                    cursor="hand2",
                )

        # Highlight digits valid for active base
        for d, btn in self._hex_digit_btns.items():
            enabled = d < self.active_base
            btn.kind = ("fn" if d >= 10 else "num") if enabled else "fn"
            btn._redraw()

    def handle_key(self, event: tk.Event) -> None:
        ch = event.char.upper() if event.char else ""
        ks = event.keysym
        if ch and ch in "0123456789ABCDEF":
            self._press_digit(int(ch, 16))
        elif ks in ("Return", "KP_Enter", "equal"):
            self._equals()
        elif ks == "BackSpace":
            self._backspace()
        elif ks in ("Escape", "Delete"):
            self._clear_all()
        elif ch == "+":
            self._set_bin_op("ADD")
        elif ch == "-":
            self._set_bin_op("SUB")
        elif ch == "*":
            self._set_bin_op("MUL")
        elif ch == "/":
            self._set_bin_op("DIV")
        elif ch == "&":
            self._set_bin_op("AND")
        elif ch == "|":
            self._set_bin_op("OR")
        elif ch == "^":
            self._set_bin_op("XOR")
        elif ch == "~":
            self._op_not()

    def apply_theme(self, palette: Dict[str, str]) -> None:
        self.palette = palette
        p = palette
        self.configure(bg=p["bg"])
        self.readout_card.apply_theme(p, p["bg"])
        self.top_ctrl.configure(bg=p["display_bg"])
        self.word_bar.apply_theme(p, p["display_bg"])
        self.bit_card.apply_theme(p, p["bg"])
        self.bit_title.configure(bg=p["surface"], fg=p["text_sub"])
        self.bit_grid_frame.configure(bg=p["surface"])
        self.bit_footer.configure(bg=p["surface"])
        for hdr in self._bit_hdr_labels:
            hdr.configure(bg=p["surface"], fg=p["text_muted"])
        self.pad_card.apply_theme(p, p["bg"])
        for btn, bg_key in self._buttons:
            btn.apply_theme(p, p[bg_key])
        self._refresh_all()
