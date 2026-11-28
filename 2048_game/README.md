# 2048 - Classic Number Puzzle Game

A modern, high-performance desktop recreation of the classic **2048** puzzle game built with **Pygame** and **NumPy**.

Join identical tiles to combine them in hope of reaching **2048** and beyond!

---

## ✨ Features

- **Silky-Smooth 60 FPS Visuals**:
  - Ease-out cubic sliding animations when tiles move.
  - Scale-up elastic pop when new tiles spawn.
  - Radiant pulse bounce when two tiles merge.
  - Subtle golden radiant glow for high-tier tiles ($128, 256, 512, 1024, 2048+$).
- **Light & Dark Themes**:
  - Classic warm cream palette (`#FAF8EF`).
  - Sleek midnight navy dark mode (`#1A1B26`).
  - Instant toggle via **`[T]`** key or header button.
- **Procedural Audio Engine (NumPy)**:
  - Slide whoosh sound.
  - Harmonious bell chime with pitch dynamically scaling up with merged tile values.
  - Triumphant victory fanfare upon reaching 2048.
  - Mute toggle via **`[M]`** key or header button.
- **Full Undo History**:
  - Multi-level undo stack to reverse accidental slides via **`[U]`** or button.
- **Touch & Mouse Swipe Controls**:
  - Play using **Arrow Keys**, **WASD**, or click and drag swipe in any direction!
- **Persistent Best Score**:
  - All-time high score automatically persisted to `best_score.json`.
- **Graceful Exit Dialog**:
  - Protected against accidental exits (`ESC`, `Cmd+Q`, `Alt+F4`, or window cross `X`).

---

## 🕹️ Controls

| Action | Control |
|---|---|
| **Slide Tiles** | **`[Arrow Keys]`** / **`[W] [A] [S] [D]`** / **Mouse Drag Swipe** |
| **Undo Move** | **`[U]`** or Undo button |
| **New Game / Restart** | **`[R]`** or New Game button |
| **Toggle Theme** | **`[T]`** or Theme button |
| **Toggle Sound** | **`[M]`** or Snd button |
| **Quit Game** | **`[Esc]`**, **`Cmd+Q`**, **`Alt+F4`**, or Window Close (`X`) |

---

## 🚀 Running the Game

```bash
cd /Users/ramrupsatpati/Desktop/Python/2048_game
python3 main.py
```

*(Or using the Python virtual environment:)*
```bash
/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py
```

---

## 🧪 Running Automated Tests

```bash
PYTHONPATH=. pytest tests/test_board.py -v
```
