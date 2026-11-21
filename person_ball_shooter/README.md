# Bubble Blast - Archer Harpoon Arcade

A modern, high-polish recreation of the arcade classic (**Pang / Bubble Trouble**) built with **Pygame** and **NumPy**. Control an archer equipped with a bow and harpoon rope to pop and split giant bouncing bubbles!

---

## 🎯 Gameplay Mechanics

1. **Archer Harpoon Shooting**:
   - The archer moves along the arena floor and shoots vertical steel harpoon arrows straight up towards the ceiling.
   - The arrow leaves a vertical trailing cable/rope from the floor up to the arrowhead tip. Any bubble touching the tip or cable splits!

2. **Bubble Splitting Physics**:
   - Bubbles bounce realistically with gravitational acceleration, rebounding off walls, floor, and ceiling.
   - Popping a bubble splits it in half with opposing horizontal velocities and an upward hop:
     - **Huge (Crimson)**: Radius 46px -> Splits into 2 **Large** bubbles.
     - **Large (Orange)**: Radius 34px -> Splits into 2 **Medium** bubbles.
     - **Medium (Emerald)**: Radius 23px -> Splits into 2 **Small** bubbles.
     - **Small (Cyan)**: Radius 13px -> Pops completely into droplet particles!

3. **Power-Ups (18% Drop Chance)**:
   - **2X (Double Arrow)**: Allows firing two simultaneous harpoons on screen for 14 seconds.
   - **SHIELD**: Grants an energy barrier absorbing 1 bubble hit safely.
   - **SLOW**: Slows game physics by 50% for 6 seconds.
   - **TNT**: Detonates immediately, splitting all active bubbles on screen.
   - **+1 LIFE**: Restores one heart (up to 5 max).

4. **Game Modes**:
   - **Campaign Levels**: 8 handcrafted stages of increasing challenge and bubble count.
   - **Endless Survival**: Fight escalating waves of bouncing titans for high scores.

---

## 🕹️ Controls

| Action | Control |
|---|---|
| **Move Left / Right** | **`[A]`** / **`[D]`** or **`[Left]`** / **`[Right]`** |
| **Shoot Harpoon Arrow** | **`[Space]`**, **`[W]`**, or **`[Up]`** |
| **Restart Current Stage** | **`[R]`** |
| **Quit Game Dialog** | **`[Esc]`**, **`Cmd+Q`**, **`Alt+F4`**, or Close (`X`) |

---

## 🚀 Running the Game

```bash
cd /Users/ramrupsatpati/Desktop/Python/bubble_blast_game
python3 main.py
```
*(Or run with `/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py`)*
