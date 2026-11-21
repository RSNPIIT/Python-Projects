# 💣 Modern Minesweeper (Python Tkinter & OOP)

A modern, arcade-grade Minesweeper game built in **Python 3** and **Tkinter**, engineered from the ground up with **pure Object-Oriented Programming (OOP)**, crisp procedural vector graphics, authentic 7-segment digital LED displays, an emotive mascot, and an intelligent deduction hint engine.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with Tkinter (`python3 -c "import tkinter"`)
- macOS, Linux, or Windows

### Launch with Protected Runner
```bash
cd /Users/ramrupsatpati/Desktop/Python/minesweeper_game
./run.sh
```

Or directly via Python:
```bash
python3 main.py
```

> **Terminal Protection**: `run.sh` isolates terminal signals (`Ctrl+C`, `Ctrl+Z`, `Ctrl+\`, `Ctrl+D`) to prevent the terminal from corrupting or freezing during gameplay, and automatically restores terminal state (`stty sane`, cursor visibility, alternate screen buffer) upon exit.

---

## 🎮 Controls & Shortcuts

| Action | Control | Description |
| :--- | :--- | :--- |
| **Probe Tile** | `Left Click` | Uncover hidden tile. Guaranteed safe opening on move 1. |
| **Flag / Mark** | `Right Click` / `Two-finger tap` | Cycle `🚩 Flag` ➔ `❓ Question` ➔ `Clear`. |
| **Chording** | `Double Click` / `Middle Click` | On revealed numbers, clears all unflagged neighbors if flags match the number. |
| **New Game** | `F2` / `R` / `Mascot Face` | Resets the minefield for a fresh round. |
| **Smart Hint** | `H` | Calculates 100% deterministic deduction (shows safe tile or mine with explanation). |
| **Toggle Audio** | `M` | Mute / Unmute procedural 8-bit sound effects. |
| **Pause / Resume** | `P` | Pauses timer and hides the field. |
| **Dismiss Hint** | `ESC` | Clears active hint highlight. |

---

## 🌟 Key Features

1. **Guaranteed Safe Opening**: The first click is mathematically guaranteed never to be a mine and will always trigger an opening cascade.
2. **Authentic 7-Segment Digital Meters**: Custom vector-rendered LED counters for remaining mines and elapsed time.
3. **Emotive Animated Mascot**:
   - 🙂 Normal gameplay
   - 😮 Suspense when mouse is pressed down on an unrevealed tile
   - 😎 Cool sunglasses on victory
   - 😵 Crossed-out eyes on detonation
   - 😇 Halo when protected by defusal shield
4. **Intelligent Deduction Solver (`Solver`)**:
   - Analyzes revealed numbered constraints and subset intersections.
   - Proves mathematically whether a move is 100% safe without guessing, or points out a definite mine.
5. **Game Modes**:
   - **Classic**: Traditional 1-life high-stakes play.
   - **Shield Mode**: Grants 1 emergency defusal shield, saving the player from the first accidental mine detonation.
6. **Difficulty Presets & Custom Field**:
   - **Beginner**: 9 × 9 grid, 10 mines
   - **Intermediate**: 16 × 16 grid, 40 mines
   - **Expert**: 16 × 30 grid, 99 mines
   - **Master**: 20 × 30 grid, 130 mines
   - **Custom**: Configure height (8–40), width (8–50), and mine count.
7. **Procedural 8-Bit Audio Engine**:
   - Generates retro WAV sound effects on the fly with zero external dependencies (clicks, chimes, cascades, chords, explosions, and victory fanfares).
8. **Multiple Color Themes**:
   - **Cyber Dark**: Sleek slate with neon cyan, purple, and emerald accents.
   - **Classic Retro**: Nostalgic Win95/Win98 beveled gray aesthetic with red digital LEDs.
   - **Nordic Frost**: Arctic Scandinavian blue and crisp snow tones.
   - **Emerald Matrix**: High-contrast cyberpunk green phosphor terminal style.
9. **Competitive Metrics**:
   - Calculates **3BV** (Bechtel's Board Benchmark Value) and 3BV/s efficiency rating.
   - High score persistence stored locally in `~/.minesweeper_records.json`.

---

## 🏛️ Object-Oriented Architecture

```
                    +--------------------+
                    |     MainWindow     |
                    +---------+----------+
                              │
          ┌───────────────────┼────────────────────┐
          ▼                   ▼                    ▼
   +--------------+    +--------------+    +---------------+
   |    Board     |    |  GridCanvas  |    |  SoundEngine  |
   +-------+------+    +--------------+    +---------------+
           │                  │                    │
           ▼                  ▼                    ▼
   +--------------+    +--------------+    +---------------+
   |     Cell     |    |  LCDDisplay  |    |     Solver    |
   +--------------+    +--------------+    +---------------+
                              │
                              ▼
                       +--------------+
                       |  FaceButton  |
                       +--------------+
```

### Module Breakdown:
- **[`src/core/cell.py`](file:///Users/ramrupsatpati/Desktop/Python/minesweeper_game/src/core/cell.py)**: Encapsulates individual cell properties (`is_mine`, `is_revealed`, `state`, `neighbor_mines`, `exploded`, `wrong_flag`).
- **[`src/core/board.py`](file:///Users/ramrupsatpati/Desktop/Python/minesweeper_game/src/core/board.py)**: Coordinates grid logic, first-click safety, breadth-first search (BFS) cascading flood-fills, chording, win checks, and 3BV calculations.
- **[`src/core/solver.py`](file:///Users/ramrupsatpati/Desktop/Python/minesweeper_game/src/core/solver.py)**: Constraint propagation solver for zero-guessing hints.
- **[`src/core/game_state.py`](file:///Users/ramrupsatpati/Desktop/Python/minesweeper_game/src/core/game_state.py)**: State machine, difficulty presets, and JSON high score records.
- **[`src/audio/sound_engine.py`](file:///Users/ramrupsatpati/Desktop/Python/minesweeper_game/src/audio/sound_engine.py)**: Procedural synthesizer generating 16-bit PCM WAV audio assets in background threads.
- **[`src/ui/lcd_display.py`](file:///Users/ramrupsatpati/Desktop/Python/minesweeper_game/src/ui/lcd_display.py)**: Canvas-based 7-segment digital meters.
- **[`src/ui/face_button.py`](file:///Users/ramrupsatpati/Desktop/Python/minesweeper_game/src/ui/face_button.py)**: Interactive emotive mascot with live facial feedback.
- **[`src/ui/grid_canvas.py`](file:///Users/ramrupsatpati/Desktop/Python/minesweeper_game/src/ui/grid_canvas.py)**: Canvas board renderer with tile hover highlights, vector flag rendering, and animated confetti celebration.
- **[`src/ui/dialogs.py`](file:///Users/ramrupsatpati/Desktop/Python/minesweeper_game/src/ui/dialogs.py)**: Modal dialogs for custom field configuration, career statistics, and victory summaries.
- **[`src/ui/main_window.py`](file:///Users/ramrupsatpati/Desktop/Python/minesweeper_game/src/ui/main_window.py)**: Top-level coordinator binding input events, menus, and state.
