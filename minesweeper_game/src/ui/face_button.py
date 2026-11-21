"""
face_button.py - Animated Mascot Face Button (🙂, 😮, 😎, 😵).
Provides emotive visual feedback during clicks, victory, and explosions.
"""

import tkinter as tk
from typing import Callable, Optional


class FaceState:
    NORMAL = "normal"      # 🙂
    SUSPENSE = "suspense"  # 😮
    WON = "won"            # 😎
    LOST = "lost"          # 😵
    SHIELD = "shield"      # 😇


class FaceButton(tk.Canvas):
    """Custom canvas-rendered emotive restart button."""

    def __init__(self, parent, command: Optional[Callable] = None, size: int = 40, **kwargs):
        super().__init__(parent, width=size, height=size, highlightthickness=0, bg="#1e293b", **kwargs)
        self.size = size
        self.command = command
        self.state = FaceState.NORMAL
        self.is_pressed = False
        self.is_hovered = False

        self.bg_color = "#334155"
        self.border_color = "#475569"

        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        self.draw()

    def set_theme(self, bg_panel: str, tile_border: str):
        self.bg_color = bg_panel
        self.border_color = tile_border
        self.configure(bg=bg_panel)
        self.draw()

    def set_face_state(self, state: str):
        if self.state != state:
            self.state = state
            self.draw()

    def _on_enter(self, _):
        self.is_hovered = True
        self.draw()

    def _on_leave(self, _):
        self.is_hovered = False
        self.is_pressed = False
        self.draw()

    def _on_press(self, _):
        self.is_pressed = True
        self.draw()

    def _on_release(self, _):
        if self.is_pressed and self.is_hovered:
            self.is_pressed = False
            self.draw()
            if self.command:
                self.command()
        self.is_pressed = False

    def draw(self):
        self.delete("all")
        s = self.size
        cx, cy = s // 2, s // 2
        r = s // 2 - 4

        # Button bevel / background
        offset = 1 if self.is_pressed else 0
        btn_bg = "#475569" if (self.is_hovered and not self.is_pressed) else "#1e293b"
        self.create_rectangle(1, 1, s - 1, s - 1, fill=btn_bg, outline=self.border_color, width=2)

        # Yellow Face Circle
        face_cx = cx + offset
        face_cy = cy + offset
        self.create_oval(face_cx - r, face_cy - r, face_cx + r, face_cy + r, fill="#fbbf24", outline="#d97706", width=1.5)

        # Emotive Facial Features
        if self.state == FaceState.NORMAL:
            # Normal Smile 🙂
            # Eyes
            self.create_oval(face_cx - 6, face_cy - 5, face_cx - 3, face_cy - 2, fill="#1e293b", outline="")
            self.create_oval(face_cx + 3, face_cy - 5, face_cx + 6, face_cy - 2, fill="#1e293b", outline="")
            # Smile Arc
            self.create_arc(face_cx - 7, face_cy - 3, face_cx + 7, face_cy + 8, start=200, extent=140, style="arc", width=2, outline="#1e293b")

        elif self.state == FaceState.SUSPENSE:
            # Suspense / Mouse down 😮
            # Wide Eyes
            self.create_oval(face_cx - 7, face_cy - 6, face_cx - 3, face_cy - 2, fill="#1e293b", outline="")
            self.create_oval(face_cx + 3, face_cy - 6, face_cx + 7, face_cy - 2, fill="#1e293b", outline="")
            # Open 'O' Mouth
            self.create_oval(face_cx - 3, face_cy + 2, face_cx + 3, face_cy + 8, fill="#1e293b", outline="")

        elif self.state == FaceState.WON:
            # Cool Sunglasses 😎
            # Glasses frames
            self.create_polygon([face_cx - 9, face_cy - 5, face_cx - 2, face_cy - 5, face_cx - 3, face_cy + 1, face_cx - 8, face_cy + 1], fill="#0f172a")
            self.create_polygon([face_cx + 2, face_cy - 5, face_cx + 9, face_cy - 5, face_cx + 8, face_cy + 1, face_cx + 3, face_cy + 1], fill="#0f172a")
            # Bridge
            self.create_line(face_cx - 3, face_cy - 4, face_cx + 3, face_cy - 4, fill="#0f172a", width=2)
            # White lens glints
            self.create_line(face_cx - 7, face_cy - 3, face_cx - 5, face_cy - 3, fill="#ffffff", width=1)
            self.create_line(face_cx + 4, face_cy - 3, face_cx + 6, face_cy - 3, fill="#ffffff", width=1)
            # Smug Grin
            self.create_arc(face_cx - 6, face_cy + 1, face_cx + 6, face_cy + 8, start=220, extent=100, style="arc", width=2, outline="#1e293b")

        elif self.state == FaceState.LOST:
            # Dead 'X' Eyes 😵
            # Left Eye 'X'
            self.create_line(face_cx - 6, face_cy - 6, face_cx - 2, face_cy - 2, fill="#dc2626", width=2)
            self.create_line(face_cx - 2, face_cy - 6, face_cx - 6, face_cy - 2, fill="#dc2626", width=2)
            # Right Eye 'X'
            self.create_line(face_cx + 2, face_cy - 6, face_cx + 6, face_cy - 2, fill="#dc2626", width=2)
            self.create_line(face_cx + 6, face_cy - 6, face_cx + 2, face_cy - 2, fill="#dc2626", width=2)
            # Frown Arc
            self.create_arc(face_cx - 7, face_cy + 4, face_cx + 7, face_cy + 13, start=30, extent=120, style="arc", width=2, outline="#1e293b")

        elif self.state == FaceState.SHIELD:
            # Angel / Halo 😇
            # Halo
            self.create_oval(face_cx - 7, face_cy - 12, face_cx + 7, face_cy - 8, outline="#38bdf8", width=2)
            # Gentle Eyes
            self.create_oval(face_cx - 6, face_cy - 5, face_cx - 3, face_cy - 2, fill="#1e293b", outline="")
            self.create_oval(face_cx + 3, face_cy - 5, face_cx + 6, face_cy - 2, fill="#1e293b", outline="")
            # Smile
            self.create_arc(face_cx - 5, face_cy - 2, face_cx + 5, face_cy + 7, start=200, extent=140, style="arc", width=2, outline="#1e293b")
