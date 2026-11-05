"""THORNSPIRE — states, run loop, scoring, camera and presentation glue."""

from __future__ import annotations

import json
import math
import random
import time as _time
from pathlib import Path

import pygame

from .audio import Audio
from .background import BackgroundDirector
from .bot import AutoPilot
from .constants import (
    ARMOR_INVULN,
    ARMOR_VALUE,
    BIOMES,
    CAMERA_LOOKAHEAD,
    CAMERA_SMOOTH_X,
    CAMERA_SMOOTH_Y,
    CHRONO_VALUE,
    COIN_VALUE,
    COMBO_MAX,
    COMBO_STEP,
    COMBO_WINDOW,
    DASH_TIME,
    DISTANCE_POINTS,
    FALL_LIMIT,
    FPS,
    GEM_VALUE,
    HEART_VALUE,
    INVULN_TIME,
    JUMP_VELOCITY,
    LOOP_BONUS,
    MAX_HEARTS,
    PLAYER,
    SCREEN_H,
    SCREEN_W,
    START_ARMOR,
    START_HEARTS,
    TITLE,
    TRIAL_CHRONO,
    TRIAL_TIME,
    UI,
    WINDOW_TITLE,
)
from .level import World
from .particles import AmbientField, ParticleSystem
from .player import Inputs, Player
from .renderer import create_renderer
from .ui import UI as GameUI
from .utils import (
    clamp,
    color_lerp,
    draw_glow,
    exp_smooth,
    format_score,
    palette_lerp,
    sign,
    smoothstep,
)

SAVE_PATH = Path(__file__).resolve().parent.parent / "save.json"
SHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"

DEFAULT_SAVE = {
    "best_loop": 0,
    "best_trial": 0,
    "best_distance_loop": 0,
    "best_distance_trial": 0,
    "total_coins": 0,
    "total_gems": 0,
    "runs": 0,
    "muted": False,
}


