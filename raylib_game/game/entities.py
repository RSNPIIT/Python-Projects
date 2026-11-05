"""Gameplay entities and tuning data."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .config import (
    BLUE,
    CYAN,
    GOLD,
    GREEN,
    MAGENTA,
    ORANGE,
    RED,
    VIOLET,
    WHITE,
    clamp,
)

# ---------------------------------------------------------------------------
# Weapons
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Weapon:
    key: str
    name: str
    short_name: str
    description: str
    damage: float
    cooldown: float
    ammo_cost: int
    pellets: int
    spread: float
    max_range: float
    automatic: bool
    pierce: int
    sound: str
    color: tuple[int, int, int, int]
    muzzle_color: tuple[int, int, int, int]
    recoil: float
    unlock_mission: int
    tracer: str


WEAPONS: tuple[Weapon, ...] = (
    Weapon(
        key="pulse",
        name="PULSE BLASTER",
        short_name="PULSE",
        description="Reliable rapid-fire plasma sidearm. Automatic.",
        damage=17.0,
        cooldown=0.135,
        ammo_cost=1,
        pellets=1,
        spread=0.010,
        max_range=24.0,
        automatic=True,
        pierce=0,
        sound="pulse",
        color=ORANGE,
        muzzle_color=(255, 196, 92, 255),
        recoil=0.22,
        unlock_mission=0,
        tracer="pulse",
    ),
    Weapon(
        key="scatter",
        name="SCATTER CANNON",
        short_name="SCATTER",
        description="Eight-pellet energy burst. Devastating up close.",
        damage=9.0,
        cooldown=0.68,
        ammo_cost=2,
        pellets=8,
        spread=0.115,
        max_range=12.0,
        automatic=False,
        pierce=0,
        sound="scatter",
        color=GOLD,
        muzzle_color=(255, 156, 64, 255),
        recoil=0.62,
        unlock_mission=1,
        tracer="scatter",
    ),
    Weapon(
        key="lance",
        name="NOVA LANCE",
        short_name="LANCE",
        description="High-impact rail spear. Pierces up to four targets.",
        damage=92.0,
        cooldown=0.95,
        ammo_cost=3,
        pellets=1,
        spread=0.001,
        max_range=34.0,
        automatic=False,
        pierce=4,
        sound="lance",
        color=CYAN,
        muzzle_color=(180, 250, 255, 255),
        recoil=0.52,
        unlock_mission=2,
        tracer="lance",
    ),
)

WEAPONS_BY_KEY = {weapon.key: weapon for weapon in WEAPONS}


# ---------------------------------------------------------------------------
# Enemy tuning
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class EnemyKind:
    key: str
    name: str
    hp: float
    speed: float
    radius: float
    height: float
    floor_offset: float
    preferred_range: float
    attack_range: float
    attack_cooldown: float
    windup: float
    damage: float
    projectile_speed: float
    projectiles: int
    spread: float
    score: int
    accent: tuple[int, int, int, int]
    min_mission: int = 0


ENEMY_KINDS: dict[str, EnemyKind] = {
    "trooper": EnemyKind(
        key="trooper",
        name="VEX TROOPER",
        hp=72.0,
        speed=1.50,
        radius=0.29,
        height=0.94,
        floor_offset=0.04,
        preferred_range=4.7,
        attack_range=11.0,
        attack_cooldown=1.45,
        windup=0.38,
        damage=9.0,
        projectile_speed=7.6,
        projectiles=1,
        spread=0.025,
        score=130,
        accent=RED,
    ),
    "drone": EnemyKind(
        key="drone",
        name="WRAITH DRONE",
        hp=48.0,
        speed=2.05,
        radius=0.31,
        height=0.68,
        floor_offset=0.55,
        preferred_range=5.0,
        attack_range=9.0,
        attack_cooldown=1.15,
        windup=0.28,
        damage=6.5,
        projectile_speed=8.6,
        projectiles=2,
        spread=0.045,
        score=100,
        accent=MAGENTA,
    ),
    "brute": EnemyKind(
        key="brute",
        name="JUGGERNAUT",
        hp=240.0,
        speed=0.95,
        radius=0.46,
        height=1.43,
        floor_offset=0.0,
        preferred_range=3.2,
        attack_range=8.5,
        attack_cooldown=2.05,
        windup=0.56,
        damage=14.0,
        projectile_speed=6.2,
        projectiles=4,
        spread=0.10,
        score=340,
        accent=ORANGE,
        min_mission=1,
    ),
    "boss": EnemyKind(
        key="boss",
        name="OVERLORD VEX",
        hp=1450.0,
        speed=0.82,
        radius=0.82,
        height=2.38,
        floor_offset=0.0,
        preferred_range=6.0,
        attack_range=15.0,
        attack_cooldown=2.0,
        windup=0.55,
        damage=16.0,
        projectile_speed=6.8,
        projectiles=3,
        spread=0.07,
        score=7000,
        accent=VIOLET,
    ),
}


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
class Player:
    def __init__(self, x: float, y: float, weapon_count: int = 1) -> None:
        self.x = x
        self.y = y
        self.angle = -math.pi * 0.5
        self.look = 0.0
        self.radius = 0.24
        self.weapon_count = max(1, min(len(WEAPONS), weapon_count))
        self.weapon_index = 0
        self.health = 100.0
        self.max_health = 100.0
        self.shield = 100.0
        self.max_shield = 100.0
        self.energy = 100
        self.max_energy = 180
        self.nova = 28.0
        self.recoil = 0.0
        self.muzzle_flash = 0.0
        self.weapon_cooldown = 0.0
        self.switch_cooldown = 0.0
        self.fire_held = False
        self.ads = False
        self.ads_blend = 0.0
        self.bob_time = 0.0
        self.move_amount = 0.0
        self.dash_time = 0.0
        self.dash_cooldown = 0.0
        self.dash_dir = (0.0, 0.0)
        self.iframe = 0.0
        self.aegis_time = 0.0
        self.aegis_cooldown = 0.0
        self.last_damage_time = 99.0
        self.hit_flash = 0.0
        self.damage_direction = 0.0
        self.hazard_tick = 0.0
        self.shake = 0.0
        self.step_phase = 0.0
        self.frozen_look = False

    @property
    def weapon(self) -> Weapon:
        return WEAPONS[self.weapon_index]

    def can_switch_to(self, index: int) -> bool:
        return 0 <= index < self.weapon_count

    def switch_weapon(self, index: int) -> bool:
        if not self.can_switch_to(index) or index == self.weapon_index:
            return False
        self.weapon_index = index
        self.switch_cooldown = 0.2
        self.weapon_cooldown = max(self.weapon_cooldown, 0.12)
        return True

    def cycle_weapon(self, direction: int) -> bool:
        if self.weapon_count <= 1:
            return False
        target = (self.weapon_index + direction) % self.weapon_count
        return self.switch_weapon(target)

    def take_damage(self, amount: float, now: float, source_angle: float | None = None) -> float:
        if self.iframe > 0 or amount <= 0:
            return 0.0
        if self.aegis_time > 0:
            amount *= 0.22
        shield_damage = min(self.shield, amount)
        self.shield -= shield_damage
        remaining = amount - shield_damage
        if remaining > 0:
            self.health -= remaining
        self.last_damage_time = now
        self.hit_flash = max(self.hit_flash, clamp(amount / 30.0, 0.25, 1.0))
        if source_angle is not None:
            self.damage_direction = source_angle
        self.shake = max(self.shake, clamp(amount / 45.0, 0.06, 0.62))
        return amount

    def heal(self, amount: float) -> float:
        before = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - before

    def add_energy(self, amount: int) -> int:
        before = self.energy
        self.energy = min(self.max_energy, self.energy + amount)
        return self.energy - before

    def add_nova(self, amount: float) -> float:
        before = self.nova
        self.nova = clamp(self.nova + amount, 0.0, 100.0)
        return self.nova - before

    def update_timers(self, dt: float, now: float) -> None:
        self.weapon_cooldown = max(0.0, self.weapon_cooldown - dt)
        self.switch_cooldown = max(0.0, self.switch_cooldown - dt)
        self.dash_cooldown = max(0.0, self.dash_cooldown - dt)
        self.aegis_cooldown = max(0.0, self.aegis_cooldown - dt)
        self.iframe = max(0.0, self.iframe - dt)
        self.aegis_time = max(0.0, self.aegis_time - dt)
        self.hit_flash = max(0.0, self.hit_flash - dt * 3.2)
        self.shake = max(0.0, self.shake - dt * 1.8)
        self.recoil = max(0.0, self.recoil - dt * 7.0)
        self.muzzle_flash = max(0.0, self.muzzle_flash - dt * 18.0)
        if self.dash_time > 0:
            self.dash_time = max(0.0, self.dash_time - dt)
        if now - self.last_damage_time > 3.0:
            regen = 16.0 * dt
            self.shield = min(self.max_shield, self.shield + regen)
        self.ads_blend += ((1.0 if self.ads else 0.0) - self.ads_blend) * min(1.0, dt * 10.0)
        if self.health <= 0:
            self.health = 0.0


# ---------------------------------------------------------------------------
# Enemies
# ---------------------------------------------------------------------------
@dataclass
class Enemy:
    kind_key: str
    x: float
    y: float
    mission_index: int = 0
    hp: float = 1.0
    max_hp: float = 1.0
    alerted: bool = False
    attack_timer: float = 0.0
    windup: float = 0.0
    windup_total: float = 0.0
    hurt_flash: float = 0.0
    animation: float = 0.0
    strafe: float = 1.0
    strafe_timer: float = 1.0
    knockback_x: float = 0.0
    knockback_y: float = 0.0
    phase: int = 1
    invulnerable: float = 0.0
    phase_banner: float = 0.0
    alerted_once: bool = False
    spawn_time: float = 0.0
    dead: bool = False
    is_boss: bool = False
    aim_glow: float = 0.0
    hurt_source_angle: float = 0.0
    special_timer: float = 0.0
    summon_count: int = 0

    @property
    def kind(self) -> EnemyKind:
        return ENEMY_KINDS[self.kind_key]

    @classmethod
    def from_spec(cls, kind_key: str, x: float, y: float, mission_index: int) -> "Enemy":
        kind = ENEMY_KINDS[kind_key]
        scale = 1.0 + mission_index * 0.13
        hp = kind.hp * scale
        enemy = cls(
            kind_key=kind_key,
            x=x,
            y=y,
            mission_index=mission_index,
            hp=hp,
            max_hp=hp,
            is_boss=(kind_key == "boss"),
            attack_timer=0.6 + (x * 0.17 + y * 0.23) % 1.2,
        )
        enemy.phase = 1
        return enemy

    @classmethod
    def make_boss(cls, x: float, y: float, mission_index: int, hp: float) -> "Enemy":
        enemy = cls.from_spec("boss", x, y, mission_index)
        enemy.hp = hp
        enemy.max_hp = hp
        enemy.is_boss = True
        return enemy

    def apply_damage(self, amount: float, source_angle: float = 0.0) -> float:
        if self.invulnerable > 0:
            return 0.0
        actual = min(self.hp, amount)
        self.hp -= amount
        self.hurt_flash = 1.0
        self.hurt_source_angle = source_angle
        self.alerted = True
        if self.hp <= 0:
            self.hp = 0.0
            self.dead = True
        return actual

    def update_timers(self, dt: float, now: float) -> None:
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.hurt_flash = max(0.0, self.hurt_flash - dt * 5.0)
        self.animation += dt
        self.strafe_timer -= dt
        self.windup = max(0.0, self.windup - dt)
        self.invulnerable = max(0.0, self.invulnerable - dt)
        self.aim_glow = max(0.0, self.aim_glow - dt * 2.4)
        self.phase_banner = max(0.0, self.phase_banner - dt)
        self.spawn_time += dt
        if self.strafe_timer <= 0:
            self.strafe_timer = 0.8 + (self.x * 1.7 + self.y * 2.3) % 1.3
            self.strafe *= -1.0

    @property
    def alert_radius(self) -> float:
        return 26.0 if self.is_boss else 12.5

    @property
    def preferred_distance(self) -> float:
        return self.kind.preferred_range


# ---------------------------------------------------------------------------
# Projectiles / effects
# ---------------------------------------------------------------------------
@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    damage: float
    color: tuple[int, int, int, int]
    radius: float = 0.11
    life: float = 4.2
    from_boss: bool = False
    size: float = 0.13
    dead: bool = False
    spin: float = 0.0

    def update(self, dt: float, game_map, player) -> bool:
        """Advance projectile.  Returns True if it hit the player this frame."""
        self.life -= dt
        if self.life <= 0:
            self.dead = True
            return False
        distance = math.hypot(self.vx, self.vy) * dt
        steps = max(1, int(distance / 0.12))
        step_x = self.vx * dt / steps
        step_y = self.vy * dt / steps
        for _ in range(steps):
            nx = self.x + step_x
            ny = self.y + step_y
            if game_map.wall_at(int(nx), int(ny)):
                self.dead = True
                return False
            self.x, self.y = nx, ny
            if math.hypot(self.x - player.x, self.y - player.y) < player.radius + self.radius:
                if player.iframe <= 0:
                    self.dead = True
                    return True
        self.spin += dt * 12.0
        return False


@dataclass
class Particle:
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    life: float
    color: tuple[int, int, int, int]
    size: float = 0.1
    gravity: float = 4.5
    drag: float = 1.7
    glow: bool = False
    dead: bool = False

    def update(self, dt: float) -> None:
        self.life -= dt
        if self.life <= 0:
            self.dead = True
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        self.vz -= self.gravity * dt
        decay = max(0.0, 1.0 - self.drag * dt)
        self.vx *= decay
        self.vy *= decay
        if self.z <= 0.02:
            self.z = 0.02
            self.vz = abs(self.vz) * 0.25
            self.vx *= 0.72
            self.vy *= 0.72
            if abs(self.vz) < 0.2:
                self.vz = 0.0


@dataclass
class Pickup:
    kind: str
    x: float
    y: float
    phase: float = 0.0
    amount: float = 0.0
    dead: bool = False
    life: float = 30.0


@dataclass
class IntelShard:
    x: float
    y: float
    phase: float = 0.0
    collected: bool = False


@dataclass
class FloatingText:
    x: float
    y: float
    z: float
    text: str
    color: tuple[int, int, int, int]
    life: float = 0.8
    max_life: float = 0.8
    dead: bool = False


@dataclass
class HudEvent:
    text: str
    color: tuple[int, int, int, int] = WHITE
    life: float = 2.0
    max_life: float = 2.0
    big: bool = False
    dead: bool = False


def ray_circle_intersection(
    origin_x: float,
    origin_y: float,
    dir_x: float,
    dir_y: float,
    center_x: float,
    center_y: float,
    radius: float,
) -> float | None:
    """Distance along the normalized ray to the first circle intersection."""
    ox = center_x - origin_x
    oy = center_y - origin_y
    projection = ox * dir_x + oy * dir_y
    if projection <= 0:
        return None
    closest_sq = ox * ox + oy * oy - projection * projection
    radius_sq = radius * radius
    if closest_sq > radius_sq:
        return None
    offset = math.sqrt(max(0.0, radius_sq - closest_sq))
    first = projection - offset
    return first if first > 0 else None


def score_for_kill(enemy: Enemy, combo: int) -> int:
    base = enemy.kind.score + (2500 if enemy.is_boss else 0)
    return int(base * (1.0 + max(0, combo) * 0.15))


def damage_scale_for_mission(mission_index: int) -> float:
    return 1.0 + mission_index * 0.10
