# Bubble Blast - Hexagonal Bubble Shooter

A recreation of the mobile bubble shooter arcade game (**Puzzle Bobble / Bust-a-Move / Bubble Witch**) built with **Pygame** and **NumPy**.

---

## 🎯 Gameplay Mechanics

1. **Hexagonal Honeycomb Matrix**:
   - Bubbles hang suspended from the ceiling in an offset hexagonal honeycomb pattern (even rows: 11 bubbles, odd rows: 10 bubbles).
   - Rich 3D glossy marble rendering with specular reflections and ambient rim lighting.

2. **Laser Aim Trajectory & Wall Bouncing**:
   - Dynamic real-time raycaster predicts the bubble's flight path.
   - Refracts off the left and right arena walls and projects an impact halo where the bubble will strike the ceiling or grid.

3. **Match-3+ Burst**:
   - Connecting a launched bubble with 2 or more bubbles of the identical color forms a match ($\ge 3$).
   - The matched cluster bursts into liquid droplet particles and awards combo points.

4. **Avalanche Cascade (Floating Bubble Drops)**:
   - Any bubbles that lose physical connection to the ceiling become orphans.
   - Detached bubbles immediately fall with gravity, awarding massive avalanche bonus points!

5. **Launcher & Ammo Pedestal**:
   - Displays current remaining ammo inside the circular pedestal.
   - Next upcoming bubble preview rests on the bottom right.
   - **Swap Feature**: Right-click, press `[C]`, or click the preview bubble to swap the active bubble with the upcoming one.

---

## 🕹️ Controls

| Action | Control |
|---|---|
| **Aim** | Move Mouse |
| **Shoot Bubble** | **Left Click** |
| **Swap Bubble** | **Right Click**, **`[C]`**, or Click Preview Bubble |
| **Restart Stage** | **`[R]`** |
| **Quit Game Dialog** | **`[Esc]`**, **`Cmd+Q`**, **`Alt+F4`**, or Close (`X`) |

---

## 🚀 Running the Game

```bash
cd /Users/ramrupsatpati/Desktop/Python/bubble_blast_shooter
python3 main.py
```
*(Or with venv: `/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py`)*
