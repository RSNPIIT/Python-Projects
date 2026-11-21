# Bubble Blast • Classic Chain Reaction Puzzle

A recreation of the classic touch-puzzle game built with **Pygame** and **NumPy**.

---

## 🎯 Gameplay & Chain Reaction Mechanics

1. **Bubble Evolution & Stages**:
   - **🔵 Blue Bubble**: Needs 4 hits to pop (Blue → Yellow → Green → Red → POP).
   - **🟡 Yellow Bubble**: Needs 3 hits to pop (Yellow → Green → Red → POP).
   - **🟢 Green Bubble**: Needs 2 hits to pop (Green → Red → POP).
   - **🔴 Red Bubble (Critical)**: Needs **1 hit/tap**! When it pops, it bursts into **4 plasma darts** shooting in all 4 cardinal directions (North, South, East, West).

2. **The Domino Effect**:
   - Flying darts trigger other bubbles along their path:
     - Hitting a **Red Bubble** causes it to immediately pop and launch 4 more darts!
     - Hitting Green, Yellow, or Blue bubbles advances their stage.
   - A single strategic touch can unleash a cascading chain reaction that wipes out the entire board!

3. **Game Modes**:
   - **Puzzle Mode**: 10+ handcrafted levels with limited touches (1-3 taps) where you must find the exact trigger bubble to clear the board.
   - **Arcade / Endless Mode**: Continuous waves of randomized boards with score tracking and replenishment touches.

4. **Visual & Audio Polish**:
   - 3D glossy liquid bubble spheres with specular reflections and breathing wobble.
   - Expanding shockwave rings and liquid splash droplet particles.
   - Procedural audio synthesized via NumPy: bubble pops, liquid bloops, ascending combo chimes, and victory fanfares.
   - Full Quit Confirmation Dialog on `[Esc]`, `Cmd+Q`, `Alt+F4`, or window cross (`X`).

---

## 🕹️ Controls

| Action | Control |
|---|---|
| **Tap / Pop Bubble** | Left Click on any bubble |
| **Retry Level** | Click `RETRY` button or press **`[R]`** |
| **Return to Menu** | Click `< MENU` button or press **`[Esc]`** |
| **Quit Game Dialog** | Press **`Cmd+Q`** / **`Alt+F4`** or **`[Esc]`** from Main Menu |

---

## 🚀 Running the Game

```bash
cd /Users/ramrupsatpati/Desktop/Python/bubble_blast_game
/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py
```
