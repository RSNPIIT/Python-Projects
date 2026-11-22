# Kapman - The Classic Retro Maze Chase

A recreation of **Kapman** (the open-source arcade maze classic developed as part of the KDE Games suite) built with **Pygame** and **NumPy**.

---

## 🏛️ Game Overview & Visual Themes

1. **Egyptian Tomb Theme** *(Iconic Kapman Theme)*:
   - **Maze**: 3D embossed golden sandstone beveled walls with brick joint textures.
   - **Player**: Indiana Jones / explorer-style adventurer in fedora hat and red explorer shirt.
   - **Ghosts / Mummies**: 4 ancient Egyptian mummies with hierarchical sashes and glowing eyes:
     - **Akhenaten (Red)**: Direct aggressive stalker.
     - **Nefertiti (Pink)**: Ambush strategist targeting 4 tiles ahead.
     - **Anubis (Cyan)**: Flanking tactician using vector doubling.
     - **Horus (Orange)**: Shy wanderer chasing only from a distance.
   - **Side Warp Tunnels**: Carved golden sarcophagi with ancient mummy relief carvings.
   - **Energizers**: Radiant golden solar sun orbs.
   - **Bonus Items**: Collectible Egyptian relics (Golden Scarab, Ankh, Eye of Horus, Royal Ruby).

2. **Classic Retro Theme**:
   - Neon blue beveled walls with yellow chomp wedge Kapman and classic ghosts.
   - Press **`[T]`** in-game or select from the Main Menu to toggle themes instantly!

---

## 🕹️ Controls

| Action | Control |
|---|---|
| **Move Explorer / Kapman** | **`[Arrow Keys]`** or **`[W] [A] [S] [D]`** |
| **Start Level / Round** | Any Arrow Key / WASD |
| **Toggle Theme** | **`[T]`** |
| **Pause Game** | **`[P]`** |
| **Quit Game Dialog** | **`[Esc]`**, **`Cmd+Q`**, **`Alt+F4`**, or Close (`X`) |

---

## 🚀 Running the Game

```bash
cd /Users/ramrupsatpati/Desktop/Python/kapman_game
python3 main.py
```
*(Or with virtualenv: `/Users/ramrupsatpati/Desktop/Python/venv/bin/python main.py`)*

### 🧪 Running Automated Tests

```bash
PYTHONPATH=. pytest tests/test_kapman.py -v
```
