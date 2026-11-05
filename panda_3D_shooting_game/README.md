# CYBER OPS: Modern Panda3D Tactical FPS

A AAA-styled 3D Modern First-Person Shooter game built in Python using **Panda3D**.

---

## 🎮 Key Features & Upgrades

1. **Modern Visuals & PBR-Style Textured World (No Roblox look)**:
   - High-resolution procedural textures: industrial diamond-tread steel floors, high-tech cyber wall panels, corrugated military shipping containers, weathered fortress sandstone, and hazard-striped fuel drums.
   - **Atmospheric Volumetric Fog**: Deep nocturnal cyber navy fog for Sector 7, and sun-bleached golden dust haze for Desert Outpost.
   - High-contrast directional lighting, specular highlights, and rotating searchlights.

2. **Smooth Wall-Sliding Movement & Tactical Balance**:
   - **Axis-independent sliding collision**: You can now smoothly glide along walls and obstacles without ever sticking.
   - **Tactical Deploy Shield (3.5s)**: Complete invulnerability on deployment with a glowing HUD timer so you can safely assess your surroundings and find cover.
   - **Smart Line-of-Sight (LOS) AI**: Enemies can **never** shoot through solid walls or containers. They also have a 1.8s reaction delay and realistic distance-based accuracy falloff.

3. **Modern AAA Tactical Sci-Fi HUD**:
   - **Glassmorphism Panels**: Dark translucent panels with neon cyan border trims and angled cyber chamfers.
   - **Digital Vitals & Shield Gauges**: Dual health and auto-regenerating shield bars with numeric readouts.
   - **Tactical Weapon Card**: Large bold digital ammo readout (`30 / 150`) and firemode badges.
   - **Dynamic Precision Crosshair**: Minimalist crosshair with dynamic spread bloom and center aiming dot.
   - **High-Tech Digital Sniper Scope**: Full-screen optical overlay with mil-dot elevation grid, rangefinder telemetry, and 12x zoom.
   - **360° Rotating Radar Sweep**: Tactical minimap with authentic rotating beam sweep line, cardinal heading (`N`), and hostile blips.

4. **Diverse Weapon Arsenal & Gun Inspect Animation**:
   - **M4A1 Assault Rifle (`[1]`)**: Rapid-fire automatic carbine.
   - **SPAS-12 Shotgun (`[2]`)**: 8-pellet dispersion pump-action CQB weapon.
   - **AWM Sniper Rifle (`[3]`)**: Heavy precision bolt-action rifle with high-power zoom scope.
   - **USP Tactical Pistol (`[4]`)**: Fast semi-auto sidearm with tritium sights.
   - **Gun Inspect Animation (`[F]`)**: Tilts and rolls weapon to examine the chamber with mechanical audio.

5. **Crash-Proof Native Audio**:
   - Native audio driver that eliminates macOS OpenAL segmentation faults.

---

## 🕹️ Controls Quick Reference

| Action | Control |
|---|---|
| **Movement** | `W`, `A`, `S`, `D` (Smooth wall sliding) |
| **Aim / Look** | `Mouse` (Click window to lock) |
| **Shoot** | `Left Mouse Button` |
| **Aim Down Sights (ADS) / Sniper Scope** | `Right Mouse Button` |
| **Gun Inspect** | `F` |
| **Reload** | `R` |
| **Switch Weapons** | `1`, `2`, `3`, `4` or `Mouse Scroll Wheel` |
| **Sprint** | `Left Shift` |
| **Crouch** | `C` or `Left Ctrl` |
| **Jump** | `Space` |
| **Minimap Expand / Compact** | `M` |
| **Pause / Resume** | `Esc` or `P` |

---

## 🚀 How to Run

```bash
cd panda_3D_shooting_game
./venv/bin/python3 main.py
```
