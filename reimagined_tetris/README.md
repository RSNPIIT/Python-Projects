# ✦ REIMAGINED TETRIS // Cyber Matrix

A modern, competition-grade **Tetris** reimagined with pure Object-Oriented architecture, official **Super Rotation System (SRS)** wall kicks, **7-Bag Randomizer**, dynamic **ModernGL post-processing shaders** (bloom glow, chromatic aberration shockwaves, CRT scanlines, vignette), procedural stereo audio synthesis, and sleek glassmorphic UI.

---

## ⚡ Quick Launch

Inside the project directory:

```bash
cd /Users/ramrupsatpati/Desktop/Python/reimagined_tetris
./run.sh
```

> **Terminal Protection**: When launched with `./run.sh`, terminal signals (`Ctrl+C`, `Ctrl+X`, `Ctrl+D`) are locked and ignored, preventing accidental terminal termination. Exit cleanly through the in-game menus or `ESC`.

---

## 🎮 Game Controls

| Action | Primary Keys | Alternate Keys |
| :--- | :--- | :--- |
| **Move Left / Right** | `←` `→` | `A` `D` (with DAS & ARR auto-repeat) |
| **Rotate Clockwise** | `↑` | `W` / `X` |
| **Rotate Counter-Clockwise** | `Z` | `Q` |
| **Soft Drop** | `↓` | `S` (Smooth speedup + points) |
| **Hard Drop** | `SPACE` | Instant drop + floor impact shockwave |
| **Hold Piece** | `C` | `Left Shift` / `Right Shift` |
| **Pause / Resume** | `ESC` | `P` |
| **Quick Toggle Scanlines**| `F2` | Toggle CRT scanlines on/off |

---

## 🌟 Key Features & Improvements Over Prototype

### 1. 🏗️ Clean Object-Oriented Architecture (OOPS)
- **Eliminated 50+ procedural global variables** (`block_matrix`, `color_matrix`, `row_indexer`, `drop_timer`, `touching_surface`, etc.).
- Modular separation into dedicated domain systems:
  - `src/engine/tetromino.py`: Immutable shapes, rotation states, SRS offset tables.
  - `src/engine/board.py`: Matrix collision detection, line clear checking, ghost calculation, 3-corner T-spin detection.
  - `src/engine/randomizer.py`: Official 7-Bag Randomizer + 5-piece Next preview queue.
  - `src/engine/score_manager.py`: Official guideline scoring (Combos, Back-to-Back, T-Spins, Perfect Clears).
  - `src/engine/game_state.py`: Gameplay coordinator, DAS / ARR timers, lock delay resets.
  - `src/graphics/shader_manager.py`: ModernGL OpenGL Core 3.3 post-processing pipeline with software fallback.
  - `src/graphics/renderer.py`: Glassmorphic faceted blocks, ghost piece, matrix container, ambient space drift.
  - `src/graphics/particles.py`: Hard drop sparks, laser clear beams, floating score text popups.
  - `src/audio/synth.py` & `sound_manager.py`: 100% procedural sound synthesis using NumPy without external assets.
  - `src/states/`: Menu state, mode selector, settings modal, pause modal, game over summary.

### 2. 🌀 Official SRS (Super Rotation System) & T-Spins
- Standard Guideline wall kicks for all 7 tetrominoes (`I`, `O`, `T`, `S`, `Z`, `J`, `L`).
- Full 5-stage kick testing per rotation (`0->R`, `R->2`, `2->L`, `L->0` and inverses).
- **Official 3-Corner T-Spin Detection**: Recognizes T-Spin Minis, T-Spin Singles, Doubles, and Triples with proper bonus points.

### 3. 🔮 Post-Processing Shaders & Cyberpunk Visuals
- **Dynamic Bloom Glow**: Illuminates neon active tetrominoes and clearing rows.
- **Chromatic Aberration & Shockwave**: Triggers dynamic screen impact distortion on hard drops, line clears, and Tetrises.
- **CRT Scanlines & Cinematic Vignette**: Retro-futuristic scanlines (toggleable with `F2` or in Settings).
- **Ghost Projection**: Shows exactly where the active piece will land.
- **Particle System**: Explosive spark bursts, laser line dissolves, and floating combo banners.

### 4. 🗂️ 4 Game Modes
1. **Marathon**: Classic 15-level climb to 150 lines with exponentially ramping gravity.
2. **Sprint (40 Lines)**: Speedrun to clear 40 lines as fast as possible with millisecond timer.
3. **Ultra (3 Minutes)**: Score rush under a strict 180-second clock.
4. **Wide Matrix (16 Columns)**: Nostalgic expanded 16-column matrix honoring the user's original prototype!

### 5. 🔊 Procedural Synthwave SFX
- Crisp high-frequency movement clicks, frequency-modulated rotation sweeps, sub-bass hard drop kicks, harmonic hold swap chimes, melodic triad line clear chords, ascending combo scale, and arpeggiated level-up fanfares.

---

## 📁 Project Directory Structure

```
reimagined_tetris/
├── run.sh                     # Protected launcher script
├── main.py                    # Entry point & game loop
├── config.py                  # Global settings, colors, guideline tables
├── requirements.txt           # Dependencies (pygame-ce, moderngl, numpy)
├── README.md                  # Complete documentation
├── data/                      # Persistent high scores (highscores.json)
└── src/
    ├── audio/
    │   ├── synth.py           # Waveform generator (NumPy stereo synthesis)
    │   └── sound_manager.py   # Sound caching & volume mixer
    ├── engine/
    │   ├── tetromino.py       # SRS rotation tables & tetromino models
    │   ├── board.py           # Collision, ghost calculation, T-spin checks
    │   ├── randomizer.py      # 7-Bag randomizer & preview queue
    │   ├── score_manager.py   # Guideline scoring, combos, B2B, stats
    │   └── game_state.py      # DAS/ARR input handling, lock delay, gravity
    ├── graphics/
    │   ├── shader_manager.py  # ModernGL bloom, shockwave & scanlines
    │   ├── renderer.py        # Glass faceted blocks, grid & layout renderer
    │   ├── particles.py       # Hard drop sparks & floating score text
    │   └── ui_components.py   # Glassmorphic panels, gauges, buttons
    └── states/
        ├── menu_state.py      # Cyberpunk main menu & settings modal
        └── modals.py          # Pause menu & Game Over summary dialogs
```
