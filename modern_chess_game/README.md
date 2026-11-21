# Modern Chess (ModernGL + Pygame + NumPy + OOP)

A modern, hardware-accelerated chess game built with **OpenGL 3.3 Core (ModernGL)**, **Pygame**, and **NumPy**, featuring both **Human vs Human (PvP)** and **Human vs AI (PvE)** modes with a clean, modular **Object-Oriented (OOP)** architecture.

---

## ✨ Features

- **🤖 Human vs Computer (AI) & Human vs Human Modes**:
  - **Human vs AI**: Play against an intelligent Minimax engine with Alpha-Beta pruning, Piece-Square Table (PST) positional heuristics, and capture move ordering.
  - **Non-blocking Multithreading**: AI calculates its moves on a background worker thread so the 60 FPS hardware rendering loop never freezes.
  - **3 Difficulty Tiers**:
    - **Easy**: Fast moves with occasional casual choices.
    - **Medium**: Depth 2 tactical search with positional evaluation.
    - **Hard**: Depth 3 deep tactical search with Alpha-Beta pruning.
  - **Human vs Human**: Classic local two-player pass-and-play.
  - Toggle game mode anytime with the `[M]` key or clicking the **Mode button** in the side panel!
- **⚡ Hardware-Accelerated ModernGL Rendering & Shaders**:
  - Custom GLSL shaders for anti-aliased rounded squares, soft drop shadows, and glowing selection rings.
  - Linear mipmapped texture filtering for crisp high-resolution piece scaling.
  - Pulsing radial glow shader for Kings in check.
- **🎨 Modern Visuals & Themes**:
  - **Cyber Blue** (sleek dark aesthetic preserving original `#18242b` and `#84c9FB` board colors).
  - **Neo Emerald** (clean tournament green/cream palette).
  - **Midnight Slate** (contemporary monochrome slate).
  - Cycle themes anytime in-game with the `[T]` key!
- **🧩 Smooth Eased Animations**:
  - Moving pieces glide across the board with cubic ease-out interpolation curves.
- **🖱️ Tactile Controls**:
  - **Drag & Drop**: Click and drag pieces with elevated 3D drop-shadow feedback.
  - **Click-to-Move**: Click a piece to select, then click any destination dot or capture ring.
  - **Interactive Promotion Dialog**: Floating promotion selector when pawns reach the back rank.
- **🔊 Procedural Audio Synthesis (NumPy + Pygame Mixer)**:
  - 100% self-contained procedural audio: piece drop thud, capture snap, castling whoosh, and check bell chimes synthesized on-the-fly.
- **🛡️ Graceful Exit with Quit Confirmation Dialog**:
  - Pressing `Cmd+Q`, `Alt+F4`, `Esc`, or clicking the window cross (`X`) triggers a sleek modal dialog: *"Are you sure you want to quit?"* with `[YES, QUIT]` and `[CANCEL]`.
- **⏪ Smart Undo / Redo & Board Flipping**:
  - In Human vs AI mode, pressing `[U]` / `[Ctrl+Z]` automatically undoes both the AI move and your move so you can try another line.
  - Press `[F]` to flip the board view or `[A]` to toggle auto-flipping per turn.

---

## 🕹️ Controls & Shortcuts

| Key / Action | Description |
|---|---|
| **Left Click / Drag** | Select, drag, and move pieces |
| **`[M]`** | Toggle Mode (`Human vs AI` ⟷ `Human vs Human`) |
| **`[D]`** | Cycle AI Difficulty (`Easy` → `Medium` → `Hard`) |
| **`[F]`** | Flip the board view (White ⟷ Black) |
| **`[A]`** | Toggle Auto-Flip on every turn |
| **`[T]`** | Cycle visual theme (Cyber Blue, Neo Emerald, Midnight Slate) |
| **`[U]` / `[Ctrl+Z]`** | Undo move (undoes both AI and player in PvE mode) |
| **`[R]`** | Reset / Start a new game |
| **`[Esc]` / `Cmd+Q`** | Open Quit Confirmation Dialog |

---

## 🚀 How to Run

```bash
cd /Users/ramrupsatpati/Desktop/Python/modern_chess_game
/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py
```
