"""Theme palettes, color math, and cross-platform typography helpers."""

from __future__ import annotations

import tkinter.font as tkfont
from typing import Dict, Tuple

THEMES: Dict[str, Dict[str, str]] = {
    "Midnight Obsidian": {
        "bg": "#0b0e17",
        "bg_alt": "#111625",
        "surface": "#161c2e",
        "surface_alt": "#1d253d",
        "surface_hi": "#263152",
        "card_border": "#293556",
        "display_bg": "#0e1322",
        "display_border": "#2e3d66",
        "text": "#f3f6ff",
        "text_sub": "#9aa8c7",
        "text_muted": "#647396",
        "accent": "#6c8cff",
        "accent_hover": "#84a0ff",
        "accent_glow": "#3b5bdb",
        "secondary": "#2dd4bf",
        "secondary_hover": "#5eead4",
        "tertiary": "#f59e0b",
        "danger": "#fb7185",
        "danger_hover": "#fda4af",
        "success": "#34d399",
        "num_btn": "#1c243b",
        "num_btn_hover": "#263150",
        "fn_btn": "#151b2d",
        "fn_btn_hover": "#202944",
        "op_btn": "#263563",
        "op_btn_hover": "#334785",
        "eq_btn": "#5472ff",
        "eq_btn_hover": "#6e88ff",
        "eq_text": "#ffffff",
        "grid_major": "#1e2946",
        "grid_minor": "#141b30",
        "axis": "#5a6d99",
        "plot_1": "#38bdf8",
        "plot_2": "#f472b6",
        "plot_3": "#34d399",
    },
    "Aurora Cyber": {
        "bg": "#091216",
        "bg_alt": "#0e1b22",
        "surface": "#12232c",
        "surface_alt": "#182f3b",
        "surface_hi": "#213f4f",
        "card_border": "#25495c",
        "display_bg": "#0b171d",
        "display_border": "#2b596e",
        "text": "#ecfeff",
        "text_sub": "#92bdc9",
        "text_muted": "#5b8591",
        "accent": "#14b8a6",
        "accent_hover": "#2dd4bf",
        "accent_glow": "#0f766e",
        "secondary": "#a855f7",
        "secondary_hover": "#c084fc",
        "tertiary": "#facc15",
        "danger": "#f43f5e",
        "danger_hover": "#fb7185",
        "success": "#4ade80",
        "num_btn": "#172d38",
        "num_btn_hover": "#203e4d",
        "fn_btn": "#102028",
        "fn_btn_hover": "#18303c",
        "op_btn": "#1c4352",
        "op_btn_hover": "#26596d",
        "eq_btn": "#0d9488",
        "eq_btn_hover": "#14b8a6",
        "eq_text": "#ffffff",
        "grid_major": "#1b3744",
        "grid_minor": "#11242d",
        "axis": "#538699",
        "plot_1": "#2dd4bf",
        "plot_2": "#e879f9",
        "plot_3": "#facc15",
    },
    "Solar Ivory": {
        "bg": "#f2f4f9",
        "bg_alt": "#e7ebf4",
        "surface": "#ffffff",
        "surface_alt": "#eef2fa",
        "surface_hi": "#dfe6f5",
        "card_border": "#d0d9ec",
        "display_bg": "#f8faff",
        "display_border": "#c3d0ea",
        "text": "#121829",
        "text_sub": "#4c5978",
        "text_muted": "#7d8ba8",
        "accent": "#3b5bdb",
        "accent_hover": "#4c6ef5",
        "accent_glow": "#dbe4ff",
        "secondary": "#0ca678",
        "secondary_hover": "#12b886",
        "tertiary": "#d97706",
        "danger": "#e11d48",
        "danger_hover": "#f43f5e",
        "success": "#059669",
        "num_btn": "#f7f9fe",
        "num_btn_hover": "#e8eefb",
        "fn_btn": "#edf1fa",
        "fn_btn_hover": "#dde5f6",
        "op_btn": "#dfe7fb",
        "op_btn_hover": "#cddafa",
        "eq_btn": "#3b5bdb",
        "eq_btn_hover": "#4c6ef5",
        "eq_text": "#ffffff",
        "grid_major": "#dce3f2",
        "grid_minor": "#edf1f9",
        "axis": "#7d8ba8",
        "plot_1": "#2563eb",
        "plot_2": "#db2777",
        "plot_3": "#059669",
    },
}

THEME_ORDER = ["Midnight Obsidian", "Aurora Cyber", "Solar Ivory"]


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    c = hex_color.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{max(0, min(255, int(r))):02x}{max(0, min(255, int(g))):02x}{max(0, min(255, int(b))):02x}"


def blend_hex(c1: str, c2: str, t: float) -> str:
    t = max(0.0, min(1.0, float(t)))
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex(
        round(r1 + (r2 - r1) * t),
        round(g1 + (g2 - g1) * t),
        round(b1 + (b2 - b1) * t),
    )


class FontSet:
    """Resolves the cleanest UI and monospace fonts available on the host OS."""

    def __init__(self) -> None:
        try:
            avail = set(tkfont.families())
        except Exception:
            avail = set()

        ui_candidates = [
            "Avenir Next",
            "SF Pro Display",
            "Helvetica Neue",
            "Segoe UI",
            "Inter",
            "Helvetica",
            "Arial",
        ]
        mono_candidates = [
            "SF Mono",
            "JetBrains Mono",
            "Menlo",
            "Consolas",
            "Monaco",
            "Courier New",
        ]

        self.ui_family = next((f for f in ui_candidates if f in avail), "Helvetica")
        self.mono_family = next((f for f in mono_candidates if f in avail), "Courier")

    def ui(self, size: int = 12, weight: str = "normal") -> tuple:
        if weight == "normal":
            return (self.ui_family, size)
        return (self.ui_family, size, weight)

    def mono(self, size: int = 13, weight: str = "normal") -> tuple:
        if weight == "normal":
            return (self.mono_family, size)
        return (self.mono_family, size, weight)
