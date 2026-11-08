"""Custom Canvas-drawn rounded widgets for pixel-consistent macOS/Windows/Linux UI."""

from __future__ import annotations

import math
import sys
import tkinter as tk
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .theme import FontSet, blend_hex


def rounded_rect_points(x1: float, y1: float, x2: float, y2: float, r: float, steps: int = 6) -> List[float]:
    w = max(1.0, x2 - x1)
    h = max(1.0, y2 - y1)
    r = max(0.0, min(r, w / 2.0, h / 2.0))
    if r < 0.5:
        return [x1, y1, x2, y1, x2, y2, x1, y2]

    pts: List[float] = []
    corners = [
        (x2 - r, y1 + r, -math.pi / 2.0, 0.0),
        (x2 - r, y2 - r, 0.0, math.pi / 2.0),
        (x1 + r, y2 - r, math.pi / 2.0, math.pi),
        (x1 + r, y1 + r, math.pi, 1.5 * math.pi),
    ]
    for cx, cy, a0, a1 in corners:
        for i in range(steps + 1):
            ang = a0 + (a1 - a0) * (i / steps)
            pts.append(cx + r * math.cos(ang))
            pts.append(cy + r * math.sin(ang))
    return pts


def draw_rounded_rect(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    r: float,
    fill: str,
    outline: str = "",
    width: int = 1,
    tags: Tuple[str, ...] = (),
) -> int:
    pts = rounded_rect_points(x1, y1, x2, y2, r)
    return canvas.create_polygon(
        pts,
        fill=fill,
        outline=outline if outline else fill,
        width=width,
        smooth=False,
        tags=tags,
    )


