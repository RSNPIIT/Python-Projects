"""Mission definitions, hand-built floorplans, and level themes."""

from __future__ import annotations

from dataclasses import dataclass, field

from .config import (
    BLACK,
    BLUE,
    CYAN,
    GOLD,
    GREEN,
    INK,
    MAGENTA,
    ORANGE,
    RED,
    TEAL,
    VIOLET,
    WHITE,
)

MAP_W = 22
MAP_H = 22
WALL_CHARS = {"#": 1, "M": 2, "N": 3, "C": 4}
FLOOR_CHARS = set(" @tdbB>+^*i!")
WALKABLE = set(" @tdbB>+^*i!")


@dataclass(frozen=True)
class Theme:
    key: str
    accent: tuple[int, int, int, int]
    accent_2: tuple[int, int, int, int]
    sky_high: tuple[int, int, int, int]
    sky_low: tuple[int, int, int, int]
    floor_far: tuple[int, int, int, int]
    floor_near: tuple[int, int, int, int]
    fog: tuple[int, int, int, int]
    wall_base: tuple[int, int, int, int]
    wall_dark: tuple[int, int, int, int]
    wall_light: tuple[int, int, int, int]
    wall_metal: tuple[int, int, int, int]
    hazard: tuple[int, int, int, int]
    outdoor: bool = False
    boss_music_pitch: float = 1.0
    ambient_particles: str = "dust"


@dataclass(frozen=True)
class EnemySpec:
    kind: str
    x: int
    y: int


@dataclass(frozen=True)
class PickupSpec:
    kind: str
    x: int
    y: int


@dataclass
class LevelDef:
    index: int
    code: str
    name: str
    subtitle: str
    briefing: str
    directive: str
    hint: str
    theme: Theme
    rows: list[str]
    start: tuple[float, float]
    exit: tuple[float, float]
    enemies: list[EnemySpec]
    pickups: list[PickupSpec]
    intel: list[tuple[int, int]]
    boss: tuple[float, float] | None = None
    boss_name: str = ""
    boss_hp: float = 0.0
    threat_level: str = "ELEVATED"
    recommended: str = "PULSE BLASTER"
    music_pitch: float = 1.0


# ---------------------------------------------------------------------------
# Floorplan assembly helpers
# ---------------------------------------------------------------------------
def _blank_map() -> list[list[str]]:
    return [["#"] * MAP_W for _ in range(MAP_H)]


def _carve(grid: list[list[str]], x1: int, y1: int, x2: int, y2: int, char: str = " ") -> None:
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 < x < MAP_W - 1 and 0 < y < MAP_H - 1:
                grid[y][x] = char


def _put(grid: list[list[str]], x: int, y: int, char: str) -> None:
    if 0 <= x < MAP_W and 0 <= y < MAP_H:
        grid[y][x] = char


def _decorate_walls(grid: list[list[str]], seed: int) -> None:
    """Mix themed wall materials into face-adjacent structural walls."""
    for y in range(MAP_H):
        for x in range(MAP_W):
            if grid[y][x] != "#":
                continue
            adjacent = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < MAP_W and 0 <= ny < MAP_H and grid[ny][nx] in WALKABLE:
                    adjacent = True
                    break
            if not adjacent:
                continue
            roll = (x * 928371 + y * 689287 + seed * 123457) % 100
            if roll < 12:
                grid[y][x] = "M"
            elif roll < 18:
                grid[y][x] = "N"
            elif roll < 20:
                grid[y][x] = "C"


