# 🎾 Pong OOP in Pure C (Terminal / ncurses)

An arcade-quality, flicker-free, full-featured Pong game built in **Pure C (C99)** demonstrating **true Object-Oriented Programming (OOP)** patterns without a C++ compiler.

---

## 🚀 Quick Start

### Prerequisites
- macOS or Linux
- Clang or GCC (`cc`, `clang`, or `gcc`)
- `ncurses` development libraries (pre-installed on macOS)

### Run with Protected Launcher
```bash
cd /Users/ramrupsatpati/Desktop/Python-Projects/pong_c_oop
./run.sh
```

> **Terminal Protection**: `run.sh` isolates terminal signals (`Ctrl+C`, `Ctrl+Z`, `Ctrl+\`, `Ctrl+D`) to prevent the terminal from corrupting or freezing during gameplay, and automatically restores terminal state (`stty sane`, cursor visibility, alternate screen buffer) upon exit.

### Manual Compilation
```bash
make clean && make
./bin/pong_c_oop
```

---

## 🎮 Controls

### Main Menu
| Key | Action |
| :--- | :--- |
| `▲ / ▼` or `W / S` | Navigate menu rows |
| `◄ / ►` or `A / D` | Adjust Game Mode, AI Difficulty, Score Limit |
| `ENTER` or `SPACE` | Start Selected Match |
| `Q` or `ESC` | Exit Game |

### In-Game (Match)
| Key | Action |
| :--- | :--- |
| `W / S` | Move Left Paddle (Player 1) |
| `▲ / ▼` | Move Right Paddle (Player 2 in 2P Local Mode) |
| `P` or `ESC` | Pause / Open In-Game Options Menu |
| `R` | Quick Reset Match |

### Game Modes
1. **1P vs CPU**: Single-player campaign against an intelligent predictive AI.
2. **2P Local**: Two players on a shared keyboard (`W/S` vs `▲/▼`).
3. **Spectator (Attract Mode)**: Autonomous AI vs AI match.
4. **Solo Practice**: Infinite rally mode against a wall.

### AI Difficulties
- **Casual**: Relaxed reaction time with intentional human-like tracking errors.
- **Pro**: Fast reactions with straight-line trajectory tracking.
- **Master**: Trigonometric reflection prediction calculating top and bottom bank bounces.
- **Unbeatable**: Millimeter-precision interception.

---

## 🏛️ Object-Oriented Architecture in Pure C

Standard C has no `class`, `virtual`, or `inheritance` keywords, yet OOP is a **design discipline**, not a compiler feature. This project implements every core tenet of OOP cleanly in ISO C99:

```
                  +--------------------------------+
                  |         Entity (Base)          |
                  |--------------------------------|
                  | - vtable: const EntityVTable*  |
                  | - pos, vel, size: Vec2         |
                  | - color: ColorPairId           |
                  +--------------------------------+
                                  ▲
                                  │ (Struct Embedding / Inheritance)
                 ┌────────────────┴────────────────┐
                 │                                 │
     +-----------------------+         +-----------------------+
     |     Paddle (Derived)  |         |      Ball (Derived)   |
     |-----------------------|         |-----------------------|
     | [Entity base]         |         | [Entity base]         |
     | - player_id: int      |         | - base_speed: float   |
     | - controller: Contr.* |         | - trail[8]: Vec2      |
     | - score: int          |         | - rally_count: int    |
     +-----------------------+         +-----------------------+
                 │
                 ▼ (Strategy Pattern)
     +-----------------------+
     |      Controller       |
     |-----------------------|
     | - vtable              |
     +-----------------------+
          ▲             ▲
          │             │
   +------------+ +------------+
   | HumanCtrl  | |   AICtrl   |
   +------------+ +------------+
```

---

### 1. Encapsulation & Data Hiding
Each module exposes an opaque or structured interface in its `.h` header file and keeps its private logic, helper algorithms, and static state hidden in its corresponding `.c` implementation file:
- Constructors (`Paddle_Create`, `Ball_Create`, `Renderer_Create`) dynamically allocate heap memory, initialize internal fields, and assign virtual tables.
- Destructors (`Entity_Destroy`, `Controller_Destroy`, `Renderer_Destroy`) guarantee clean deallocation and resource reclamation.

---

### 2. Single Inheritance via C99 Struct Embedding
According to the ISO C99 standard (§6.7.2.1), a pointer to a structure object points to its initial member. By placing the base class as the **exact first member** of a derived class:

```c
/* include/entity.h (Base Class) */
typedef struct Entity {
    const EntityVTable* vtable;
    const char* type_name;
    Vec2 pos;
    Vec2 vel;
    Vec2 size;
    ColorPairId color;
    bool active;
} Entity;

/* include/paddle.h (Derived Class) */
typedef struct Paddle {
    Entity base;            /* <-- EXACT FIRST MEMBER: Enables zero-offset polymorphic casting */
    int player_id;
    float speed;
    int score;
    Controller* controller; /* Injected Control Strategy */
    float hit_flash_timer;
} Paddle;
```

**Memory Guarantee**:
```c
(Entity*)my_paddle == &(my_paddle->base)
```
Any `Paddle*` or `Ball*` can be safely cast to `Entity*` without memory offset adjustments or compiler warnings.

---

### 3. Dynamic Polymorphism via VTables (Virtual Method Tables)
Just like a C++ compiler creates an internal `_vptr`, we define a table of function pointers representing virtual methods:

```c
/* include/entity.h */
typedef struct EntityVTable {
    void (*update)(struct Entity* self, float dt, struct GameApp* app);
    void (*render)(const struct Entity* self, struct Renderer* renderer);
    void (*on_collision)(struct Entity* self, struct Entity* other, struct GameApp* app);
    void (*destroy)(struct Entity* self);
} EntityVTable;
```

Concrete implementations (`src/paddle.c` and `src/ball.c`) define their own static function tables:
```c
/* src/paddle.c */
static const EntityVTable PADDLE_VTABLE = {
    .update       = Paddle_Update,
    .render       = Paddle_Render,
    .on_collision = Paddle_OnCollision,
    .destroy      = Paddle_Destroy
};
```

#### Polymorphic Dispatch in Action:
The game engine maintains a single heterogeneous array: `Entity* entities[MAX_ENTITIES];`.
During each frame, the engine loops over all entities and dispatches to their specific implementations without knowing whether each object is a Paddle or a Ball:

```c
/* src/scene_match.c */
for (int i = 0; i < app->entity_count; i++) {
    Entity* e = app->entities[i];
    if (e && e->active) {
        Entity_Update(e, dt, app);      /* e->vtable->update(...) */
        Entity_Render(e, app->renderer);/* e->vtable->render(...) */
    }
}
```

---

### 4. Strategy Pattern (Input & AI Decoupling)
Paddles do not know whether they are controlled by a keyboard or artificial intelligence. A `Controller` interface is injected into each paddle:
- `HumanController`: Reads key states (`W/S` or `▲/▼`).
- `AIController`: Analyzes ball trajectory, performs bank-bounce trigonometry, adds configurable reaction latency, and computes target coordinates.

Switching game modes (Singleplayer, 2P Local, or Spectator) simply swaps the controller instance assigned to each paddle:
```c
/* src/game.c */
Paddle_SetController(self->player1, HumanController_Create('w', 's', KEY_UP, KEY_DOWN));
Paddle_SetController(self->player2, AIController_Create(self->ai_difficulty));
```

---

### 5. State Pattern (Scene Manager)
The game flow is coordinated through polymorphic scene states implementing `GameScene`:
- `MenuScene`: Interactive animated main menu.
- `MatchScene`: Physics, collisions, scoring, and HUD telemetry.
- `GameOverScene`: Victory laurels, final statistics, and replay options.

---

## 📊 Comparison: Procedural Prototype vs. Pure C OOP

| Metric | Original Prototype (`pong_game.c`) | Refactored OOP (`pong_c_oop`) |
| :--- | :--- | :--- |
| **Architecture** | Monolithic 120-line single function | Modular 11-header OOP hierarchy |
| **State Management** | Raw mutable local variables | Encapsulated structs with constructors/destructors |
| **Physics** | Discrete integer grid steps | Sub-character floating-point vector math (`Vec2`) |
| **Collisions** | Hardcoded paddle checks | Generic AABB collision with polymorphic dispatch |
| **AI** | Rigid integer comparison | Predictive reflection trajectory with difficulty presets |
| **Rendering** | Direct in-loop curses calls (flicker-prone) | Double-buffered renderer, color pairs, motion trails |
| **Input Handling** | Blocking / fragile `wgetch` | Non-blocking keymap buffer with terminal signal trapping |

---

## 📁 Project Directory Structure

```
pong_c_oop/
├── Makefile                # Automated build system with dependencies
├── README.md               # Architecture documentation & guide
├── run.sh                  # Signal-trapped execution launcher
├── include/                # Public OOP headers & interfaces
│   ├── ball.h              # Ball class definition
│   ├── common.h            # 2D math (Vec2, Rect), enums & helpers
│   ├── controller.h        # Strategy pattern controller interface
│   ├── court.h             # Responsive court geometry manager
│   ├── entity.h            # Base Entity class & VTable
│   ├── game.h              # Top-level application coordinator
│   ├── paddle.h            # Paddle class definition
│   ├── renderer.h          # Ncurses TUI double-buffered renderer
│   ├── scene.h             # GameScene interface (State pattern)
│   ├── scene_gameover.h    # Match victory scene
│   ├── scene_match.h       # Active gameplay match scene
│   └── scene_menu.h        # Interactive main menu scene
└── src/                    # Concrete implementations
    ├── ball.c              # Ball physics, reflection angles & motion trail
    ├── controller.c        # Human & predictive AI controllers
    ├── court.c             # Court drawing & responsive resize
    ├── entity.c            # Base entity lifecycle
    ├── game.c              # 60 FPS clock, entity array & match lifecycle
    ├── main.c              # Application entry point
    ├── paddle.c            # Paddle movement, input & hit flash
    ├── renderer.c          # Double-buffering, scoreboard & HUD
    ├── scene_gameover.c    # Post-match summary dialog
    ├── scene_match.c       # Match game loop & collision dispatch
    └── scene_menu.c        # Title menu & settings toggles
```
