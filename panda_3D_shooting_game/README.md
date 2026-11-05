# CYBER OPS: Modern Panda3D Tactical FPS

A complete, feature-rich 3D Modern First-Person Shooter game built in Python using the **Panda3D** game engine.

---

## 🎮 Key Features

1. **Arsenal of Distinct Weapons**:
   - **M4A1 Assault Rifle**: Full-auto carbine with balanced recoil, holo-sight glow, 30-round mag.
   - **SPAS-12 Shotgun**: Pump-action devastating CQB weapon with 8-pellet randomized dispersion cone.
   - **AWM Heavy Sniper Rifle**: Extreme distance bolt-action precision with high-power zoom, mil-dot scope overlay, vignette effect, and breathing sway.
   - **USP Tactical Pistol**: Crisp semi-auto sidearm with tritium glow sights, fast draw speed.
2. **Gun Inspect Animation (`F` Key)**:
   - Dynamic procedural inspect motion: tilts the weapon 45° sideways, rolls up to examine chamber markings, and returns smoothly to hip position with authentic mechanical audio.
3. **Multiple Dynamic Maps**:
   - **Map 1: Sector 7 - Cyber Facility**: High-tech industrial complex with shipping containers, elevated catwalks, working elevator platforms, and dynamic rotating security searchlights.
   - **Map 2: Ruins of Oasis - Desert Outpost**: Sun-bleached sandstone fort ruins with courtyard pillars, ramps, and a moving hover platform crossing the sand trench.
4. **Dynamic Map Elements**:
   - **Explosive Barrels**: Shootable red hazard barrels that detonate with AoE shockwaves, dealing heavy damage to nearby enemies and player.
   - **Moving Platforms & Elevators**: Dynamic physics platforms that carry the player vertically or horizontally.
   - **Respawning Pickups**: Floating, spinning Medkits (+50 HP) and Ammo Crates.
5. **Real-time Tactical Minimap & Radar (`M` Key)**:
   - Top-right corner radar HUD showing real-time player heading arrow, red enemy blips, orange barrel markers, and cyan pickup/platform icons.
   - Press **`M`** to toggle between compact corner radar and full-screen tactical radar.
6. **Smart AI Enemies**:
   - **Grunt Bot**: Assault rifle soldier bot that maneuvers, takes cover, and fires burst rounds.
   - **Striker Bot**: Fast, aggressive shotgun rusher that closes in quickly.
   - **Sniper Bot**: Long-range threat that tracks the player with a **visible red aiming laser line** before firing high-damage sniper shots.
7. **Tactical Audio & Voice Effects**:
   - Procedurally synthesized gunshots, reloads, inspect clicks, footstep cadences, bullet impacts, explosive booms, and radio voice callouts ("Kill confirmed", "Incoming wave alert", etc.).
8. **Modern Tactical HUD**:
   - Dynamic expanding crosshairs based on movement and recoil.
   - Hitmarkers with crisp audio ticks (white for hits, red for kills).
   - Health and auto-regenerating shield bars.
   - Damage vignette indicators.

---

## 🕹️ Controls

| Action | Key / Control |
|---|---|
| **Move** | `W`, `A`, `S`, `D` |
| **Aim / Look** | `Mouse` (Smooth pitch & yaw) |
| **Fire Weapon** | `Left Mouse Button` |
| **Aim Down Sights (ADS) / Sniper Scope** | `Right Mouse Button` |
| **Gun Inspect Animation** | `F` |
| **Reload Weapon** | `R` |
| **Switch Weapons** | `1`, `2`, `3`, `4` or `Mouse Scroll Wheel` |
| **Sprint** | `Left Shift` |
| **Crouch** | `C` or `Left Ctrl` |
| **Jump** | `Space` |
| **Toggle Tactical Minimap** | `M` |
| **Pause Menu / Unlock Cursor** | `Esc` or `P` |

---

## 🚀 How to Run

### Option 1: Using the created virtual environment (Recommended)
```bash
cd panda_3D_shooting_game
./venv/bin/python3 main.py
```

### Option 2: System Python (if Panda3D is installed globally)
```bash
cd panda_3D_shooting_game
pip install -r requirements.txt
python3 main.py
```

---

## 📁 Project Architecture

- **`main.py`**: Game state machine (Menu, Playing, Paused, Game Over), wave progression, and ShowBase entry point.
- **`player.py`**: First-person controller, WASD physics, mouse look, recoil spring, crouch/sprint, and hitscan raycasting.
- **`weapons.py`**: Weapon base class, Pistol, AR, Shotgun, Sniper, procedural 3D viewmodels, recoil kick, and inspect animations.
- **`enemy.py`**: Enemy AI classes (Grunt, Striker, Sniper with red warning laser), pathing, and wave spawner.
- **`map_manager.py`**: Cyber Facility & Desert Outpost generators, explosive barrels, moving elevators, and pickups.
- **`minimap.py`**: 2D tactical radar and expanded tactical map HUD.
- **`hud.py`**: Dynamic crosshair, hitmarker, health/shield bars, sniper scope overlay, and damage indicator.
- **`particles.py`**: Bullet tracers, sparks, muzzle flashes, and fireball explosion debris.
- **`mesh_builder.py`**: Procedural 3D geometry generator (cubes, cylinders, wedges, ramps).
- **`audio_generator.py`**: Synthesizes all tactical sound effects and voice callouts directly into `.wav` format.