def _finish(
    grid: list[list[str]],
    start: tuple[int, int],
    exit_cell: tuple[int, int],
    enemies: list[tuple[str, int, int]],
    pickups: list[tuple[str, int, int]],
    intel: list[tuple[int, int]],
    boss: tuple[int, int] | None,
    hazards: list[tuple[int, int]] | None = None,
) -> tuple[list[str], list[EnemySpec], list[PickupSpec]]:
    for x, y in hazards or []:
        if grid[y][x] == " ":
            grid[y][x] = "!"
    _put(grid, *start, "@")
    _put(grid, *exit_cell, ">")
    for x, y in intel:
        _put(grid, x, y, "i")
    for kind, x, y in pickups:
        _put(grid, x, y, {"health": "+", "ammo": "^", "nova": "*"}[kind])
    for kind, x, y in enemies:
        _put(grid, x, y, {"trooper": "t", "drone": "d", "brute": "b"}[kind])
    if boss:
        _put(grid, *boss, "B")
    # Safety: every marker cell must remain walkable.
    for y in range(MAP_H):
        for x in range(MAP_W):
            if grid[y][x] in "tdbB+^*i>@":
                grid[y][x] = " " if grid[y][x] != "!" else "!"
    # Re-apply wall material treatment after carving.
    return ["".join(row) for row in grid], [EnemySpec(k, x, y) for k, x, y in enemies], [
        PickupSpec(k, x, y) for k, x, y in pickups
    ]


def _build_level_one() -> tuple[list[str], list[EnemySpec], list[PickupSpec]]:
    g = _blank_map()
    for rect in [
        (1, 1, 7, 6),
        (9, 1, 14, 6),
        (17, 1, 20, 6),
        (1, 8, 7, 14),
        (9, 9, 14, 14),
        (16, 8, 20, 14),
        (1, 16, 7, 20),
        (15, 16, 20, 20),
        (9, 16, 13, 19),
    ]:
        _carve(g, *rect)
    for rect in [
        (7, 3, 9, 3),
        (14, 4, 17, 4),
        (4, 6, 4, 8),
        (18, 6, 18, 8),
        (7, 11, 9, 11),
        (14, 11, 16, 11),
        (4, 14, 4, 16),
        (11, 14, 11, 16),
        (13, 18, 15, 18),
        (7, 18, 9, 18),
        (18, 14, 18, 16),
        (11, 6, 11, 9),
    ]:
        _carve(g, *rect)
    for x, y in [
        (11, 3),
        (12, 3),
        (11, 4),
        (18, 13),
        (5, 12),
        (2, 9),
        (13, 18),
        (10, 10),
        (10, 11),
        (3, 3),
        (19, 5),
    ]:
        _put(g, x, y, "M" if (x + y) % 2 else "#")
    _decorate_walls(g, 1)
    enemies = [
        ("trooper", 5, 3),
        ("trooper", 12, 2),
        ("trooper", 12, 12),
        ("trooper", 3, 11),
        ("trooper", 11, 18),
        ("drone", 18, 4),
        ("drone", 18, 12),
        ("drone", 10, 16),
    ]
    pickups = [
        ("ammo", 2, 10),
        ("ammo", 12, 17),
        ("ammo", 6, 17),
        ("ammo", 3, 6),
        ("health", 3, 9),
        ("health", 18, 9),
        ("health", 12, 16),
        ("nova", 19, 16),
    ]
    intel = [(13, 5), (3, 13), (19, 17)]
    return _finish(g, (2, 19), (19, 19), enemies, pickups, intel, None)


def _build_level_two() -> tuple[list[str], list[EnemySpec], list[PickupSpec]]:
    g = _blank_map()
    _carve(g, 9, 1, 12, 20)
    for rect in [(1, 2, 6, 9), (15, 2, 20, 9), (1, 12, 6, 18), (15, 12, 20, 18)]:
        _carve(g, *rect)
    for rect in [
        (6, 4, 9, 5),
        (12, 4, 15, 5),
        (6, 15, 9, 16),
        (12, 15, 15, 16),
        (8, 18, 13, 19),
    ]:
        _carve(g, *rect)
    for x, y in [
        (9, 7),
        (9, 8),
        (12, 12),
        (12, 13),
        (10, 10),
        (11, 16),
        (4, 4),
        (17, 4),
        (4, 14),
        (17, 14),
        (9, 2),
        (12, 2),
        (2, 8),
        (19, 8),
        (2, 17),
        (19, 17),
    ]:
        _put(g, x, y, "M" if (x * 3 + y) % 4 else "#")
    _decorate_walls(g, 2)
    enemies = [
        ("trooper", 3, 5),
        ("trooper", 5, 16),
        ("trooper", 10, 6),
        ("trooper", 11, 12),
        ("trooper", 18, 6),
        ("trooper", 16, 16),
        ("drone", 10, 4),
        ("drone", 3, 13),
        ("drone", 17, 10),
        ("drone", 12, 17),
        ("brute", 4, 7),
        ("brute", 17, 16),
    ]
    pickups = [
        ("ammo", 3, 15),
        ("ammo", 18, 8),
        ("ammo", 11, 18),
        ("ammo", 5, 3),
        ("health", 4, 13),
        ("health", 17, 13),
        ("health", 10, 8),
        ("nova", 19, 19),
    ]
    intel = [(2, 3), (18, 3), (2, 18)]
    return _finish(g, (10, 19), (10, 2), enemies, pickups, intel, None)


