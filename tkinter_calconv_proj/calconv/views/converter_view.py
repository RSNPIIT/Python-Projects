"""Measuring & Unit Converter view across 16 categories and 150+ units."""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Dict, List, Optional, Tuple

from ..evaluator import CalcError, evaluate, format_number, format_plain
from ..theme import FontSet
from ..units import CATEGORIES, CATEGORY_MAP, convert_all, convert_value, get_unit
from ..widgets import (
    DropdownPill,
    RoundedButton,
    RoundedCard,
    ScrollableFrame,
    StyledEntry,
)


class ConverterView(tk.Frame):
    """Live bidirectional Measuring & Unit Converter with all-units comparison table."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        fonts: FontSet,
        palette: Dict[str, str],
        on_send_to_calc: Callable[[float], None],
    ) -> None:
        super().__init__(parent, bg=palette["bg"], bd=0, highlightthickness=0)
        self.fonts = fonts
        self.palette = palette
        self.on_send_to_calc = on_send_to_calc

        self.current_cat: str = CATEGORIES[0].key
        self.from_unit: str = CATEGORIES[0].default_from
        self.to_unit: str = CATEGORIES[0].default_to
        self.last_result: Optional[float] = None

        self._buttons: List[Tuple[RoundedButton, str]] = []
        self._cat_rows: Dict[str, Tuple[tk.Frame, tk.Label]] = {}

        self._build_ui()
        self._select_category(self.current_cat)

    def _build_ui(self) -> None:
        p = self.palette
        self.grid_columnconfigure(0, weight=0, minsize=238)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Category Sidebar Card
        self.cat_card = RoundedCard(
            self,
            palette=p,
            parent_bg=p["bg"],
            fill_key="surface",
            border_key="card_border",
            radius=16,
            pad_x=10,
            pad_y=12,
        )
        self.cat_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        cb = self.cat_card.body
        cb.grid_columnconfigure(0, weight=1)
        cb.grid_rowconfigure(1, weight=1)

        self.cat_hdr = tk.Label(
            cb,
            text="MEASUREMENT CATEGORIES",
            anchor="w",
            bg=p["surface"],
            fg=p["text_sub"],
            font=self.fonts.ui(10, "bold"),
            padx=6,
        )
        self.cat_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.cat_scroll = ScrollableFrame(cb, bg=p["surface"])
        self.cat_scroll.grid(row=1, column=0, sticky="nsew")
        self._populate_categories()

        # Right Workspace
        self.right_col = tk.Frame(self, bg=p["bg"], bd=0, highlightthickness=0)
        self.right_col.grid(row=0, column=1, sticky="nsew")
        self.right_col.grid_columnconfigure(0, weight=1)
        self.right_col.grid_rowconfigure(0, weight=0, minsize=288)
        self.right_col.grid_rowconfigure(1, weight=1)

        # Top Interactive Converter Card
        self.conv_card = RoundedCard(
            self.right_col,
            palette=p,
            parent_bg=p["bg"],
            fill_key="surface",
            border_key="card_border",
            radius=16,
            pad_x=18,
            pad_y=14,
        )
        self.conv_card.configure(height=288)
        self.conv_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        cv = self.conv_card.body
        cv.grid_columnconfigure(0, weight=3)
        cv.grid_columnconfigure(1, weight=2, minsize=210)

        # Header + unit ratio subtitle
        self.hdr_row = tk.Frame(cv, bg=p["surface"])
        self.hdr_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self.cat_title_lbl = tk.Label(
            self.hdr_row,
            text="Length & Distance",
            bg=p["surface"],
            fg=p["text"],
            font=self.fonts.ui(16, "bold"),
        )
        self.cat_title_lbl.pack(side="left")

        self.ratio_lbl = tk.Label(
            self.hdr_row,
            text="",
            bg=p["surface"],
            fg=p["accent"],
            font=self.fonts.mono(11),
        )
        self.ratio_lbl.pack(side="right")

        # FROM label + input + unit dropdown
        self.from_tag = tk.Label(
            cv,
            text="FROM VALUE (expressions like 3/4 or 2*pi supported)",
            anchor="w",
            bg=p["surface"],
            fg=p["text_muted"],
            font=self.fonts.ui(10, "bold"),
        )
        self.from_tag.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        self.input_entry = StyledEntry(
            cv,
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            initial="1",
            font_size=18,
            mono=True,
            height=46,
            on_change=lambda _s: self._recalculate(),
        )
        self.input_entry.grid(row=2, column=0, sticky="ew", padx=(0, 10))

        self.from_dropdown = DropdownPill(
            cv,
            items=[],
            selected_key=self.from_unit,
            on_select=self._on_from_selected,
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            height=46,
            font_size=12,
        )
        self.from_dropdown.grid(row=2, column=1, sticky="ew")

        # Action toolbar row (Swap, Presets, Copy, Send to Calc)
        self.action_row = tk.Frame(cv, bg=p["surface"])
        self.action_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=12)

        self.swap_btn = RoundedButton(
            self.action_row,
            "⇅  Swap Units",
            command=self._swap_units,
            kind="op",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            width=118,
            height=34,
            radius=9,
            font_size=11,
        )
        self.swap_btn.pack(side="left", padx=(0, 8))
        self._buttons.append((self.swap_btn, "surface"))

        for preset in ("1", "10", "100", "1000"):
            pb = RoundedButton(
                self.action_row,
                preset,
                command=lambda val=preset: self.input_entry.set(val),
                kind="fn",
                fonts=self.fonts,
                palette=p,
                parent_bg=p["surface"],
                width=48,
                height=34,
                radius=9,
                font_size=10,
                mono=True,
            )
            pb.pack(side="left", padx=2)
            self._buttons.append((pb, "surface"))

        self.to_calc_btn = RoundedButton(
            self.action_row,
            "→ Scientific",
            command=self._send_to_calc,
            kind="secondary",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            width=104,
            height=34,
            radius=9,
            font_size=11,
        )
        self.to_calc_btn.pack(side="right", padx=(6, 0))
        self._buttons.append((self.to_calc_btn, "surface"))

        self.copy_res_btn = RoundedButton(
            self.action_row,
            "Copy",
            command=self._copy_converted,
            kind="ghost",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            width=66,
            height=34,
            radius=9,
            font_size=11,
        )
        self.copy_res_btn.pack(side="right")
        self._buttons.append((self.copy_res_btn, "surface"))

        # TO label + output box + unit dropdown
        self.to_tag = tk.Label(
            cv,
            text="CONVERTED RESULT",
            anchor="w",
            bg=p["surface"],
            fg=p["text_muted"],
            font=self.fonts.ui(10, "bold"),
        )
        self.to_tag.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        self.result_box = RoundedCard(
            cv,
            palette=p,
            parent_bg=p["surface"],
            fill_key="display_bg",
            border_key="display_border",
            radius=10,
            pad_x=12,
            pad_y=8,
        )
        self.result_box.configure(height=48)
        self.result_box.grid(row=5, column=0, sticky="ew", padx=(0, 10))
        self.result_lbl = tk.Label(
            self.result_box.body,
            text="0",
            anchor="w",
            bg=p["display_bg"],
            fg=p["secondary"],
            font=self.fonts.mono(19, "bold"),
        )
        self.result_lbl.pack(fill="both", expand=True)

        self.to_dropdown = DropdownPill(
            cv,
            items=[],
            selected_key=self.to_unit,
            on_select=self._on_to_selected,
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            height=48,
            font_size=12,
        )
        self.to_dropdown.grid(row=5, column=1, sticky="ew")

        # Bottom All-Units Comparison Card
        self.all_card = RoundedCard(
            self.right_col,
            palette=p,
            parent_bg=p["bg"],
            fill_key="surface",
            border_key="card_border",
            radius=16,
            pad_x=16,
            pad_y=12,
        )
        self.all_card.grid(row=1, column=0, sticky="nsew")
        ab = self.all_card.body
        ab.grid_columnconfigure(0, weight=1)
        ab.grid_rowconfigure(1, weight=1)

        self.all_hdr = tk.Label(
            ab,
            text="ALL EQUIVALENT UNITS IN CATEGORY  ·  CLICK ANY UNIT TO SELECT AS TARGET",
            anchor="w",
            bg=p["surface"],
            fg=p["text_sub"],
            font=self.fonts.ui(10, "bold"),
        )
        self.all_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.all_scroll = ScrollableFrame(ab, bg=p["surface"])
        self.all_scroll.grid(row=1, column=0, sticky="nsew")

    # ------------------------------------------------------------------
    # Logic
    # ------------------------------------------------------------------
    def _populate_categories(self) -> None:
        p = self.palette
        for child in self.cat_scroll.inner.winfo_children():
            child.destroy()
        self._cat_rows.clear()

        for cat in CATEGORIES:
            row = tk.Frame(self.cat_scroll.inner, bg=p["surface"], padx=8, pady=6, cursor="hand2")
            row.pack(fill="x", pady=1)
            lbl = tk.Label(
                row,
                text=f"{cat.badge}  {cat.name}",
                anchor="w",
                bg=p["surface"],
                fg=p["text"],
                font=self.fonts.ui(11),
            )
            lbl.pack(fill="x")

            def _pick(_e: tk.Event, k: str = cat.key) -> None:
                self._select_category(k)

            row.bind("<ButtonRelease-1>", _pick)
            lbl.bind("<ButtonRelease-1>", _pick)
            self._cat_rows[cat.key] = (row, lbl)

        self._highlight_active_category()

    def _highlight_active_category(self) -> None:
        p = self.palette
        for k, (row, lbl) in self._cat_rows.items():
            is_sel = k == self.current_cat
            bg = p["accent"] if is_sel else p["surface"]
            fg = p["eq_text"] if is_sel else p["text"]
            row.configure(bg=bg)
            lbl.configure(bg=bg, fg=fg, font=self.fonts.ui(11, "bold" if is_sel else "normal"))

    def _select_category(self, cat_key: str) -> None:
        self.current_cat = cat_key
        cat = CATEGORY_MAP[cat_key]
        self.from_unit = cat.default_from
        self.to_unit = cat.default_to
        self.cat_title_lbl.configure(text=f"{cat.badge}  {cat.name}")

        dropdown_items = [(u.code, f"{u.name}  ({u.symbol})") for u in cat.units]
        self.from_dropdown.set_items(dropdown_items, self.from_unit)
        self.to_dropdown.set_items(dropdown_items, self.to_unit)
        self._highlight_active_category()
        self._recalculate()

    def _on_from_selected(self, code: str) -> None:
        self.from_unit = code
        self._recalculate()

    def _on_to_selected(self, code: str) -> None:
        self.to_unit = code
        self._recalculate()

    def _swap_units(self) -> None:
        self.from_unit, self.to_unit = self.to_unit, self.from_unit
        self.from_dropdown.set_selected(self.from_unit)
        self.to_dropdown.set_selected(self.to_unit)
        self._recalculate()

    def _copy_converted(self) -> None:
        if self.last_result is None:
            return
        self.clipboard_clear()
        self.clipboard_append(format_plain(self.last_result, precision=12))
        self.copy_res_btn.set_text("Copied ✓")
        self.after(1100, lambda: self.copy_res_btn.set_text("Copy"))

    def _send_to_calc(self) -> None:
        if self.last_result is not None:
            self.on_send_to_calc(self.last_result)

    def set_external_value(self, val: float) -> None:
        self.input_entry.set(format_plain(val, precision=12))
        self._recalculate()

    def _recalculate(self) -> None:
        p = self.palette
        raw = self.input_entry.get().strip().replace(",", "")
        if not raw:
            self.last_result = None
            self.result_lbl.configure(text="—", fg=p["text_muted"])
            self.ratio_lbl.configure(text="")
            self._render_all_units(None)
            return

        try:
            in_val = float(raw)
        except ValueError:
            try:
                in_val = evaluate(raw, angle_mode="DEG")
            except CalcError:
                self.last_result = None
                self.result_lbl.configure(text="Invalid number", fg=p["danger"])
                self._render_all_units(None)
                return

        try:
            out_val = convert_value(self.current_cat, in_val, self.from_unit, self.to_unit)
            unit_one = convert_value(self.current_cat, 1.0, self.from_unit, self.to_unit)
        except Exception as exc:
            self.last_result = None
            self.result_lbl.configure(text=str(exc), fg=p["danger"])
            return

        self.last_result = out_val
        u_from = get_unit(self.current_cat, self.from_unit)
        u_to = get_unit(self.current_cat, self.to_unit)
        sym_from = u_from.symbol if u_from else self.from_unit
        sym_to = u_to.symbol if u_to else self.to_unit

        self.result_lbl.configure(
            text=f"{format_number(out_val, precision=11)}  {sym_to}",
            fg=p["secondary"],
        )
        if self.current_cat == "temperature":
            self.ratio_lbl.configure(
                text=f"{format_number(in_val, precision=6)} {sym_from}  =  {format_number(out_val, precision=6)} {sym_to}"
            )
        else:
            self.ratio_lbl.configure(
                text=f"1 {sym_from}  =  {format_number(unit_one, precision=8)} {sym_to}"
            )

        self._render_all_units(in_val)

    def _render_all_units(self, in_val: Optional[float]) -> None:
        p = self.palette
        inner = self.all_scroll.inner
        for child in inner.winfo_children():
            child.destroy()

        if in_val is None:
            return

        inner.grid_columnconfigure(0, weight=1, uniform="allu")
        inner.grid_columnconfigure(1, weight=1, uniform="allu")

        all_pairs = convert_all(self.current_cat, in_val, self.from_unit)
        for idx, (u, converted) in enumerate(all_pairs):
            r, c = divmod(idx, 2)
            is_target = u.code == self.to_unit
            card_bg = p["op_btn"] if is_target else p["surface_alt"]

            cell = tk.Frame(inner, bg=card_bg, padx=10, pady=7, cursor="hand2")
            cell.grid(row=r, column=c, sticky="ew", padx=4, pady=3)

            nlbl = tk.Label(
                cell,
                text=u.name,
                anchor="w",
                bg=card_bg,
                fg=p["text_sub"] if not is_target else p["text"],
                font=self.fonts.ui(10, "bold" if is_target else "normal"),
            )
            nlbl.pack(side="left")

            vlbl = tk.Label(
                cell,
                text=f"{format_number(converted, precision=9)} {u.symbol}",
                anchor="e",
                bg=card_bg,
                fg=p["accent_hover"] if is_target and p["bg"].startswith("#0") else (p["accent"] if is_target else p["text"]),
                font=self.fonts.mono(11, "bold"),
            )
            vlbl.pack(side="right")

            def _select_target(_e: tk.Event, code: str = u.code) -> None:
                self.to_unit = code
                self.to_dropdown.set_selected(code)
                self._recalculate()

            for w in (cell, nlbl, vlbl):
                w.bind("<ButtonRelease-1>", _select_target)

    def apply_theme(self, palette: Dict[str, str]) -> None:
        self.palette = palette
        p = palette
        self.configure(bg=p["bg"])
        self.right_col.configure(bg=p["bg"])

        self.cat_card.apply_theme(p, p["bg"])
        self.cat_hdr.configure(bg=p["surface"], fg=p["text_sub"])
        self.cat_scroll.apply_bg(p["surface"])
        self._populate_categories()

        self.conv_card.apply_theme(p, p["bg"])
        self.hdr_row.configure(bg=p["surface"])
        self.cat_title_lbl.configure(bg=p["surface"], fg=p["text"])
        self.ratio_lbl.configure(bg=p["surface"], fg=p["accent"])
        self.from_tag.configure(bg=p["surface"], fg=p["text_muted"])
        self.to_tag.configure(bg=p["surface"], fg=p["text_muted"])
        self.action_row.configure(bg=p["surface"])

        self.input_entry.apply_theme(p, p["surface"])
        self.from_dropdown.apply_theme(p, p["surface"])
        self.to_dropdown.apply_theme(p, p["surface"])
        self.result_box.apply_theme(p, p["surface"])

        self.all_card.apply_theme(p, p["bg"])
        self.all_hdr.configure(bg=p["surface"], fg=p["text_sub"])
        self.all_scroll.apply_bg(p["surface"])

        for btn, bg_key in self._buttons:
            btn.apply_theme(p, p[bg_key])
        self._recalculate()
