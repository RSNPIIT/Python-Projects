# Block Blast • Rocket Cannon Arcade Shooter

A high-octane physics arcade game inspired by classic mobile block-blasting physics shooters.

---

## 🎯 Gameplay & Core Mechanics

- **Aim & Shoot**: Point your cannon with the mouse and hold the **Left Mouse Button** or **Spacebar** to unleash continuous streams of rockets.
- **Destroy Blocks**: Each block displays its remaining Hit Points. Numbered blocks flash when damaged and shatter with explosive particle bursts when HP reaches 0!
- **⚡ Vicinity Chain Blast (High-Value Knockdown)**:
  - When you destroy a block with a **higher number**, any neighboring blocks in its immediate vicinity (horizontal, vertical, diagonal) with a **lesser number** are **automatically blasted**!
  - This can trigger a cascading domino chain reaction (`2x COMBO!`, `3x CHAIN!`), wiping out entire clusters and rewarding massive bonus multipliers.
- **Danger Deadline**: Blocks steadily descend wave by wave. If any block touches the glowing **Danger Line** barrier at the bottom, the game is **OVER**!
- **Chain Reactions**: Special **Bomb Blocks (TNT)** trigger 3×3 shockwave explosions when destroyed, detonating neighboring blocks.
- **Power-Ups**: Destroyed blocks drop glowing power-up capsules:
  - **3X Spread Shot**: Triple rocket barrage fan.
  - **BOLT (Laser Drill)**: High-velocity energy rockets drilling through multiple blocks.
  - **SPD (Rapid Fire)**: Doubles rocket fire rate.
  - **ICE (Pushback)**: Instantly pushes descending blocks back up to buy breathing room!

---

## 🕹️ Controls

| Control | Action |
|---|---|
| **Mouse Aim** | Rotates the cannon & projects the laser trajectory sight |
| **Left Click / Hold** | Fire rockets continuously |
| **`[Space]`** | Alternative fire key |
| **`[R]`** | Restart / New Game |
| **`Cmd+Q` / `Alt+F4`** | Quit application |

---

## 🚀 Running the Game

```bash
cd /Users/ramrupsatpati/Desktop/Python/blockblast_game_directory
/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py
```