def _build_level_three() -> tuple[list[str], list[EnemySpec], list[PickupSpec]]:
    g = _blank_map()
    _carve(g, 3, 3, 18, 18)
    _carve(g, 1, 16, 7, 20)
    _carve(g, 14, 16, 20, 20)
    _carve(g, 1, 1, 6, 6)
    _carve(g, 15, 1, 20, 6)
    for y in range(8, 14):
        for x in range(8, 14):
            g[y][x] = "C"
    hazards = [
        (7, 7),
        (7, 8),
        (7, 9),
        (7, 10),
        (7, 11),
        (7, 12),
        (7, 13),
        (7, 14),
        (14, 7),
        (14, 8),
        (14, 9),
        (14, 10),
        (14, 11),
        (14, 12),
        (14, 13),
        (14, 14),
        (9, 7),
        (10, 7),
        (11, 7),
        (12, 7),
        (9, 14),
        (10, 14),
        (11, 14),
        (12, 14),
        (5, 10),
        (16, 10),
    ]
    for x, y in [
        (4, 6),
        (5, 6),
        (4, 15),
        (5, 15),
        (16, 6),
        (17, 6),
        (16, 15),
        (17, 15),
        (9, 3),
        (12, 3),
        (9, 18),
        (12, 18),
        (18, 4),
        (3, 9),
        (18, 17),
        (3, 12),
    ]:
        _put(g, x, y, "M" if (x + y) % 3 else "#")
    for x, y in [(2, 4), (19, 4), (2, 19), (19, 19)]:
        _put(g, x, y, "N")
    _decorate_walls(g, 3)
    enemies = [
        ("trooper", 5, 4),
        ("trooper", 11, 4),
        ("trooper", 15, 4),
        ("trooper", 18, 8),
        ("trooper", 4, 18),
        ("trooper", 10, 17),
        ("trooper", 16, 18),
        ("drone", 10, 8),
        ("drone", 13, 11),
        ("drone", 6, 8),
        ("drone", 15, 13),
        ("brute", 18, 5),
        ("brute", 3, 14),
        ("brute", 12, 17),
    ]
    pickups = [
        ("ammo", 2, 4),
        ("ammo", 19, 15),
        ("ammo", 10, 19),
        ("ammo", 17, 8),
        ("health", 5, 11),
        ("health", 16, 11),
        ("health", 11, 18),
        ("nova", 19, 18),
    ]
    intel = [(4, 3), (18, 3), (3, 18)]
    return _finish(g, (2, 19), (18, 19), enemies, pickups, intel, None, hazards)