class Game:
    def __init__(
        self,
        seed: int | None = None,
        mode: str = "loop",
        headless: bool = False,
        mute: bool = False,
        autoplay: bool = False,
        god: bool = False,
    ) -> None:
        self.seed = seed
        self.mode = mode if mode in ("loop", "trial") else "loop"
        self.headless = headless
        self.autopilot = autoplay
        self.god = god

        self.save = self._load_save()
        for key, value in DEFAULT_SAVE.items():
            self.save.setdefault(key, value)

        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self._set_icon()
        pygame.key.set_repeat(0)
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False
        self.debug_fps = False

        self.time = 0.0
        self.elapsed = 0.0
        self.state = "title"

        self.audio = Audio(muted=bool(self.save.get("muted", False)) or mute)
        self.ui = GameUI()
        self.renderer, self.gpu = create_renderer()
        self.backdrop = BackgroundDirector()
        self.particles = ParticleSystem()
        self.ambient = AmbientField(80)
        self.bot = AutoPilot()

        self.world_surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

        # menu
        self.title_options = [
            ("ENDLESS LOOP", "run forever · loop the biomes · one run"),
            ("TIME TRIAL", "90 seconds · collect · chrono shards add time"),
        ]
        self.title_index = 0 if self.mode == "loop" else 1
        self.menu_index = 0
        self.title_total = 0

        # gameplay state (safe defaults so drawing helpers never explode)
        self.player = None
        self.world = None
        self.palette = BIOMES[0]
        self.biome_index = 0
        self.blend_from = BIOMES[0]
        self.blend_to = BIOMES[0]
        self.blend_t = 10.0
        self.cam = pygame.Vector2(0, 0)
        self.score = 0
        self.final_score = 0
        self.time_bonus = 0
        self.coins = 0
        self.gems = 0
        self.chronos = 0
        self.hearts_picked = 0
        self.distance = 0
        self.scored_distance = 0
        self.loop_number = 1
        self.combo_count = 0
        self.combo_timer = 0.0
        self.combo_mult = 1
        self.time_left = TRIAL_TIME
        self.elapsed = 0.0
        self.safe_pos = (0.0, 0.0)
        self.active_checkpoint = None
        self.safe_timer = 0.0
        self.hitstop = 0.0
        self.shake = 0.0
        self.flash = 0.0
        self.end_reason = ""
        self.new_best = False
        self.death_timer = 0.0
        self.banner_timer = 0.0
        self.banner_total = 3.2
        self.banner_title = ""
        self.banner_sub = ""
        self.hints = True

        self.jump_queued = False
        self.dash_queued = False
        self._mode_change_cooldown = 0.0

        self._init_title_world()

    # ------------------------------------------------------------------
    # persistence / window
    # ------------------------------------------------------------------
    def _load_save(self) -> dict:
        try:
            if SAVE_PATH.exists():
                data = json.loads(SAVE_PATH.read_text())
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
        return dict(DEFAULT_SAVE)

    def save_progress(self) -> None:
        try:
            SAVE_PATH.write_text(json.dumps(self.save, indent=2))
        except Exception:
            pass

    def _set_icon(self) -> None:
        icon = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.polygon(icon, (150, 120, 240),
                            [(32, 4), (50, 28), (32, 60), (14, 28)])
        pygame.draw.polygon(icon, (210, 190, 255),
                            [(32, 4), (41, 28), (32, 42)])
        pygame.draw.polygon(icon, (255, 220, 140),
                            [(32, 22), (38, 32), (32, 44), (26, 32)])
        pygame.display.set_icon(icon)

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        try:
            flags = (pygame.FULLSCREEN | pygame.SCALED) if self.fullscreen else 0
            self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
            pygame.display.set_caption(WINDOW_TITLE)
        except Exception:
            self.screen = pygame.display.get_surface()

    def _screenshot(self) -> None:
        try:
            SHOT_DIR.mkdir(parents=True, exist_ok=True)
            name = _time.strftime("thornspire_%Y%m%d_%H%M%S.png")
            pygame.image.save(self.screen, str(SHOT_DIR / name))
        except Exception:
            pass

    # ------------------------------------------------------------------
    # title
    # ------------------------------------------------------------------
    def _init_title_world(self) -> None:
        self.title_world = World(seed=20260301, mode="loop")
        self.title_world.ensure_until(3600)
        self.title_cam = pygame.Vector2(430.0, 196.0)
        self.palette = BIOMES[0]

    def _update_title(self, dt: float) -> None:
        self.title_world.time += dt
        self.title_world.update_moving_platforms(dt, None, self.time)
        self.title_cam.x = 430.0 + math.sin(self.time * 0.045) * 90.0
        self.title_cam.y = 196.0 + math.sin(self.time * 0.03) * 10.0
        self.ambient.update(dt, 7.0)
        self.palette = BIOMES[0]
        self.biome_index = 0

    def start_run(self, mode: str | None = None, seed: int | None = None) -> None:
        if mode in ("loop", "trial"):
            self.mode = mode
        seed = seed if seed is not None else self.seed
        if seed is None:
            seed = random.randrange(1, 2**31 - 1)
        self.run_seed = seed
        self.world = World(seed, self.mode)
        self.player = Player(self.world.spawn_x, self.world.spawn_y)
        self.player.hearts = START_HEARTS
        self.player.armor = START_ARMOR
        self.safe_pos = (self.world.spawn_x, self.world.spawn_y)
        self.active_checkpoint = None
        self.safe_timer = 0.0

        self.score = 0
        self.final_score = 0
        self.time_bonus = 0
        self.coins = 0
        self.gems = 0
        self.chronos = 0
        self.hearts_picked = 0
        self.distance = 0
        self.scored_distance = 0
        self.loop_number = 1
        self.combo_count = 0
        self.combo_timer = 0.0
        self.combo_mult = 1
        self.time_left = TRIAL_TIME
        self.elapsed = 0.0
        self.hitstop = 0.0
        self.shake = 0.0
        self.flash = 0.0
        self.end_reason = ""
        self.new_best = False
        self.death_timer = 0.0
        self.hints = True

        self.biome_index = self.world.biome_at(self.player.x)
        self.palette = BIOMES[self.biome_index]
        self.blend_from = self.palette
        self.blend_to = self.palette
        self.blend_t = 10.0
        self._set_banner(BIOMES[self.biome_index]["name"],
                         BIOMES[self.biome_index]["tagline"])
        self.particles.clear()
        self.ambient = AmbientField(80)
        self.cam = pygame.Vector2(0, 0)
        self._snap_camera()
        self.state = "playing"
        self.menu_index = 0
        self.jump_queued = False
        self.dash_queued = False
        self.audio.play("select")

    def _to_title(self) -> None:
        self.state = "title"
        self.menu_index = 0
        self.title_index = 0 if self.mode == "loop" else 1
        self.palette = BIOMES[0]
        self.biome_index = 0
        self.particles.clear()
        self.banner_timer = 0.0
        self.audio.play("select")

    def _set_banner(self, title: str, sub: str, duration: float = 3.2) -> None:
        self.banner_title = title
        self.banner_sub = sub
        self.banner_timer = duration
        self.banner_total = duration

    # ------------------------------------------------------------------
    # input plumbing
    # ------------------------------------------------------------------
    def _poll_inputs(self) -> Inputs:
        keys = pygame.key.get_pressed()
        inp = Inputs(
            left=bool(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            right=bool(keys[pygame.K_d] or keys[pygame.K_RIGHT]),
            up=bool(keys[pygame.K_w] or keys[pygame.K_UP]),
            down=bool(keys[pygame.K_s] or keys[pygame.K_DOWN]),
            jump_pressed=self.jump_queued,
            jump_held=bool(keys[pygame.K_SPACE]),
            dash_pressed=self.dash_queued,
        )
        self.jump_queued = False
        self.dash_queued = False
        return inp

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_progress()
                self.running = False
                return
            if event.type == pygame.WINDOWFOCUSLOST and self.state == "playing":
                self.state = "paused"
                self.menu_index = 0
                self.jump_queued = False
                self.dash_queued = False
                continue
            if event.type != pygame.KEYDOWN:
                continue
            key = event.key
            if key == pygame.K_F11:
                self.toggle_fullscreen()
                continue
            if key == pygame.K_F12:
                self._screenshot()
                continue
            if key == pygame.K_F3:
                self.debug_fps = not self.debug_fps
                continue
            if key == pygame.K_m:
                self._toggle_mute()
                continue

            if self.state == "title":
                if key in (pygame.K_UP, pygame.K_w):
                    self.title_index = (self.title_index - 1) % len(self.title_options)
                    self.audio.play("select")
                elif key in (pygame.K_DOWN, pygame.K_s):
                    self.title_index = (self.title_index + 1) % len(self.title_options)
                    self.audio.play("select")
                elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    self.start_run("loop" if self.title_index == 0 else "trial")
                elif key == pygame.K_ESCAPE:
                    self.save_progress()
                    self.running = False
            elif self.state == "playing":
                if key in (pygame.K_ESCAPE, pygame.K_p):
                    self.state = "paused"
                    self.menu_index = 0
                    self.jump_queued = False
                    self.dash_queued = False
                    self.audio.play("select")
                elif key == pygame.K_SPACE:
                    self.jump_queued = True
                elif key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_x):
                    self.dash_queued = True
            elif self.state == "paused":
                if key in (pygame.K_UP, pygame.K_w):
                    self.menu_index = (self.menu_index - 1) % len(self.pause_items())
                    self.audio.play("select")
                elif key in (pygame.K_DOWN, pygame.K_s):
                    self.menu_index = (self.menu_index + 1) % len(self.pause_items())
                    self.audio.play("select")
                elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    self._pause_action()
                elif key in (pygame.K_ESCAPE, pygame.K_p):
                    self.state = "playing"
            elif self.state == "gameover":
                if key in (pygame.K_UP, pygame.K_w):
                    self.menu_index = (self.menu_index - 1) % len(self.over_items())
                    self.audio.play("select")
                elif key in (pygame.K_DOWN, pygame.K_s):
                    self.menu_index = (self.menu_index + 1) % len(self.over_items())
                    self.audio.play("select")
                elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    self._over_action()
                elif key == pygame.K_ESCAPE:
                    self._to_title()

    def pause_items(self) -> list[str]:
        return [
            "RESUME",
            "RESTART RUN",
            f"SOUND: {'OFF' if self.audio.muted else 'ON'}",
            "QUIT TO TITLE",
        ]

    def over_items(self) -> list[str]:
        return ["RUN AGAIN", "RETURN TO TITLE"]

    def _pause_action(self) -> None:
        if self.menu_index == 0:
            self.state = "playing"
        elif self.menu_index == 1:
            self.start_run(self.mode)
        elif self.menu_index == 2:
            self._toggle_mute()
        elif self.menu_index == 3:
            self._to_title()

    def _over_action(self) -> None:
        if self.menu_index == 0:
            self.start_run(self.mode)
        else:
            self._to_title()

    def _toggle_mute(self) -> None:
        muted = self.audio.toggle_mute()
        self.save["muted"] = muted
        self.save_progress()

    # ------------------------------------------------------------------
    # stepping
    # ------------------------------------------------------------------
    def step(self, dt: float) -> None:
        dt = max(0.0, min(dt, 1.0 / 20.0))
        self.time += dt
        if self.state == "title":
            self._update_title(dt)
        elif self.state == "playing":
            self._update_playing(dt)
        elif self.state == "dying":
            self._update_dying(dt)
        elif self.state == "gameover":
            self._update_gameover(dt)
        else:
            self.jump_queued = False
            self.dash_queued = False

        self.flash = max(0.0, self.flash - dt * 2.4)
        self.shake = max(0.0, self.shake - dt * 38.0)
        self.banner_timer = max(0.0, self.banner_timer - dt)

    def _update_playing(self, dt: float) -> None:
        if self.hitstop > 0.0:
            self.hitstop -= dt
            self.particles.update(dt * 0.35)
            self.ambient.update(dt * 0.35)
            return

        self.elapsed += dt
        if self.mode == "trial":
            self.time_left -= dt
            if self.time_left <= 0.0:
                self.time_left = 0.0
                self._end_run("time")
                return

        if self.autopilot:
            inp = self.bot.think(self.player, self.world, dt)
        else:
            inp = self._poll_inputs()

        self.world.update_moving_platforms(dt, self.player, self.time)
        self.player.update(dt, inp, self.world)
        self._consume_player_events()

        if not self.autopilot:
            if self.player.x < 18:
                self.player.x = 18
                if self.player.vx < 0:
                    self.player.vx = 0.0

        self.world.ensure_until(self.cam.x + SCREEN_W * 2.4)
        self.world.update(dt, self.player, self.cam.x)

        self._collect_pickups()
        self._check_checkpoints()
        if not self.god:
            self._check_hazards()
            if self.state != "playing":
                return
            self._check_enemies()
            if self.state != "playing":
                return
            self._check_projectiles()
            if self.state != "playing":
                return
            self._check_fall()
            if self.state != "playing":
                return

        self._update_safe_pos(dt)
        self._update_combo(dt)
        self._update_progress()
        self._update_biome(dt)
        self._update_camera(dt)
        self._update_player_fx()
        self.particles.update(dt)
        self.ambient.update(dt, 8.0 + 5.0 * math.sin(self.time * 0.2))

    def _update_dying(self, dt: float) -> None:
        self.death_timer -= dt
        self.particles.update(dt * 0.7)
        self.ambient.update(dt * 0.3)
        if self.world:
            self.world.time += dt
        if self.death_timer <= 0.0:
            self._finalize_run()

    def _update_gameover(self, dt: float) -> None:
        self.particles.update(dt * 0.3)
        self.ambient.update(dt * 0.25)
        if self.world:
            self.world.time += dt

    # ------------------------------------------------------------------
    # gameplay systems
    # ------------------------------------------------------------------
    def _consume_player_events(self) -> None:
        p = self.player
        pal = self.palette
        for ev in p.events:
            if ev == "jump":
                self.audio.play("jump")
                self.particles.dust(p.x + p.w / 2, p.y + p.h, pal["moss"], 5, 0.8)
            elif ev == "land":
                self.audio.play("land")
                self.particles.dust(p.x + p.w / 2, p.y + p.h, pal["moss"], 7, 1.1)
            elif ev == "wall_jump":
                self.audio.play("jump")
                self.particles.dust(p.x + p.w / 2, p.y + p.h * 0.5, pal["moss"], 6, 1.0)
            elif ev == "dash":
                self.audio.play("dash")
                self.shake = max(self.shake, 5.0)
                self.particles.burst(p.x + p.w / 2, p.y + p.h / 2, pal["accent"],
                                     10, 150, 0.35, 0, 4, "spark")
            elif ev == "grab":
                self.particles.dust(p.x + p.w / 2, p.y + p.h * 0.5, pal["moss"], 5, 0.7)
            elif ev == "slide":
                self.particles.trail(p.x + (0 if p.wall_dir > 0 else p.w),
                                     p.y + p.h * 0.7, pal["moss"], 1, 4, 15, 0.3)
            elif ev == "drop":
                self.particles.dust(p.x + p.w / 2, p.y + p.h, pal["rock_light"], 5, 0.7)

    def _update_player_fx(self) -> None:
        p = self.player
        palette = self.palette
        if p.dashing:
            self.particles.trail(p.x + p.w / 2, p.y + p.h / 2, palette["accent"],
                                 2, 5, 28, 0.3)
        if p.jump_boosting:
            self.particles.trail(p.x + p.w / 2 + random.uniform(-7, 7),
                                 p.y + p.h - random.uniform(0, 10),
                                 palette["accent2"], 1, 3, 15, 0.28)
        if p.hearts == 1 and random.random() < 0.12:
            self.particles.trail(p.x + p.w / 2 + random.uniform(-10, 10),
                                 p.y + random.uniform(4, 16),
                                 (255, 90, 100), 1, 3, 10, 0.4)

    def _collect_pickups(self) -> None:
        p = self.player
        pal = self.palette
        for pickup in self.world.pickups_near(p.rect.inflate(8, 6)):
            if pickup.collected:
                continue
            pickup.collected = True
            kind = pickup.kind
            mult = self.combo_mult
            if kind == "coin":
                self.coins += 1
                value = COIN_VALUE
                color = pal["coin"]
                self.audio.play("coin")
                self.particles.burst(pickup.x, pickup.y, color, 6, 90, 0.4, 120, 3, "spark")
            elif kind == "gem":
                self.gems += 1
                value = GEM_VALUE
                color = pal["gem"]
                self.audio.play("gem")
                self.particles.burst(pickup.x, pickup.y, color, 18, 170, 0.7, 80, 4, "glow")
                self.particles.ring(pickup.x, pickup.y, color, 18, 0.5)
                self.flash = max(self.flash, 0.18)
            elif kind == "heart":
                self.hearts_picked += 1
                value = HEART_VALUE
                color = (255, 126, 148)
                self.audio.play("heart")
                if not p.heal(1):
                    value += 40
                self.particles.burst(pickup.x, pickup.y, color, 12, 130, 0.6, 60, 4, "glow")
            elif kind == "chrono":
                self.chronos += 1
                value = CHRONO_VALUE
                color = (136, 244, 255)
                self.time_left += TRIAL_CHRONO
                self.audio.play("chrono")
                self.particles.burst(pickup.x, pickup.y, color, 12, 130, 0.6, 40, 4, "glow")
                self.particles.text(pickup.x, pickup.y - 18, f"+{int(TRIAL_CHRONO)}s",
                                    color, big=False)
            elif kind == "armor":
                value = ARMOR_VALUE
                color = (128, 238, 255)
                self.audio.play("armor")
                gained_armor = p.add_armor(1)
                if not gained_armor:
                    value += 50
                self.particles.burst(pickup.x, pickup.y, color, 14, 140, 0.65, 40, 4, "glow")
                self.particles.ring(pickup.x, pickup.y, color, 16, 0.5)
                self.particles.text(pickup.x, pickup.y - 20,
                                    "SHIELD +1" if gained_armor else "ARMOR FULL",
                                    color, big=False)
            else:
                continue

            self.combo_count += 1
            self.combo_timer = COMBO_WINDOW
            self.combo_mult = min(COMBO_MAX, 1 + self.combo_count // COMBO_STEP)
            gained = value * self.combo_mult
            self.score += gained
            if kind in ("gem", "heart", "chrono", "armor"):
                self.particles.text(pickup.x, pickup.y - 34,
                                    f"+{gained}", color, big=kind == "gem")
            elif self.combo_mult > 1:
                self.particles.text(pickup.x, pickup.y - 12, f"+{gained}", color, big=False)

    def _check_checkpoints(self) -> None:
        for cp in self.world.checkpoints_near(self.player.rect.inflate(6, 6)):
            if cp.active:
                continue
            cp.active = True
            self.active_checkpoint = cp
            healed = self.player.heal(1)
            self.score += 50
            self.flash = max(self.flash, 0.35)
            self.shake = max(self.shake, 4.0)
            self.audio.play("checkpoint")
            self.particles.ring(cp.x, cp.y - 40, self.palette["accent"], 26, 0.7)
            self.particles.burst(cp.x, cp.y - 40, self.palette["accent"], 16, 110, 0.8,
                                  20, 4)
            self.particles.text(cp.x, cp.y - 92, "CHECKPOINT", self.palette["accent"],
                                big=False)
            if healed:
                self.particles.text(cp.x, cp.y - 72, "+1 HEART", (255, 150, 160))

    def _check_hazards(self) -> None:
        p = self.player
        if p.invuln > 0:
            return
        hit = self.world.hazards_near(p.rect.inflate(-6, -4))
        if hit:
            source = hit[0].x + hit[0].w / 2
            self._hurt_player(source, reason="thorn")

    def _check_enemies(self) -> None:
        p = self.player
        if p.invuln > 0:
            return
        for enemy in self.world.enemies_near(p.rect.inflate(-7, -6)):
            self._hurt_player(enemy.x + enemy.w / 2, reason="enemy")
            return

    def _check_projectiles(self) -> None:
        p = self.player
        if p.invuln > 0:
            return
        for proj in self.world.projectiles:
            if proj.alive and proj.rect.colliderect(p.rect.inflate(-6, -6)):
                proj.alive = False
                self._hurt_player(proj.x, reason="thorn")
                return

    def _check_fall(self) -> None:
        p = self.player
        if p.y <= FALL_LIMIT:
            return
        if self.god:
            self._respawn(hearts=p.hearts, invuln=2.0)
            return
        if self.mode == "loop":
            p.hearts -= 1
            self.shake = 16
            self.flash = max(self.flash, 0.3)
            if p.hearts <= 0:
                self._end_run("death")
                return
            if self._respawn(hearts=p.hearts, invuln=2.2):
                self.particles.text(p.x, p.y - 24, "-1 HEART", (255, 120, 130))
                self.audio.play("hurt")
                self.shake = 12
        else:
            if self._respawn(hearts=max(2, p.hearts), invuln=2.2,
                             penalty=8.0, label="-8s"):
                self.audio.play("hurt")
                self.shake = 12

    def _hurt_player(self, source_x: float, reason: str = "hit") -> None:
        p = self.player
        if p.invuln > 0 or self.state != "playing" or self.god:
            return
        direction = sign(p.x + p.w / 2 - source_x) or -p.facing
        p.vx = direction * 330
        p.vy = -420
        p.on_ground = False
        p.dashing = False
        p.climbing = False
        p.vine = None
        self.combo_count = 0
        self.combo_timer = 0.0
        self.combo_mult = 1
        self.shake = 16
        self.hitstop = 0.055

        # Armor takes the hit first: shield break, no heart lost.
        if p.armor > 0:
            p.armor -= 1
            p.invuln = ARMOR_INVULN
            p.hurt_timer = 0.22
            self.flash = max(self.flash, 0.3)
            self.audio.play("shield")
            self.particles.burst(p.x + p.w / 2, p.y + p.h / 2, (128, 238, 255),
                                 24, 220, 0.65, 350, 4, "glow")
            self.particles.ring(p.x + p.w / 2, p.y + p.h * 0.5,
                                (150, 245, 255), 26, 0.55)
            self.particles.text(p.x + p.w / 2, p.y - 16, "SHIELD BREAK",
                                (150, 245, 255))
            return

        p.hearts -= 1
        p.invuln = INVULN_TIME
        p.hurt_timer = 0.3
        self.flash = max(self.flash, 0.25)
        self.audio.play("hurt")
        self.particles.burst(p.x + p.w / 2, p.y + p.h / 2, self.palette["danger"],
                             16, 200, 0.5, 700, 4, "spark")
        if p.hearts <= 0:
            if self.mode == "trial":
                p.hearts = 0
                self._trial_knockout()
            else:
                self._end_run("death")

    def _trial_knockout(self) -> None:
        if self.state != "playing":
            return
        self.flash = max(self.flash, 0.6)
        self.shake = 20
        if self.time_left - 15.0 <= 0.0:
            self.time_left = 0.0
            self._end_run("time")
            return
        self.time_left -= 15.0
        self._respawn(hearts=2, invuln=2.6)
        self.particles.text(self.player.x + self.player.w / 2,
                            self.player.y - 24, "-15s", UI["danger"], big=True)
        self.audio.play("death")

    def _respawn(self, hearts: int | None = None, invuln: float = 2.0,
                 penalty: float = 0.0, label: str | None = None) -> bool:
        p = self.player
        old_x, old_y = p.x + p.w / 2, p.y + p.h / 2
        if hearts is None:
            hearts = p.hearts
        if self.active_checkpoint is not None:
            x, y = self.active_checkpoint.respawn_pos()
        else:
            x, y = self.safe_pos
        p.reset(x, y, hearts=max(1, hearts))
        p.invuln = invuln
        self.world.ensure_until(x + SCREEN_W * 2.0)
        self._snap_camera()
        self.particles.dust(old_x, old_y, self.palette["rock_light"], 10, 1.4)
        self.particles.ring(p.x + p.w / 2, p.y + p.h / 2, self.palette["accent"], 24, 0.6)
        if penalty > 0:
            self.time_left = max(0.0, self.time_left - penalty)
            self.particles.text(p.x + p.w / 2, p.y - 18,
                                label or f"-{int(penalty)}s", UI["danger"], big=True)
            if self.time_left <= 0.0:
                self._end_run("time")
                return False
        return True

    def _update_safe_pos(self, dt: float) -> None:
        p = self.player
        self.safe_timer -= dt
        if self.safe_timer > 0 or not p.on_ground or p.climbing:
            return
        probe = p.rect.inflate(44, 16)
        if self.world.hazards_near(probe):
            return
        if self.world.enemies_near(p.rect.inflate(60, 60)):
            return
        self.safe_pos = (p.x, p.y)
        self.safe_timer = 0.4

    def _update_combo(self, dt: float) -> None:
        if self.combo_count > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_count = 0
                self.combo_timer = 0.0
                self.combo_mult = 1

    def _update_progress(self) -> None:
        p = self.player
        meters = self.world.progress_meters(p.x)
        if meters > self.distance:
            self.distance = meters
        if meters > self.scored_distance:
            gained = (meters - self.scored_distance) * DISTANCE_POINTS
            self.score += gained
            self.scored_distance = meters
        loop = self.world.loop_number(p.x)
        if loop > self.loop_number:
            self.loop_number = loop
            self.score += LOOP_BONUS
            self.flash = max(self.flash, 0.3)
            self.audio.play("loop")
            self.particles.ring(p.x + p.w / 2, p.y + p.h / 2,
                                self.palette["accent"], 30, 0.8)
            self.particles.text(p.x + p.w / 2, p.y - 18, f"+{LOOP_BONUS}",
                                self.palette["accent"], big=True)
            self._set_banner(f"LOOP {loop}", "the wheel turns again · +500", 4.0)

    def _update_biome(self, dt: float) -> None:
        p = self.player
        new_biome = self.world.biome_at(p.x)
        if new_biome != self.biome_index:
            self.blend_from = dict(self.palette)
            self.blend_to = BIOMES[new_biome]
            self.biome_index = new_biome
            self.blend_t = 0.0
            self.backdrop.prepare(new_biome)
            pal = BIOMES[new_biome]
            self._set_banner(pal["name"], pal["tagline"], 3.8)
            self.flash = max(self.flash, 0.2)
        if self.blend_t < 2.2:
            self.blend_t += dt
            t = smoothstep(0.0, 2.2, self.blend_t)
            self.palette = palette_lerp(self.blend_from, self.blend_to, t)
        else:
            self.palette = BIOMES[self.biome_index]

    def _camera_target(self) -> tuple[float, float]:
        p = self.player
        tx = (p.x + p.w / 2 + p.facing * CAMERA_LOOKAHEAD + p.vx * 0.16
              - SCREEN_W * 0.43)
        ty = p.y + p.h / 2 - SCREEN_H * 0.60
        tx = max(0.0, tx)
        ty = clamp(ty, -190.0, 440.0)
        return tx, ty

    def _update_camera(self, dt: float) -> None:
        tx, ty = self._camera_target()
        self.cam.x = exp_smooth(self.cam.x, tx, CAMERA_SMOOTH_X, dt)
        self.cam.y = exp_smooth(self.cam.y, ty, CAMERA_SMOOTH_Y, dt)
        self.cam.y = clamp(self.cam.y, -210.0, 470.0)

    def _snap_camera(self) -> None:
        tx, ty = self._camera_target()
        self.cam.x, self.cam.y = tx, ty

    # ------------------------------------------------------------------
    # endings
    # ------------------------------------------------------------------
    def _end_run(self, reason: str) -> None:
        if self.state != "playing":
            return
        self.end_reason = reason
        self.state = "dying"
        self.death_timer = 1.25
        self.hitstop = 0.0
        self.flash = 0.5 if reason == "death" else 0.25
        self.shake = 22 if reason == "death" else 10
        p = self.player
        if reason == "death":
            self.audio.play("death")
            self.particles.burst(p.x + p.w / 2, p.y + p.h / 2,
                                 self.palette["danger"], 26, 240, 0.9, 500, 5, "spark")
            self.particles.burst(p.x + p.w / 2, p.y + p.h / 2,
                                 self.palette["accent"], 20, 160, 0.9, 200, 4)
            p.hurt_timer = 0.0
        else:
            self.audio.play("loop")
            self.particles.ring(p.x + p.w / 2, p.y + p.h / 2,
                                self.palette["accent"], 34, 0.9)

    def _finalize_run(self) -> None:
        # Time Trial is a pure score attack: the clock running out ends the run,
        # so there is no remaining-time bonus.
        self.time_bonus = 0
        self.final_score = self.score
        best_key = "best_loop" if self.mode == "loop" else "best_trial"
        old_best = int(self.save.get(best_key, 0))
        self.new_best = self.final_score > old_best
        if self.new_best:
            self.save[best_key] = self.final_score
        dist_key = "best_distance_loop" if self.mode == "loop" else "best_distance_trial"
        self.save[dist_key] = max(int(self.save.get(dist_key, 0)), self.distance)
        self.save["total_coins"] = int(self.save.get("total_coins", 0)) + self.coins
        self.save["total_gems"] = int(self.save.get("total_gems", 0)) + self.gems
        self.save["runs"] = int(self.save.get("runs", 0)) + 1
        self.save_progress()
        self.state = "gameover"
        self.menu_index = 0
        if self.new_best:
            self.audio.play("checkpoint")

    def best_for_mode(self) -> int:
        key = "best_loop" if self.mode == "loop" else "best_trial"
        return int(self.save.get(key, 0))

    # ------------------------------------------------------------------
    # drawing
    # ------------------------------------------------------------------
    def _draw_title_scene(self) -> None:
        ws = self.world_surface
        ws.fill((0, 0, 0, 0))
        cam = self.title_cam
        self.backdrop.draw(ws, cam.x, cam.y, 0, self.time)
        self.title_world.time = self.time
        self.title_world.draw_terrain(ws, cam.x, cam.y, self.time)
        self.title_world.draw_pickups(ws, cam.x, cam.y, self.time)
        self.ambient.draw(ws, 0, self.time)
        frame = self.renderer.render(ws, BIOMES[0], self.time, cam.x,
                                     hurt=0.0, flash=0.0, dash=0.0,
                                     bloom_strength=0.95)
        self.screen.blit(frame, (0, 0))

    def _draw_gameplay_scene(self) -> None:
        ws = self.world_surface
        ws.fill((0, 0, 0, 0))
        sx = sy = 0.0
        if self.shake > 0.2:
            sx = random.uniform(-self.shake, self.shake)
            sy = random.uniform(-self.shake, self.shake)
        cx = self.cam.x + sx
        cy = self.cam.y + sy
        self.backdrop.draw(ws, cx, cy, self.biome_index, self.time)
        self.world.draw_terrain(ws, cx, cy, self.time)
        self.world.draw_checkpoints(ws, cx, cy, self.time)
        self.world.draw_pickups(ws, cx, cy, self.time)
        self.world.draw_enemies(ws, cx, cy, self.time)
        self.world.draw_projectiles(ws, cx, cy, self.time)
        if self.player is not None:
            self.player.draw(ws, cx, cy)
            self.player.draw_hint(ws, cx, cy, self.world)
        self.particles.draw(ws, cx, cy, font=self.ui.f_float)
        self.ambient.draw(ws, self.biome_index, self.time)

        hurt = self.player.hurt_timer / 0.3 if self.player else 0.0
        if self.player is not None and self.player.hearts == 1 and self.state == "playing":
            hurt = max(hurt, 0.10)
        dash = 1.0 if (self.player is not None and self.player.dashing) else 0.0
        frame = self.renderer.render(ws, self.palette, self.time, cx,
                                     hurt=hurt, flash=self.flash, dash=dash,
                                     bloom_strength=0.92)
        self.screen.blit(frame, (0, 0))

    def draw(self) -> pygame.Surface:
        if self.state == "title":
            self._draw_title_scene()
            self.ui.draw_title(self.screen, self)
        else:
            self._draw_gameplay_scene()
            if self.state == "playing":
                self.ui.draw_hud(self.screen, self)
            elif self.state == "paused":
                self.ui.draw_pause(self.screen, self)
            elif self.state == "dying":
                self.ui.draw_hud(self.screen, self)
                self.ui.draw_dying(self.screen, self)
            elif self.state == "gameover":
                self.ui.draw_gameover(self.screen, self)
        return self.screen

    # ------------------------------------------------------------------
    def run(self, max_seconds: float | None = None) -> None:
        started = _time.perf_counter()
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.step(dt)
            self.draw()
            pygame.display.flip()
            if max_seconds is not None and (_time.perf_counter() - started) >= max_seconds:
                break
        self.save_progress()
        pygame.quit()