class RoundedButton(tk.Canvas):
    """Tactile Canvas-drawn rounded button immune to macOS Aqua Button color overrides."""

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command: Optional[Callable[[], None]] = None,
        *,
        kind: str = "num",
        fonts: FontSet,
        palette: Dict[str, str],
        parent_bg: Optional[str] = None,
        width: int = 68,
        height: int = 46,
        radius: int = 11,
        font_size: Optional[int] = None,
        mono: bool = False,
        active: bool = False,
        subtext: str = "",
    ) -> None:
        self.palette = palette
        self.parent_bg = parent_bg or palette["surface"]
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=self.parent_bg,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self.text = text
        self.subtext = subtext
        self.command = command
        self.kind = kind
        self.fonts = fonts
        self.radius = radius
        self.font_size = font_size
        self.mono = mono
        self.active = active
        self._hovered = False
        self._pressed = False

        self.bind("<Configure>", lambda _e: self._redraw())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def set_text(self, text: str, subtext: Optional[str] = None) -> None:
        self.text = text
        if subtext is not None:
            self.subtext = subtext
        self._redraw()

    def set_active(self, active: bool) -> None:
        self.active = active
        self._redraw()

    def apply_theme(self, palette: Dict[str, str], parent_bg: Optional[str] = None) -> None:
        self.palette = palette
        self.parent_bg = parent_bg or palette["surface"]
        self.configure(bg=self.parent_bg)
        self._redraw()

    def _resolve_colors(self) -> Tuple[str, str, str]:
        p = self.palette
        if self.active:
            fill = p["accent_hover"] if self._hovered else p["accent"]
            fg = p["eq_text"]
            border = blend_hex(fill, "#ffffff", 0.25)
            return fill, fg, border

        if self.kind == "num":
            fill = p["num_btn_hover"] if self._hovered else p["num_btn"]
            fg = p["text"]
            border = p["card_border"]
        elif self.kind == "fn":
            fill = p["fn_btn_hover"] if self._hovered else p["fn_btn"]
            fg = p["text_sub"] if not self._hovered else p["text"]
            border = p["card_border"]
        elif self.kind == "op":
            fill = p["op_btn_hover"] if self._hovered else p["op_btn"]
            fg = p["accent_hover"] if p["bg"].startswith("#0") else p["accent"]
            border = blend_hex(p["op_btn"], p["accent"], 0.35)
        elif self.kind == "eq":
            fill = p["eq_btn_hover"] if self._hovered else p["eq_btn"]
            fg = p["eq_text"]
            border = blend_hex(fill, "#ffffff", 0.22)
        elif self.kind == "danger":
            base = blend_hex(p["fn_btn"], p["danger"], 0.18)
            hov = blend_hex(p["fn_btn"], p["danger"], 0.34)
            fill = hov if self._hovered else base
            fg = p["danger"]
            border = blend_hex(p["card_border"], p["danger"], 0.35)
        elif self.kind == "secondary":
            base = blend_hex(p["fn_btn"], p["secondary"], 0.18)
            hov = blend_hex(p["fn_btn"], p["secondary"], 0.34)
            fill = hov if self._hovered else base
            fg = p["secondary"]
            border = blend_hex(p["card_border"], p["secondary"], 0.35)
        else:  # ghost / pill
            fill = p["surface_hi"] if self._hovered else p["surface_alt"]
            fg = p["text"]
            border = p["card_border"]

        if self._pressed:
            fill = blend_hex(fill, p["accent"], 0.22)
        return fill, fg, border

    def _redraw(self) -> None:
        self.delete("all")
        w = max(10, self.winfo_width())
        h = max(10, self.winfo_height())
        if w <= 1:
            w = int(self["width"])
            h = int(self["height"])

        fill, fg, border = self._resolve_colors()
        dy = 1.0 if self._pressed else 0.0
        pad = 1.5
        draw_rounded_rect(
            self,
            pad,
            pad + dy,
            w - pad,
            h - pad + dy,
            min(self.radius, (h - 3) / 2),
            fill=fill,
            outline=border,
            width=1,
        )

        fsize = self.font_size
        if fsize is None:
            if self.kind == "num":
                fsize = 15
            elif self.kind in ("op", "eq"):
                fsize = 15
            else:
                fsize = 12
        weight = "bold" if self.kind in ("num", "op", "eq") or self.active else "normal"
        font = self.fonts.mono(fsize, weight) if self.mono else self.fonts.ui(fsize, weight)

        if self.subtext:
            self.create_text(
                w / 2.0,
                h * 0.26 + dy,
                text=self.subtext,
                fill=self.palette["text_muted"] if not self.active else self.palette["eq_text"],
                font=self.fonts.ui(max(8, fsize - 4)),
            )
            self.create_text(
                w / 2.0,
                h * 0.64 + dy,
                text=self.text,
                fill=fg,
                font=font,
            )
        else:
            self.create_text(
                w / 2.0,
                h / 2.0 + dy,
                text=self.text,
                fill=fg,
                font=font,
            )

    def _on_enter(self, _event: tk.Event) -> None:
        self._hovered = True
        self._redraw()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hovered = False
        self._pressed = False
        self._redraw()

    def _on_press(self, _event: tk.Event) -> None:
        self._pressed = True
        self._redraw()

    def _on_release(self, event: tk.Event) -> None:
        was_pressed = self._pressed
        self._pressed = False
        self._redraw()
        if was_pressed and self.command is not None:
            if 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
                self.command()