def _build_level_four() -> tuple[list[str], list[EnemySpec], list[PickupSpec]]:
    g = _blank_map()
    _carve(g, 2, 2, 19, 19)
    for rect in [
        (5, 5, 6, 6),
        (15, 5, 16, 6),
        (5, 13, 6, 14),
        (15, 13, 16, 14),
        (9, 9, 9, 9),
        (12, 9, 12, 9),
        (7, 6, 7, 6),
        (15, 6, 15, 6),
    ]:
        _carve(g, *rect, "#")
    for x, y in [(2, 8), (19, 8), (2, 16), (19, 16)]:
        _put(g, x, y, "M")
    _decorate_walls(g, 4)
    enemies = [
        ("trooper", 4, 3),
        ("trooper", 17, 3),
        ("trooper", 4, 10),
        ("trooper", 17, 10),
        ("trooper", 9, 15),
        ("trooper", 13, 15),
        ("drone", 8, 6),
        ("drone", 14, 6),
        ("drone", 3, 14),
        ("drone", 18, 14),
        ("brute", 3, 7),
        ("brute", 18, 7),
    ]
    pickups = [
        ("ammo", 3, 11),
        ("ammo", 18, 11),
        ("ammo", 8, 17),
        ("ammo", 14, 17),
        ("health", 4, 16),
        ("health", 17, 16),
        ("health", 10, 12),
        ("health", 11, 12),
        ("nova", 2, 3),
        ("nova", 19, 3),
    ]
    intel = [(3, 17), (7, 2), (14, 2)]
    return _finish(g, (11, 19), (18, 18), enemies, pickups, intel, (11, 4))


# ---------------------------------------------------------------------------
# Themes
# ---------------------------------------------------------------------------
DOCKS_THEME = Theme(
    key="docks",
    accent=CYAN,
    accent_2=ORANGE,
    sky_high=(6, 12, 31, 255),
    sky_low=(24, 79, 105, 255),
    floor_far=(31, 76, 90, 255),
    floor_near=(12, 27, 36, 255),
    fog=(8, 21, 34, 255),
    wall_base=(34, 72, 86, 255),
    wall_dark=(14, 31, 42, 255),
    wall_light=(83, 147, 154, 255),
    wall_metal=(61, 77, 92, 255),
    hazard=(255, 91, 54, 255),
    outdoor=True,
    ambient_particles="rain",
)

SKY_THEME = Theme(
    key="sky",
    accent=MAGENTA,
    accent_2=CYAN,
    sky_high=(17, 10, 43, 255),
    sky_low=(109, 45, 92, 255),
    floor_far=(66, 49, 96, 255),
    floor_near=(22, 18, 43, 255),
    fog=(28, 18, 48, 255),
    wall_base=(62, 55, 104, 255),
    wall_dark=(25, 22, 50, 255),
    wall_light=(143, 102, 190, 255),
    wall_metal=(86, 79, 107, 255),
    hazard=(255, 119, 52, 255),
    outdoor=True,
    ambient_particles="embers",
)

REACTOR_THEME = Theme(
    key="reactor",
    accent=ORANGE,
    accent_2=GREEN,
    sky_high=(11, 8, 17, 255),
    sky_low=(61, 23, 21, 255),
    floor_far=(65, 37, 31, 255),
    floor_near=(22, 14, 17, 255),
    fog=(22, 13, 15, 255),
    wall_base=(75, 46, 38, 255),
    wall_dark=(31, 20, 19, 255),
    wall_light=(153, 91, 51, 255),
    wall_metal=(80, 67, 61, 255),
    hazard=(255, 77, 35, 255),
    outdoor=False,
    ambient_particles="embers",
)

CITADEL_THEME = Theme(
    key="citadel",
    accent=GOLD,
    accent_2=VIOLET,
    sky_high=(10, 7, 24, 255),
    sky_low=(64, 31, 91, 255),
    floor_far=(51, 39, 75, 255),
    floor_near=(17, 14, 31, 255),
    fog=(15, 11, 29, 255),
    wall_base=(53, 42, 80, 255),
    wall_dark=(20, 17, 37, 255),
    wall_light=(128, 99, 169, 255),
    wall_metal=(91, 70, 57, 255),
    hazard=(255, 195, 70, 255),
    outdoor=False,
    ambient_particles="dust",
)


