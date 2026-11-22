# 🐦 KFlapper // The OG Classic Flappy Bird (HD Edition)

An authentic, arcade-grade remake of the classic **Flappy Bird** built for **widescreen desktop displays (1280 × 720 HD)** in Python using **Pygame**. Engineered from the ground up with clean **Object-Oriented Programming (OOP)**, procedural vector-grade pixel art, 5-layer parallax scrolling, procedural 8-bit sound effects, character skins, and tiered medals.

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

> **Terminal Protection**: [`run.sh`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/run.sh) traps interrupt signals (`Ctrl+C`, `Ctrl+X`, `Ctrl+D`, `Ctrl+Z`) and preserves terminal sanity (`stty sane`) upon exit.

---

## 🎮 Controls & Shortcuts

| Action | Key / Input | Description |
| :--- | :--- | :--- |
| **Flap** | `SPACE` / `▲` / `W` / `Left Click` | Flap wings upwards. Tap in rhythm to maintain altitude! |
| **Pause / Resume** | `P` or `ESC` | Pauses the flight simulation and dims the screen. |
| **Restart Game** | `R` or `ENTER` | Instantly resets and starts a fresh match. |
| **Cycle Skin** | `C` | Cycles through 5 bird skins in real-time. |
| **Switch Difficulty** | `D` | Toggles between **Classic**, **Chill**, and **Hardcore**. |
| **Switch Time of Day** | `T` | Cycles sky themes: **Day**, **Sunset**, **Night**, or **Dynamic**. |
| **Toggle Audio** | `M` | Mute / Unmute procedural 8-bit sound effects. |
| **Toggle Fullscreen** | `F11` or `F` | Toggles borderless fullscreen arcade mode. |

---

## 🌟 Key Features

1. **Widescreen 16:9 HD Display (1280 × 720)**:
   - Designed specifically for larger desktop monitors.
   - Smooth 60 FPS flight dynamics with crisp rendering and borderless fullscreen toggle (`F11`).

2. **Authentic OG Flight Dynamics**:
   - Precise gravity acceleration (`0.50 px/f²`), flap impulse (`-9.2 px/f`), and velocity clamping.
   - Realistic attitude pitch dynamics: snaps upwards to `+26°` upon flapping and smoothly tilts down to `-90°` nosedive during descents.
   - Triple-frame wing flapping animation with smooth sinusoidal idle hover in the main menu.

3. **5 Selectable Character Skins (`C` key)**:
   - 🐤 **KFlapper (Classic)**: Iconic golden yellow body, fiery orange beak, and white belly.
   - 🦅 **Cyber Falcon**: Electric cyan plumage, neon magenta wing, and cyber visor eye.
   - 🔥 **Crimson Phoenix**: Ruby body, gold crest plume, and amber belly.
   - 🪶 **Midnight Raven**: Obsidian navy feathers, royal violet wing, and ruby glint eye.
   - 🦜 **Emerald Parakeet**: Lime green plumage, turquoise wing, and warm amber beak.

4. **Multi-Layer Parallax Environment**:
   - **Layer 1 (Atmosphere)**: Smooth vertical sky gradient with Day, Sunset, and Night color palettes.
   - **Layer 2 (Drifting Clouds)**: Soft cumulus clouds drifting at `0.10×` parallax speed.
   - **Layer 3 (City Skyline)**: Distant cityscape silhouette with radio towers at `0.22×` speed.
   - **Layer 4 (Rolling Hills)**: Gentle green hills and roadside bushes at `0.45×` speed.
   - **Layer 5 (Scrolling Ground)**: Iconic retro dirt ground with scrolling diagonal hash stripes in sync with pipes.
   - **Dynamic Time Mode**: Sky seamlessly transitions from Day ➔ Sunset ➔ Night ➔ Dawn every 10 points!

5. **Obstacles & Fair Hitboxes**:
   - Authentic retro green pipe shading with lip collar caps, inner shadows, and specular highlight stripes.
   - Circular-vs-box collision algorithm with a 3-pixel inset margin so close-shave maneuvers feel fair and responsive.

6. **Procedural 8-bit Sound Synthesizer**:
   - Zero external audio files required! Synthesizes 6 distinct retro WAV sounds directly in memory:
     - `flap`: Light wing whoosh
     - `point`: Crystal two-tone arcade chime (B5 + E6)
     - `hit`: Crunchy pipe crash impact
     - `die`: Falling pitch drop slide
     - `swoosh`: Smooth UI transition whoosh
     - `medal`: Triumphant 4-note victory fanfare

7. **Tiered Medals & High Score Persistence**:
   - Automatic record saving in `~/.kflapper_save.json` per difficulty tier.
   - Post-game scoreboard card with animated counting score, high-score comparison, and unlocked medals:
     - 🥉 **Bronze Medal** (10 – 19 points)
     - 🥈 **Silver Medal** (20 – 29 points)
     - 🥇 **Gold Medal** (30 – 39 points)
     - 💎 **Platinum Diamond Medal** (40+ points)
     - Animated glowing `NEW!` badge when setting a personal best.

8. **Visual Juice & Effects**:
   - Drifting feather particles emitted when flapping and upon collision.
   - Diamond coin score sparkles when clearing pipes.
   - Screen shake and flash on crash.
   - Big arcade score digits with score pop bounce animation.

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
- **[`src/config.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/config.py)**: Central configuration, physics coefficients, difficulties, skin definitions, and color themes.
- **[`src/audio.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/audio.py)**: Pure procedural wave synthesizer and audio manager with asynchronous playback.
- **[`src/entities/bird.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/entities/bird.py)**: Physics simulation, rotation interpolation, wing animation cycles, and procedural skin rendering.
- **[`src/entities/pipe.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/entities/pipe.py)**: Top and bottom pipe generation, gap tracking, scoring triggers, and collision detection.
- **[`src/entities/background.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/entities/background.py)**: 5-layer parallax scenery and endless scrolling striped ground.
- **[`src/entities/particles.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/entities/particles.py)**: Feather drift, score sparkles, impact puffs, and screen shake effects.
- **[`src/ui/hud.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/ui/hud.py)**: In-game big score counter with bounce animation and status pills.
- **[`src/ui/menu.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/ui/menu.py)**: Title screen with 3D logo, floating bird, and animated post-match scoreboard card.
- **[`src/ui/medals.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/ui/medals.py)**: Procedural vector drawing of Bronze, Silver, Gold, and Platinum medals.
- **[`src/game.py`](file:///Users/ramrupsatpati/Desktop/Python/flappy_bird_game/src/game.py)**: Top-level state coordinator, event dispatcher, persistent records, and main game loop.