class SegmentedBar(tk.Canvas):
    """Modern segmented navigation bar with animated-feel pill selection."""

    def __init__(
        self,
        parent: tk.Widget,
        options: Sequence[Tuple[str, str]],
        selected: str,
        on_change: Callable[[str], None],
        *,
        fonts: FontSet,
        palette: Dict[str, str],
        parent_bg: Optional[str] = None,
        height: int = 38,
        font_size: int = 12,
    ) -> None:
        self.palette = palette
        self.parent_bg = parent_bg or palette["bg"]
        super().__init__(
            parent,
            height=height,
            bg=self.parent_bg,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self.options = list(options)
        self.selected = selected
        self.on_change = on_change
        self.fonts = fonts
        self.font_size = font_size
        self._hover_idx: Optional[int] = None

        self.bind("<Configure>", lambda _e: self._redraw())
        self.bind("<Motion>", self._on_motion)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_click)

    def set_selected(self, key: str) -> None:
        if key != self.selected:
            self.selected = key
            self._redraw()

    def apply_theme(self, palette: Dict[str, str], parent_bg: Optional[str] = None) -> None:
        self.palette = palette
        self.parent_bg = parent_bg or palette["bg"]
        self.configure(bg=self.parent_bg)
        self._redraw()

    def _redraw(self) -> None:
        self.delete("all")
        w = max(40, self.winfo_width())
        h = max(24, self.winfo_height())
        n = max(1, len(self.options))
        p = self.palette

        draw_rounded_rect(self, 1, 1, w - 1, h - 1, h / 2.0, fill=p["surface"], outline=p["card_border"], width=1)
        pad = 4.0
        seg_w = (w - 2 * pad) / n

        for idx, (key, label) in enumerate(self.options):
            x0 = pad + idx * seg_w
            x1 = x0 + seg_w
            is_sel = key == self.selected
            if is_sel:
                draw_rounded_rect(
                    self,
                    x0 + 1,
                    pad,
                    x1 - 1,
                    h - pad,
                    (h - 2 * pad) / 2.0,
                    fill=p["accent"],
                    outline=blend_hex(p["accent"], "#ffffff", 0.2),
                    width=1,
                )
                fg = p["eq_text"]
                weight = "bold"
            elif self._hover_idx == idx:
                draw_rounded_rect(
                    self,
                    x0 + 1,
                    pad,
                    x1 - 1,
                    h - pad,
                    (h - 2 * pad) / 2.0,
                    fill=p["surface_alt"],
                    outline="",
                    width=1,
                )
                fg = p["text"]
                weight = "normal"
            else:
                fg = p["text_sub"]
                weight = "normal"

            self.create_text(
                (x0 + x1) / 2.0,
                h / 2.0,
                text=label,
                fill=fg,
                font=self.fonts.ui(self.font_size, weight),
            )

    def _idx_at(self, x: float) -> int:
        w = max(40, self.winfo_width())
        n = max(1, len(self.options))
        pad = 4.0
        seg_w = (w - 2 * pad) / n
        idx = int((x - pad) // seg_w)
        return max(0, min(n - 1, idx))

    def _on_motion(self, event: tk.Event) -> None:
        idx = self._idx_at(event.x)
        if idx != self._hover_idx:
            self._hover_idx = idx
            self._redraw()

    def _on_leave(self, _event: tk.Event) -> None:
        if self._hover_idx is not None:
            self._hover_idx = None
            self._redraw()

    def _on_click(self, event: tk.Event) -> None:
        idx = self._idx_at(event.x)
        key, _ = self.options[idx]
        if key != self.selected:
            self.selected = key
            self._redraw()
            self.on_change(key)


class RoundedCard(tk.Canvas):
    """Rounded container panel with an interior `self.body` Frame."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        palette: Dict[str, str],
        parent_bg: Optional[str] = None,
        fill_key: str = "surface",
        border_key: str = "card_border",
        radius: int = 16,
        pad_x: int = 14,
        pad_y: int = 12,
    ) -> None:
        self.palette = palette
        self.parent_bg = parent_bg or palette["bg"]
        self.fill_key = fill_key
        self.border_key = border_key
        self.radius = radius
        self.pad_x = pad_x
        self.pad_y = pad_y

        super().__init__(
            parent,
            bg=self.parent_bg,
            bd=0,
            highlightthickness=0,
        )
        self.body = tk.Frame(self, bg=palette[self.fill_key], bd=0, highlightthickness=0)
        self._win_id = self.create_window(pad_x, pad_y, window=self.body, anchor="nw")
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event: tk.Event) -> None:
        w = max(20, event.width)
        h = max(20, event.height)
        self.delete("card_bg")
        bg_id = draw_rounded_rect(
            self,
            1.5,
            1.5,
            w - 1.5,
            h - 1.5,
            self.radius,
            fill=self.palette[self.fill_key],
            outline=self.palette[self.border_key],
            width=1,
            tags=("card_bg",),
        )
        self.tag_lower(bg_id)
        self.coords(self._win_id, self.pad_x, self.pad_y)
        self.itemconfigure(
            self._win_id,
            width=max(4, w - 2 * self.pad_x),
            height=max(4, h - 2 * self.pad_y),
        )

    def apply_theme(self, palette: Dict[str, str], parent_bg: Optional[str] = None) -> None:
        self.palette = palette
        self.parent_bg = parent_bg or palette["bg"]
        self.configure(bg=self.parent_bg)
        self.body.configure(bg=palette[self.fill_key])
        w = max(20, self.winfo_width())
        h = max(20, self.winfo_height())
        self.delete("card_bg")
        bg_id = draw_rounded_rect(
            self,
            1.5,
            1.5,
            w - 1.5,
            h - 1.5,
            self.radius,
            fill=palette[self.fill_key],
            outline=palette[self.border_key],
            width=1,
            tags=("card_bg",),
        )
        self.tag_lower(bg_id)


class StyledEntry(tk.Canvas):
    """Rounded single-line input field with focus glow ring."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        fonts: FontSet,
        palette: Dict[str, str],
        parent_bg: Optional[str] = None,
        initial: str = "",
        font_size: int = 14,
        mono: bool = True,
        height: int = 42,
        justify: str = "left",
        on_change: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.palette = palette
        self.parent_bg = parent_bg or palette["surface"]
        self.fonts = fonts
        self.font_size = font_size
        self.mono = mono
        self._focused = False

        super().__init__(
            parent,
            height=height,
            bg=self.parent_bg,
            bd=0,
            highlightthickness=0,
        )
        self.var = tk.StringVar(value=initial)
        if on_change is not None:
            self.var.trace_add("write", lambda *_: on_change(self.var.get()))

        font = fonts.mono(font_size) if mono else fonts.ui(font_size)
        self.entry = tk.Entry(
            self,
            textvariable=self.var,
            font=font,
            bg=palette["display_bg"],
            fg=palette["text"],
            insertbackground=palette["accent"],
            selectbackground=palette["accent"],
            selectforeground=palette["eq_text"],
            bd=0,
            highlightthickness=0,
            relief="flat",
            justify=justify,
        )
        self._win_id = self.create_window(12, height // 2, window=self.entry, anchor="w")
        self.bind("<Configure>", self._redraw)
        self.bind("<Button-1>", lambda _e: self.entry.focus_set())
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

    def get(self) -> str:
        return self.var.get()

    def set(self, value: str) -> None:
        self.var.set(value)

    def _on_focus_in(self, _e: tk.Event) -> None:
        self._focused = True
        self._redraw()

    def _on_focus_out(self, _e: tk.Event) -> None:
        self._focused = False
        self._redraw()

    def _redraw(self, _event: Optional[tk.Event] = None) -> None:
        w = max(30, self.winfo_width())
        h = max(26, self.winfo_height())
        self.delete("entry_bg")
        border = self.palette["accent"] if self._focused else self.palette["display_border"]
        bg_id = draw_rounded_rect(
            self,
            1.5,
            1.5,
            w - 1.5,
            h - 1.5,
            10,
            fill=self.palette["display_bg"],
            outline=border,
            width=2 if self._focused else 1,
            tags=("entry_bg",),
        )
        self.tag_lower(bg_id)
        self.coords(self._win_id, 12, h / 2.0)
        self.itemconfigure(self._win_id, width=max(10, w - 24))

    def apply_theme(self, palette: Dict[str, str], parent_bg: Optional[str] = None) -> None:
        self.palette = palette
        self.parent_bg = parent_bg or palette["surface"]
        self.configure(bg=self.parent_bg)
        self.entry.configure(
            bg=palette["display_bg"],
            fg=palette["text"],
            insertbackground=palette["accent"],
            selectbackground=palette["accent"],
            selectforeground=palette["eq_text"],
        )
        self._redraw()


class DropdownPill(tk.Canvas):
    """Themed custom dropdown button with searchable floating popover list."""

    def __init__(
        self,
        parent: tk.Widget,
        items: Sequence[Tuple[str, str]],
        selected_key: str,
        on_select: Callable[[str], None],
        *,
        fonts: FontSet,
        palette: Dict[str, str],
        parent_bg: Optional[str] = None,
        height: int = 40,
        font_size: int = 12,
    ) -> None:
        self.palette = palette
        self.parent_bg = parent_bg or palette["surface"]
        self.fonts = fonts
        self.font_size = font_size
        self.items: List[Tuple[str, str]] = list(items)
        self.selected_key = selected_key
        self.on_select = on_select
        self._hovered = False
        self._popup: Optional[tk.Toplevel] = None

        super().__init__(
            parent,
            height=height,
            bg=self.parent_bg,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self.bind("<Configure>", lambda _e: self._redraw())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", lambda _e: self._toggle_popup())

    def set_items(self, items: Sequence[Tuple[str, str]], selected_key: Optional[str] = None) -> None:
        self.items = list(items)
        if selected_key is not None:
            self.selected_key = selected_key
        elif self.items and not any(k == self.selected_key for k, _ in self.items):
            self.selected_key = self.items[0][0]
        self._redraw()

    def set_selected(self, key: str) -> None:
        self.selected_key = key
        self._redraw()

    def get_selected(self) -> str:
        return self.selected_key

    def _current_label(self) -> str:
        for k, lbl in self.items:
            if k == self.selected_key:
                return lbl
        return self.selected_key

    def apply_theme(self, palette: Dict[str, str], parent_bg: Optional[str] = None) -> None:
        self.palette = palette
        self.parent_bg = parent_bg or palette["surface"]
        self.configure(bg=self.parent_bg)
        self._redraw()

    def _on_enter(self, _e: tk.Event) -> None:
        self._hovered = True
        self._redraw()

    def _on_leave(self, _e: tk.Event) -> None:
        self._hovered = False
        self._redraw()

    def _redraw(self) -> None:
        self.delete("all")
        w = max(60, self.winfo_width())
        h = max(26, self.winfo_height())
        p = self.palette
        fill = p["surface_hi"] if self._hovered else p["surface_alt"]
        border = p["accent"] if self._popup is not None else p["card_border"]
        draw_rounded_rect(self, 1.5, 1.5, w - 1.5, h - 1.5, 10, fill=fill, outline=border, width=1)
        self.create_text(
            14,
            h / 2.0,
            text=self._current_label(),
            anchor="w",
            fill=p["text"],
            font=self.fonts.ui(self.font_size, "bold"),
        )
        # Crisp vector chevron
        cx = w - 18
        cy = h / 2.0
        self.create_line(
            cx - 5, cy - 2, cx, cy + 3, cx + 5, cy - 2,
            fill=p["accent"],
            width=2,
            capstyle="round",
            joinstyle="round",
        )

    def _close_popup(self) -> None:
        if self._popup is not None:
            try:
                self._popup.destroy()
            except Exception:
                pass
            self._popup = None
            self._redraw()

    def _toggle_popup(self) -> None:
        if self._popup is not None:
            self._close_popup()
            return
        if not self.items:
            return

        p = self.palette
        pop = tk.Toplevel(self)
        pop.wm_overrideredirect(True)
        pop.configure(bg=p["card_border"])
        try:
            pop.attributes("-topmost", True)
        except Exception:
            pass
        self._popup = pop
        self._redraw()

        outer = tk.Frame(pop, bg=p["surface"], bd=0, highlightthickness=1, highlightbackground=p["accent"])
        outer.pack(fill="both", expand=True)

        filter_var = tk.StringVar()
        if len(self.items) > 7:
            search_wrap = tk.Frame(outer, bg=p["surface"], padx=8, pady=6)
            search_wrap.pack(fill="x")
            search_entry = tk.Entry(
                search_wrap,
                textvariable=filter_var,
                font=self.fonts.ui(11),
                bg=p["display_bg"],
                fg=p["text"],
                insertbackground=p["accent"],
                bd=0,
                highlightthickness=1,
                highlightbackground=p["card_border"],
                highlightcolor=p["accent"],
                relief="flat",
            )
            search_entry.pack(fill="x", ipady=4)
            search_entry.focus_set()
        else:
            search_entry = None

        list_canvas = tk.Canvas(
            outer,
            bg=p["surface"],
            bd=0,
            highlightthickness=0,
            height=min(280, len(self.items) * 32 + 6),
        )
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=list_canvas.yview)
        list_canvas.configure(yscrollcommand=scrollbar.set)
        if len(self.items) > 8:
            scrollbar.pack(side="right", fill="y")
        list_canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(list_canvas, bg=p["surface"])
        inner_win = list_canvas.create_window((0, 0), window=inner, anchor="nw")
        list_canvas.bind("<Configure>", lambda e: list_canvas.itemconfigure(inner_win, width=e.width))
        inner.bind("<Configure>", lambda _e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))

        def _wheel(ev: tk.Event) -> None:
            if getattr(ev, "num", None) == 4:
                list_canvas.yview_scroll(-1, "units")
            elif getattr(ev, "num", None) == 5:
                list_canvas.yview_scroll(1, "units")
            elif ev.delta:
                step = -1 if ev.delta > 0 else 1
                if abs(ev.delta) >= 120:
                    step = int(-ev.delta / 120)
                list_canvas.yview_scroll(step, "units")

        pop.bind("<MouseWheel>", _wheel)
        pop.bind("<Button-4>", _wheel)
        pop.bind("<Button-5>", _wheel)
        pop.bind("<Escape>", lambda _e: self._close_popup())

        def _populate() -> None:
            for child in inner.winfo_children():
                child.destroy()
            q = filter_var.get().strip().lower()
            shown = [it for it in self.items if not q or q in it[1].lower() or q in it[0].lower()]
            for key, lbl in shown:
                is_cur = key == self.selected_key
                row_bg = p["op_btn"] if is_cur else p["surface"]
                row = tk.Label(
                    inner,
                    text=lbl,
                    anchor="w",
                    padx=12,
                    pady=6,
                    bg=row_bg,
                    fg=p["accent_hover"] if is_cur and p["bg"].startswith("#0") else (p["accent"] if is_cur else p["text"]),
                    font=self.fonts.ui(11, "bold" if is_cur else "normal"),
                    cursor="hand2",
                )
                row.pack(fill="x")

                def _enter(_e: tk.Event, r: tk.Label = row, cur: bool = is_cur) -> None:
                    if not cur:
                        r.configure(bg=p["surface_hi"])

                def _leave(_e: tk.Event, r: tk.Label = row, cur: bool = is_cur) -> None:
                    if not cur:
                        r.configure(bg=p["surface"])

                def _pick(_e: tk.Event, k: str = key) -> None:
                    self.selected_key = k
                    self._close_popup()
                    self.on_select(k)

                row.bind("<Enter>", _enter)
                row.bind("<Leave>", _leave)
                row.bind("<ButtonRelease-1>", _pick)

            list_canvas.update_idletasks()
            new_h = min(280, max(36, len(shown) * 32 + 4))
            list_canvas.configure(height=new_h)

        filter_var.trace_add("write", lambda *_: _populate())
        _populate()

        pop.update_idletasks()
        bx = self.winfo_rootx()
        by = self.winfo_rooty() + self.winfo_height() + 4
        pw = max(self.winfo_width(), 240)
        ph = pop.winfo_reqheight()
        screen_h = self.winfo_screenheight()
        if by + ph > screen_h - 40:
            by = max(20, self.winfo_rooty() - ph - 4)
        pop.geometry(f"{pw}x{ph}+{bx}+{by}")
        if search_entry is None:
            pop.focus_force()

        def _check_focus_out(ev: tk.Event) -> None:
            if self._popup is None:
                return
            focused = pop.focus_get()
            if focused is None or str(focused) == "" or not str(focused).startswith(str(pop)):
                self.after(80, self._maybe_close_if_unfocused)

        pop.bind("<FocusOut>", _check_focus_out)

    def _maybe_close_if_unfocused(self) -> None:
        if self._popup is None:
            return
        try:
            focused = self._popup.focus_get()
            if focused is None or not str(focused).startswith(str(self._popup)):
                self._close_popup()
        except Exception:
            self._close_popup()


class ScrollableFrame(tk.Frame):
    """Vertical scrollable container with smooth mousewheel support."""

    def __init__(self, parent: tk.Widget, *, bg: str) -> None:
        super().__init__(parent, bg=bg, bd=0, highlightthickness=0)
        self.canvas = tk.Canvas(self, bg=bg, bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=bg, bd=0, highlightthickness=0)
        self._win_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._win_id, width=e.width))
        self.inner.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.bind("<Enter>", self._bind_wheel)
        self.canvas.bind("<Leave>", self._unbind_wheel)

    def apply_bg(self, bg: str) -> None:
        self.configure(bg=bg)
        self.canvas.configure(bg=bg)
        self.inner.configure(bg=bg)

    def _on_wheel(self, event: tk.Event) -> None:
        if getattr(event, "num", None) == 4:
            self.canvas.yview_scroll(-1, "units")
        elif getattr(event, "num", None) == 5:
            self.canvas.yview_scroll(1, "units")
        elif event.delta:
            step = -1 if event.delta > 0 else 1
            if abs(event.delta) >= 120:
                step = int(-event.delta / 120)
            self.canvas.yview_scroll(step, "units")

    def _bind_wheel(self, _e: tk.Event) -> None:
        if sys.platform == "linux":
            self.canvas.bind_all("<Button-4>", self._on_wheel)
            self.canvas.bind_all("<Button-5>", self._on_wheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self._on_wheel)

    def _unbind_wheel(self, _e: tk.Event) -> None:
        if sys.platform == "linux":
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")