def _build_levels() -> list[LevelDef]:
    l1_rows, l1_enemies, l1_pickups = _build_level_one()
    l2_rows, l2_enemies, l2_pickups = _build_level_two()
    l3_rows, l3_enemies, l3_pickups = _build_level_three()
    l4_rows, l4_enemies, l4_pickups = _build_level_four()
    return [
        LevelDef(
            index=0,
            code="SECTOR 01 // DOCKS",
            name="NEON DOCKS",
            subtitle="THE CITY'S LUNGS ARE ON FIRE",
            briefing=(
                "Vex's scavenger legion has sealed the docks and cut the city's power relay. "
                "Drop into the container yards, purge the occupation force, and reach the extraction beacon."
            ),
            directive="PURGE ALL HOSTILES // REACH EXTRACTION",
            hint="Dash with SHIFT. Your AEGIS shield automatically recharges after a short delay.",
            theme=DOCKS_THEME,
            rows=l1_rows,
            start=(2.5, 19.5),
            exit=(19.5, 19.5),
            enemies=l1_enemies,
            pickups=l1_pickups,
            intel=[(13.5, 5.5), (3.5, 13.5), (19.5, 17.5)],
            threat_level="ELEVATED",
            recommended="PULSE BLASTER",
            music_pitch=0.92,
        ),
        LevelDef(
            index=1,
            code="SECTOR 02 // SKYWAY",
            name="SKYBRIDGE NINE",
            subtitle="NO GROUND. NO MERCY.",
            briefing=(
                "A Vex gunship wing is using Skybridge Nine as a forward staging ground. "
                "Fight across the span, break the blockade, and reach the roof beacon."
            ),
            directive="BREAK THE BLOCKADE // REACH EXTRACTION",
            hint="Scatter Cannon unlocked. Brutes telegraph heavy bursts - strafe or dash out of the cone.",
            theme=SKY_THEME,
            rows=l2_rows,
            start=(10.5, 19.5),
            exit=(10.5, 2.5),
            enemies=l2_enemies,
            pickups=l2_pickups,
            intel=[(2.5, 3.5), (18.5, 3.5), (2.5, 18.5)],
            threat_level="SEVERE",
            recommended="SCATTER CANNON",
            music_pitch=0.99,
        ),
        LevelDef(
            index=2,
            code="SECTOR 03 // CORE",
            name="REACTOR ZERO",
            subtitle="THE CORE IS GOING CRITICAL",
            briefing=(
                "The occupation force is overloading Reactor Zero to black out the eastern grid. "
                "Vent the plasma ring, destroy the Warden's guards, and clear a path to extraction."
            ),
            directive="CONTAIN THE MELTDOWN // REACH EXTRACTION",
            hint="Plasma pools inflict burn damage. Nova Lance unlocked - it punches through armor.",
            theme=REACTOR_THEME,
            rows=l3_rows,
            start=(2.5, 19.5),
            exit=(18.5, 19.5),
            enemies=l3_enemies,
            pickups=l3_pickups,
            intel=[(4.5, 3.5), (18.5, 3.5), (3.5, 18.5)],
            threat_level="CRITICAL",
            recommended="NOVA LANCE",
            music_pitch=1.04,
        ),
        LevelDef(
            index=3,
            code="SECTOR 04 // CITADEL",
            name="TITAN CITADEL",
            subtitle="THE LAST HERO. THE FINAL TITAN.",
            briefing=(
                "Overlord Vex has barricaded himself inside the Titan Citadel with the last of his guard. "
                "The city is watching. Break the throne, destroy Vex, and end the Eclipse Protocol."
            ),
            directive="DESTROY OVERLORD VEX",
            hint="Vex's core is exposed between phases. Clear the adds and keep moving - nowhere is safe.",
            theme=CITADEL_THEME,
            rows=l4_rows,
            start=(11.5, 19.5),
            exit=(18.5, 18.5),
            enemies=l4_enemies,
            pickups=l4_pickups,
            intel=[(3.5, 17.5), (7.5, 2.5), (14.5, 2.5)],
            boss=(11.5, 4.5),
            boss_name="OVERLORD VEX",
            boss_hp=1450.0,
            threat_level="APOCALYPSE",
            recommended="NOVA LANCE",
            music_pitch=1.1,
        ),
    ]


LEVELS = _build_levels()

THREAT_COLORS = {
    "ELEVATED": ORANGE,
    "SEVERE": RED,
    "CRITICAL": (255, 74, 52, 255),
    "APOCALYPSE": VIOLET,
}

WEAPON_UNLOCK_HINTS = {
    1: "SCATTER CANNON ONLINE",
    2: "NOVA LANCE ONLINE",
}
