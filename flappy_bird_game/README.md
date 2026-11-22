# 🐦 KFlapper // The OG Classic Flappy Bird (HD Edition)

An authentic, arcade-grade remake of the classic **Flappy Bird** built for **widescreen desktop displays (1280 × 720 HD)** in Python using **Pygame**. Engineered from the ground up with clean **Object-Oriented Programming (OOP)**, procedural vector-grade pixel art, 5-layer parallax scrolling, procedural 8-bit sound effects, character skins, interactive menu GUI, and dynamic progressive biomes.

---

## 🚀 Quick Start

### Run with the Protected Launcher
```bash
cd /Users/ramrupsatpati/Desktop/Python/flappy_bird_game
./run.sh
```

Or run directly with the virtual environment Python:
```bash
../venv/bin/python3 main.py
```

> **Terminal Protection**: [`run.sh`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/run.sh) traps interrupt signals (`Ctrl+C`, `Ctrl+X`, `Ctrl+D`, `Ctrl+Z`), locks terminal line keys, and preserves terminal sanity (`stty sane`) upon exit.

---

## 🎮 Controls & Shortcuts

| Action | Control | Description |
| :--- | :--- | :--- |
| **Flap** | `SPACE` / `▲` / `W` / `Left Click` / `Touch Tap` | Flap wings upwards. Tap in rhythm to navigate pipe gaps. |
| **Clickable GUI Menu** | `Mouse Click` / `Trackpad Tap` | Direct point-and-click difficulty cards, skin arrows, and play button! |
| **Pause / Resume** | `P` or `ESC` | Pauses the flight simulation and dims the screen. |
| **Restart Game** | `R` or `ENTER` | Instantly resets and starts a fresh match. |
| **Cycle Skin** | `C` or Menu Arrows | Cycles through all 5 character skins with live preview. |
| **Switch Difficulty** | `D` or Menu Cards | Toggles between **Chill**, **Classic**, and **Hardcore**. |
| **Switch Biomes** | `T` or Menu Button | Cycles between **Dynamic (Progressive)** or locked biomes. |
| **Toggle Audio** | `M` | Mute / Unmute procedural 8-bit sound effects. |
| **Toggle Fullscreen** | `F11` or `F` | Toggles borderless fullscreen arcade mode. |
| **Quit** | `Q` | Exits the game cleanly. |

---

## 🌟 Progressive Biome Evolution (Dynamic Map Shifting)

As you survive and clear pipes, the environment dynamically evolves into new visual sectors:

| Sector | Threshold | Environment & Visual Theme |
| :--- | :--- | :--- |
| **Sector 1: Earth Meadow** | `0 – 29 bars` | Classic sunny azure sky, fluffy white clouds, green hills, emerald green pipes, and lush grass. |
| **Sector 2: Martian Wasteland** | `30 – 59 bars` | Alien crimson & copper rust sky, alien red dunes, copper metallic pipes, and drifting red dust motes. |
| **Sector 3: Cyber Neon City** | `60 – 89 bars` | Synthwave purple/magenta sky, glowing digital skyscrapers, electric cyan/turquoise glowing laser pipes, and neon motes. |
| **Sector 4: Cosmic Midnight** | `90+ bars` | Deep starry space void, shimmering aurora borealis, midnight blue silhouette hills, silver starlight pipes, and twinkling stars. |

> **Milestone Alerts**: Crossing bar 30, 60, and 90 triggers an animated arcade banner announcement (`✦ SECTOR SHIFT // MARTIAN RED DUST ✦`), a triumphant milestone fanfare, and celebratory particle bursts!

---

## 🕹️ Interactive Menu GUI

Rather than passive text or hidden keys, the title screen features full point-and-click GUI controls:
1. **Difficulty Cards**: 3 dedicated clickable cards (`CHILL`, `CLASSIC`, `HARDCORE`) with hover glows, active selection outlines, and detailed gap/speed metrics.
2. **Skin Switcher**: Live animated flapping preview with clickable `< PREV` and `NEXT >` arrow controls.
3. **Primary Play Button**: Large, pulsing `[ PLAY GAME (SPACE / TAP) ]` button.
4. **Quick Toolbar**: Direct click buttons for Biome Mode, SFX toggle, and High Score display.

---

## 🏛️ Object-Oriented Architecture

```
                       +-----------------------+
                       |     KFlapperGame      |
                       +-----------+-----------+
                                   │
      ┌──────────────┬─────────────┼─────────────┬──────────────┐
      ▼              ▼             ▼             ▼              ▼
+-----------+  +-----------+ +-----------+ +-----------+  +------------+
|   Bird    |  |PipeManager| |Background | |SoundEngine|  |    HUD     |
+-----------+  +-----+-----+ +-----------+ +-----------+  +------------+
                     │                                          │
                     ▼                                          ▼
               +-----------+                              +------------+
               | PipePair  |                              |    Menu    |
               +-----------+                              +-----+------+
                                                                │
                                                                ▼
                                                          +------------+
                                                          |   Medals   |
                                                          +------------+
```

### Module Breakdown:
- **[`src/config.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/config.py)**: Central configuration, physics coefficients, difficulties, skin definitions, and 4-tier progressive biomes.
- **[`src/audio.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/audio.py)**: Pure procedural wave synthesizer and audio manager with asynchronous playback.
- **[`src/entities/bird.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/entities/bird.py)**: Physics simulation, rotation interpolation, wing animation cycles, and procedural skin rendering.
- **[`src/entities/pipe.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/entities/pipe.py)**: Top and bottom pipe generation, gap tracking, scoring triggers, and collision detection.
- **[`src/entities/background.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/entities/background.py)**: 5-layer parallax scenery and endless scrolling striped ground with biome styling.
- **[`src/entities/particles.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/entities/particles.py)**: Feather drift, score sparkles, impact puffs, ambient dust/sparks/stars, and screen shake effects.
- **[`src/ui/hud.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/ui/hud.py)**: In-game score counter, sector indicators, and milestone biome transition banners.
- **[`src/ui/menu.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/ui/menu.py)**: Clickable difficulty cards, skin switcher, primary play button, and animated scoreboard card.
- **[`src/ui/medals.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/ui/medals.py)**: Procedural vector drawing of Bronze, Silver, Gold, and Platinum medals.
- **[`src/game.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/game.py)**: Top-level state coordinator, event dispatcher, persistent records, and main game loop.
