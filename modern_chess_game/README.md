# Modern Chess (ModernGL + Pygame + NumPy + OOP)

A modern, hardware-accelerated chess game built with **OpenGL 3.3 Core (ModernGL)**, **Pygame**, and **NumPy**, refactored from Python Turtle into a clean, modular **Object-Oriented (OOP)** architecture.

---

## ✨ Features

- **⚡ Hardware-Accelerated Rendering (ModernGL & GLSL Shaders)**:
  - Custom GLSL shaders for anti-aliased rounded squares, soft drop shadows, and glowing selection rings.
  - Linear mipmapped texture filtering for crisp high-resolution piece scaling.
  - Pulsing radial glow shader for Kings in check.
- **🎨 Modern Visuals & Themes**:
  - **Cyber Blue** (sleek dark aesthetic preserving the original `#18242b` and `#84c9FB` board colors).
  - **Neo Emerald** (clean tournament green/cream palette).
  - **Midnight Slate** (contemporary monochrome slate).
  - Cycle themes anytime in-game with the `[T]` key!
- **🧩 Smooth Eased Animations**:
  - Moving pieces glide across the board with cubic ease-out interpolation curves.
- **🖱️ Intuitive Controls**:
  - **Drag & Drop**: Click and drag pieces with elevated 3D drop-shadow feedback.
  - **Click-to-Move**: Click a piece to select, then click any destination dot or capture ring.
  - **Interactive Promotion Dialog**: Floating promotion selector when pawns reach the back rank.
- **🔊 Procedural Sound Synthesis (NumPy + Pygame Mixer)**:
  - 100% self-contained procedural audio: piece drop thud, capture snap, castling whoosh, and check bell chimes synthesized on-the-fly.
- **👑 Full Chess Rules Support**:
  - En-passant captures.
  - Both Kingside (`O-O`) and Queenside (`O-O-O`) castling with through-check validation.
  - Absolute pin detection & king safety checks.
  - Pawn promotion to Queen, Rook, Bishop, or Knight.
  - Checkmate, stalemate, and move log tracking in standard algebraic notation.
- **⏪ Undo / Redo & Board Flipping**:
  - Press `[U]` or `[Ctrl+Z]` / `[Cmd+Z]` to undo moves.
  - Press `[F]` to manually flip the board view or `[A]` to toggle auto-flipping per turn.

---

## 🏗️ Architecture & OOP Design

```text
modern_chess_game/
├── core/
│   ├── constants.py      # Enums (Color, PieceType), window dimensions, color palettes
│   ├── piece.py          # Abstract Piece class & subclasses (Pawn, Knight, Bishop, Rook, Queen, King)
│   ├── move.py           # Move dataclass with algebraic notation generation (SAN)
│   └── board.py          # Board state, legal move generation, pin/check validation, undo stack
├── graphics/
│   ├── shaders.py        # GLSL Vertex & Fragment shaders (SDF circles, quads, rounded rects)
│   ├── texture.py        # ModernGL texture caching with mipmaps from PNG & Pygame surfaces
│   └── renderer.py       # OpenGL VAO/VBO batching with NumPy, interpolation, and UI rendering
├── audio/
│   └── sound_manager.py  # Procedural audio generator using NumPy waveform synthesis
├── game.py               # Game state controller, mouse/keyboard event handler
├── main.py               # Application entry point with 60 FPS GL event loop
└── requirements.txt      # Dependencies
```

---

## 🚀 How to Run

1. Activate your virtual environment:
   ```bash
   source /Users/ramrupsatpati/Desktop/Python/venv/bin/activate
   ```

2. Navigate to the project directory:
   ```bash
   cd /Users/ramrupsatpati/Desktop/Python/modern_chess_game
   ```

3. Launch the game:
   ```bash
   python main.py
   ```

---

## ⌨️ Controls & Shortcuts

| Key / Action | Description |
|---|---|
| **Left Click / Drag** | Select, drag, and move pieces |
| **`[F]`** | Flip the board (White ⟷ Black perspective) |
| **`[A]`** | Toggle Auto-Flip on every turn (like original Turtle game) |
| **`[T]`** | Cycle visual theme (Cyber Blue, Neo Emerald, Midnight Slate) |
| **`[U]` / `[Ctrl+Z]`** | Undo last move |
| **`[R]`** | Reset / Start a new game |
| **`[Esc]`** | Deselect current piece |
