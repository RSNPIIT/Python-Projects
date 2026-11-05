"""NOVA STRIKE: ECLIPSE PROTOCOL - core game loop and state machine."""

from __future__ import annotations

import json
import math
import random
import time
from datetime import datetime

import raylib as rl

from .audio import AudioManager
from .config import (
    BLACK,
    CLEAR,
    CYAN,
    FOV,
    GOLD,
    GREEN,
    MAGENTA,
    MAX_FRAME_TIME,
    ORANGE,
    PAPER,
    RED,
    SAVE_PATH,
    SCREENSHOT_DIR,
    TARGET_FPS,
    VIOLET,
    WHITE,
    WINDOW_H,
    WINDOW_W,
    WORLD_H,
    WORLD_W,
    approach,
    clamp,
    ensure_dirs,
    lerp,
    pulse,
)
from .entities import (
    ENEMY_KINDS,
    WEAPONS,
    Enemy,
    FloatingText,
    HudEvent,
    IntelShard,
    Particle,
    Pickup,
    Player,
    Projectile,
    damage_scale_for_mission,
    ray_circle_intersection,
)
from .fonts import FontBook, format_number, format_time
from .levels import LEVELS, MAP_H, MAP_W, WEAPON_UNLOCK_HINTS
from .textures import TextureLibrary
from .ui import UI, with_alpha
from .world import GameMap, Renderer, cast_ray

TITLE = "title"
MISSION_SELECT = "mission_select"
BRIEFING = "briefing"
CONTROLS = "controls"
PLAYING = "playing"
PAUSED = "paused"
LEVEL_COMPLETE = "level_complete"
GAME_OVER = "game_over"
VICTORY = "victory"

DEFAULT_SAVE = {
    "version": 1,
    "highest_unlocked": 0,
    "cleared_missions": [],
    "best_scores": {},
    "career_kills": 0,
    "career_intel": 0,
    "best_combo": 1.0,
    "campaigns_completed": 0,
    "best_campaign_score": 0,
}


class Game:
    def __init__(self) -> None:
        ensure_dirs()
        rl.SetTraceLogLevel(rl.LOG_WARNING)
        rl.SetConfigFlags(rl.FLAG_VSYNC_HINT | rl.FLAG_MSAA_4X_HINT)
        rl.InitWindow(WINDOW_W, WINDOW_H, b"NOVA STRIKE // Eclipse Protocol")
        rl.SetExitKey(0)
        rl.SetTargetFPS(TARGET_FPS)
        rl.EnableCursor()

        self.fonts = FontBook()
        self.textures = TextureLibrary()
        self.ui = UI(self.fonts, self.textures)
        self.audio = AudioManager()
        self.audio.init()
        self.world_target = rl.LoadRenderTexture(WORLD_W, WORLD_H)
        rl.SetTextureFilter(self.world_target.texture, rl.TEXTURE_FILTER_POINT)
        self.renderer = Renderer(self.textures)

        self.running = True
        self.time = 0.0
        self.state = TITLE
        self.state_time = 0.0
        self.fade_alpha = 1.0
        self.screenshot_notice = 0.0

        self.save_data = self._load_save()
        self.current_level_index = 0
        self.level_def = LEVELS[0]
        self.game_map = GameMap(self.level_def)
        self.player: Player | None = None
        self.enemies: list[Enemy] = []
        self.projectiles: list[Projectile] = []
        self.particles: list[Particle] = []
        self.pickups: list[Pickup] = []
        self.intel_shards: list[IntelShard] = []
        self.floating_texts: list[FloatingText] = []
        self.hud_events: list[HudEvent] = []
        self.boss: Enemy | None = None
        self.level_finished = False
        self.portal_active = False
        self.intro_timer = 0.0
        self.level_time = 0.0
        self.total_enemies = 0
        self.kills = 0
        self.intel_collected = 0
        self.intel_total = 0
        self.shots_fired = 0
        self.shots_hit = 0
        self.score_earned = 0
        self.combo = 0
        self.combo_timer = 0.0
        self.best_combo_this_level = 1.0
        self.hit_marker_timer = 0.0
        self.nova_flash = 0.0
        self.player_in_hazard = False
        self.flow_timer = 0.0
        self.ambient_timer = 0.0
        self.ignore_fire = 0.0
        self.ignore_mouse_frames = 0
        self.muzzle_light = 0.0
        self.pending_game_over = False
        self.mission_stats: dict = {}
        self.campaign_totals: dict = {}
        self.rng = random.Random(742)

        mouse_initial = rl.GetMousePosition()
        self.mouse_pos = (float(mouse_initial.x), float(mouse_initial.y))
        self.mouse_moved = False
        self.mouse_clicked = False

        self.title_selection = 0
        self.title_options: list[dict] = []
        self.mission_selection = 0
        self.briefing_level = 0
        self.briefing_return = TITLE
        self.help_return = TITLE
        self.pause_selection = 0
        self.complete_selection = 0
        self.gameover_selection = 0
        self.victory_selection = 0
        self.complete_options: list[dict] = []
        self.gameover_options = [
            {"id": "retry", "label": "RETRY SECTOR", "sub": "REDEPLOY FROM THE LAST CHECKPOINT"},
            {"id": "select", "label": "MISSION SELECT", "sub": "RETURN TO THE AEGIS ARCHIVE"},
            {"id": "title", "label": "ABORT TO TITLE", "sub": "LEAVE THE BATTLEFIELD"},
        ]
        self.victory_options = [
            {"id": "title", "label": "RETURN TO TITLE", "sub": "REST AND REMEMBER"},
            {"id": "select", "label": "MISSION SELECT", "sub": "REPLAY A SECTOR"},
        ]
        self.pause_options = [
            {"id": "resume", "label": "RESUME MISSION", "sub": "BACK TO THE FIGHT"},
            {"id": "restart", "label": "RESTART SECTOR", "sub": "RESET THIS MISSION"},
            {"id": "controls", "label": "FIELD CONTROLS", "sub": "REVIEW COMBAT PROTOCOLS"},
            {"id": "title", "label": "ABORT TO TITLE", "sub": "ABANDON THIS RUN"},
        ]
        self._refresh_title_options()
        self.campaign_totals = self._build_campaign_totals()
        self.audio.start_music(False)
        self.audio.set_music_pitch(0.9)

    # ------------------------------------------------------------------
    # Save data
    # ------------------------------------------------------------------
    def _load_save(self) -> dict:
        data = dict(DEFAULT_SAVE)
        data["best_scores"] = {}
        data["cleared_missions"] = []
        if not SAVE_PATH.exists():
            return data
        try:
            raw = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return data
            data["highest_unlocked"] = int(clamp(int(raw.get("highest_unlocked", 0)), 0, len(LEVELS) - 1))
            cleared = raw.get("cleared_missions", [])
            if isinstance(cleared, list):
                data["cleared_missions"] = sorted(
                    {int(v) for v in cleared if isinstance(v, (int, float)) and 0 <= int(v) < len(LEVELS)}
                )
            best = raw.get("best_scores", {})
            if isinstance(best, dict):
                for key, value in best.items():
                    try:
                        index = int(key)
                    except (TypeError, ValueError):
                        continue
                    if 0 <= index < len(LEVELS):
                        data["best_scores"][str(index)] = max(0, int(value))
            for key in ("career_kills", "career_intel", "campaigns_completed", "best_campaign_score"):
                data[key] = max(0, int(raw.get(key, 0)))
            data["best_combo"] = max(1.0, float(raw.get("best_combo", 1.0)))
        except Exception:
            pass
        return data

    def _save(self) -> None:
        try:
            serializable = dict(self.save_data)
            serializable["best_scores"] = {str(k): int(v) for k, v in self.save_data["best_scores"].items()}
            serializable["cleared_missions"] = sorted(set(self.save_data["cleared_missions"]))
            temp = SAVE_PATH.with_suffix(".tmp")
            temp.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
            temp.replace(SAVE_PATH)
        except Exception:
            pass

    @property
    def highest_unlocked(self) -> int:
        return int(self.save_data.get("highest_unlocked", 0))

    @property
    def cleared_missions(self) -> set[int]:
        return set(self.save_data.get("cleared_missions", []))

    @property
    def cleared_count(self) -> int:
        return len(self.cleared_missions)

    @property
    def best_score(self) -> int:
        scores = self.save_data.get("best_scores", {})
        return max((int(value) for value in scores.values()), default=0)

    def best_score_for(self, index: int) -> int:
        return int(self.save_data.get("best_scores", {}).get(str(index), 0))

    def rank_for(self, index: int) -> str:
        score = self.best_score_for(index)
        if score <= 0:
            return "-"
        return self._rank_for_score(index, score)

    def _rank_for_score(self, index: int, score: int) -> str:
        level = LEVELS[index]
        base = sum(ENEMY_KINDS[enemy.kind].score for enemy in level.enemies)
        base += 7000 if level.boss else 0
        base = max(1, base)
        if score >= base * 1.75:
            return "S"
        if score >= base * 1.30:
            return "A"
        if score >= base * 0.92:
            return "B"
        return "C"

    def _build_campaign_totals(self) -> dict:
        scores = self.save_data.get("best_scores", {})
        return {
            "score": sum(int(value) for value in scores.values()),
            "kills": int(self.save_data.get("career_kills", 0)),
            "intel": int(self.save_data.get("career_intel", 0)),
            "best_combo": float(self.save_data.get("best_combo", 1.0)),
            "new_best": False,
        }

    # ------------------------------------------------------------------
    # State and menus
    # ------------------------------------------------------------------
    def _refresh_title_options(self) -> None:
        options = []
        if self.highest_unlocked > 0:
            target = self.highest_unlocked
            options.append(
                {
                    "id": "continue",
                    "label": f"CONTINUE // SECTOR {target + 1:02d}",
                    "sub": f"RESUME AT {LEVELS[target].name}",
                }
            )
            options.append(
                {
                    "id": "campaign",
                    "label": "NEW CAMPAIGN",
                    "sub": "BEGIN AT SECTOR 01",
                }
            )
        else:
            options.append(
                {
                    "id": "campaign",
                    "label": "START CAMPAIGN",
                    "sub": "BEGIN THE ECLIPSE PROTOCOL",
                }
            )
        options.append(
            {
                "id": "select",
                "label": "MISSION SELECT",
                "sub": f"{self.cleared_count}/{len(LEVELS)} SECTORS CLEARED",
            }
        )
        options.append({"id": "controls", "label": "FIELD CONTROLS", "sub": "COMBAT & MOVEMENT"})
        options.append({"id": "quit", "label": "EXIT TO DESKTOP", "sub": "THE CITY WILL WAIT"})
        self.title_options = options
        self.title_selection = min(self.title_selection, len(options) - 1)

    def _set_state(self, state: str, fade: bool = True) -> None:
        self.state = state
        self.state_time = 0.0
        if fade:
            self.fade_alpha = 1.0
        if state == PLAYING:
            rl.DisableCursor()
        else:
            rl.EnableCursor()

    def _open_briefing(self, index: int, return_state: str) -> None:
        self.briefing_level = int(clamp(index, 0, len(LEVELS) - 1))
        self.briefing_return = return_state
        self._set_state(BRIEFING)
        self.audio.play("ui_click", 0.8)

    def _open_controls(self, return_state: str) -> None:
        self.help_return = return_state
        self._set_state(CONTROLS)
        self.audio.play("ui_click", 0.7)

    def _activate_title(self, option_id: str) -> None:
        self.audio.play("ui_click", 0.8)
        if option_id == "continue":
            self._open_briefing(self.highest_unlocked, TITLE)
        elif option_id == "campaign":
            self._open_briefing(0, TITLE)
        elif option_id == "select":
            self._set_state(MISSION_SELECT)
        elif option_id == "controls":
            self._open_controls(TITLE)
        elif option_id == "quit":
            self.running = False

    def _update_title(self, dt: float) -> None:
        count = len(self.title_options)
        if count <= 0:
            return
        if rl.IsKeyPressed(rl.KEY_UP) or rl.IsKeyPressed(rl.KEY_W):
            self.title_selection = (self.title_selection - 1) % count
            self.audio.play("ui_move", 0.55)
        if rl.IsKeyPressed(rl.KEY_DOWN) or rl.IsKeyPressed(rl.KEY_S):
            self.title_selection = (self.title_selection + 1) % count
            self.audio.play("ui_move", 0.55)
        mouse_x, mouse_y = self.mouse_pos
        for index in range(count):
            x, y, w, h = self.ui.title_option_rect(index, count)
            if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                if self.mouse_moved and self.title_selection != index:
                    self.title_selection = index
                    self.audio.play("ui_move", 0.35)
                if self.mouse_clicked and self.state_time > 0.15:
                    self.title_selection = index
                    self._activate_title(self.title_options[index]["id"])
                break
        if rl.IsKeyPressed(rl.KEY_ENTER) or rl.IsKeyPressed(rl.KEY_SPACE):
            self._activate_title(self.title_options[self.title_selection]["id"])
        if rl.IsKeyPressed(rl.KEY_ESCAPE):
            self.running = False

    def _update_mission_select(self, dt: float) -> None:
        if rl.IsKeyPressed(rl.KEY_LEFT) or rl.IsKeyPressed(rl.KEY_A):
            self.mission_selection = max(0, self.mission_selection - 1)
            self.audio.play("ui_move", 0.45)
        if rl.IsKeyPressed(rl.KEY_RIGHT) or rl.IsKeyPressed(rl.KEY_D):
            self.mission_selection = min(len(LEVELS) - 1, self.mission_selection + 1)
            self.audio.play("ui_move", 0.45)
        if rl.IsKeyPressed(rl.KEY_UP) or rl.IsKeyPressed(rl.KEY_W):
            self.mission_selection = max(0, self.mission_selection - 2)
            self.audio.play("ui_move", 0.45)
        if rl.IsKeyPressed(rl.KEY_DOWN) or rl.IsKeyPressed(rl.KEY_S):
            self.mission_selection = min(len(LEVELS) - 1, self.mission_selection + 2)
            self.audio.play("ui_move", 0.45)
        mouse_x, mouse_y = self.mouse_pos
        for index in range(len(LEVELS)):
            x, y, w, h = self.ui.mission_card_rect(index)
            if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                if self.mouse_moved and self.mission_selection != index:
                    self.mission_selection = index
                    self.audio.play("ui_move", 0.3)
                if self.mouse_clicked and self.state_time > 0.15:
                    self.mission_selection = index
                    self._mission_select_activate(index)
                break
        if rl.IsKeyPressed(rl.KEY_ENTER):
            self._mission_select_activate(self.mission_selection)
        if rl.IsKeyPressed(rl.KEY_ESCAPE):
            self._set_state(TITLE)
            self.audio.play("ui_click", 0.5)

    def _mission_select_activate(self, index: int) -> None:
        if index > self.highest_unlocked:
            self.audio.play("denied", 0.7)
            return
        self._open_briefing(index, MISSION_SELECT)

    def _update_briefing(self, dt: float) -> None:
        if rl.IsKeyPressed(rl.KEY_ESCAPE):
            self._set_state(self.briefing_return)
            self.audio.play("ui_click", 0.5)
            return
        deploy = self.ui.briefing_deploy_rect()
        back = self.ui.briefing_back_rect()
        mouse_x, mouse_y = self.mouse_pos
        if rl.IsKeyPressed(rl.KEY_ENTER) or rl.IsKeyPressed(rl.KEY_SPACE):
            self._start_level(self.briefing_level)
            return
        if self.state_time > 0.15 and self.mouse_clicked:
            if deploy[0] <= mouse_x <= deploy[0] + deploy[2] and deploy[1] <= mouse_y <= deploy[1] + deploy[3]:
                self._start_level(self.briefing_level)
                return
            if back[0] <= mouse_x <= back[0] + back[2] and back[1] <= mouse_y <= back[1] + back[3]:
                self._set_state(self.briefing_return)
                self.audio.play("ui_click", 0.5)
                return

    def _update_controls(self, dt: float) -> None:
        if rl.IsKeyPressed(rl.KEY_ESCAPE) or rl.IsKeyPressed(rl.KEY_ENTER) or rl.IsKeyPressed(rl.KEY_SPACE):
            self._set_state(self.help_return, fade=False)
            self.audio.play("ui_click", 0.5)
            return
        back = self.ui.controls_back_rect()
        mouse_x, mouse_y = self.mouse_pos
        if self.state_time > 0.15 and self.mouse_clicked:
            if back[0] <= mouse_x <= back[0] + back[2] and back[1] <= mouse_y <= back[1] + back[3]:
                self._set_state(self.help_return, fade=False)

    def _update_pause(self, dt: float) -> None:
        count = len(self.pause_options)
        if rl.IsKeyPressed(rl.KEY_ESCAPE):
            self._resume()
            return
        if rl.IsKeyPressed(rl.KEY_UP) or rl.IsKeyPressed(rl.KEY_W):
            self.pause_selection = (self.pause_selection - 1) % count
            self.audio.play("ui_move", 0.5)
        if rl.IsKeyPressed(rl.KEY_DOWN) or rl.IsKeyPressed(rl.KEY_S):
            self.pause_selection = (self.pause_selection + 1) % count
            self.audio.play("ui_move", 0.5)
        mouse_x, mouse_y = self.mouse_pos
        for index in range(count):
            x, y, w, h = self.ui.pause_option_rect(index, count)
            if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                if self.mouse_moved and self.pause_selection != index:
                    self.pause_selection = index
                    self.audio.play("ui_move", 0.3)
                if self.mouse_clicked and self.state_time > 0.15:
                    self.pause_selection = index
                    self._activate_pause(self.pause_options[index]["id"])
                break
        if rl.IsKeyPressed(rl.KEY_ENTER):
            self._activate_pause(self.pause_options[self.pause_selection]["id"])

    def _activate_pause(self, option_id: str) -> None:
        if option_id == "resume":
            self._resume()
        elif option_id == "restart":
            self._start_level(self.current_level_index)
        elif option_id == "controls":
            self._open_controls(PAUSED)
        elif option_id == "title":
            self._return_to_title()

    def _resume(self) -> None:
        self._set_state(PLAYING, fade=False)
        self.ignore_mouse_frames = 4
        self.ignore_fire = 0.2
        self.audio.play("ui_click", 0.5)

    def _update_complete(self, dt: float) -> None:
        count = len(self.complete_options)
        if rl.IsKeyPressed(rl.KEY_UP) or rl.IsKeyPressed(rl.KEY_W):
            self.complete_selection = (self.complete_selection - 1) % count
            self.audio.play("ui_move", 0.5)
        if rl.IsKeyPressed(rl.KEY_DOWN) or rl.IsKeyPressed(rl.KEY_S):
            self.complete_selection = (self.complete_selection + 1) % count
            self.audio.play("ui_move", 0.5)
        mouse_x, mouse_y = self.mouse_pos
        for index in range(count):
            x, y, w, h = self.ui.complete_option_rect(index, count)
            if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                if self.mouse_moved and self.complete_selection != index:
                    self.complete_selection = index
                    self.audio.play("ui_move", 0.3)
                if self.mouse_clicked and self.state_time > 0.2:
                    self.complete_selection = index
                    self._activate_complete(self.complete_options[index]["id"])
                break
        if rl.IsKeyPressed(rl.KEY_ENTER) or rl.IsKeyPressed(rl.KEY_SPACE):
            self._activate_complete(self.complete_options[self.complete_selection]["id"])

    def _activate_complete(self, option_id: str) -> None:
        self.audio.play("ui_click", 0.7)
        if option_id == "next":
            self._open_briefing(min(self.current_level_index + 1, len(LEVELS) - 1), TITLE)
        elif option_id == "replay":
            self._start_level(self.current_level_index)
        elif option_id == "victory":
            self._enter_victory()
        elif option_id == "select":
            self._set_state(MISSION_SELECT)
            self.audio.start_music(False)
            self.audio.set_music_pitch(0.9)

    def _update_game_over(self, dt: float) -> None:
        count = len(self.gameover_options)
        if rl.IsKeyPressed(rl.KEY_UP) or rl.IsKeyPressed(rl.KEY_W):
            self.gameover_selection = (self.gameover_selection - 1) % count
            self.audio.play("ui_move", 0.5)
        if rl.IsKeyPressed(rl.KEY_DOWN) or rl.IsKeyPressed(rl.KEY_S):
            self.gameover_selection = (self.gameover_selection + 1) % count
            self.audio.play("ui_move", 0.5)
        mouse_x, mouse_y = self.mouse_pos
        for index in range(count):
            x, y, w, h = self.ui.gameover_option_rect(index, count)
            if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                if self.mouse_moved and self.gameover_selection != index:
                    self.gameover_selection = index
                    self.audio.play("ui_move", 0.3)
                if self.mouse_clicked and self.state_time > 0.2:
                    self.gameover_selection = index
                    self._activate_game_over(self.gameover_options[index]["id"])
                break
        if rl.IsKeyPressed(rl.KEY_ENTER) or rl.IsKeyPressed(rl.KEY_SPACE):
            self._activate_game_over(self.gameover_options[self.gameover_selection]["id"])

    def _activate_game_over(self, option_id: str) -> None:
        self.audio.play("ui_click", 0.6)
        if option_id == "retry":
            self._start_level(self.current_level_index)
        elif option_id == "select":
            self._set_state(MISSION_SELECT)
            self.audio.start_music(False)
            self.audio.set_music_pitch(0.9)
        elif option_id == "title":
            self._return_to_title()

    def _update_victory(self, dt: float) -> None:
        count = len(self.victory_options)
        if rl.IsKeyPressed(rl.KEY_UP) or rl.IsKeyPressed(rl.KEY_W):
            self.victory_selection = (self.victory_selection - 1) % count
            self.audio.play("ui_move", 0.5)
        if rl.IsKeyPressed(rl.KEY_DOWN) or rl.IsKeyPressed(rl.KEY_S):
            self.victory_selection = (self.victory_selection + 1) % count
            self.audio.play("ui_move", 0.5)
        mouse_x, mouse_y = self.mouse_pos
        for index in range(count):
            x, y, w, h = self.ui.victory_option_rect(index, count)
            if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                if self.mouse_moved and self.victory_selection != index:
                    self.victory_selection = index
                    self.audio.play("ui_move", 0.3)
                if self.mouse_clicked and self.state_time > 0.2:
                    self.victory_selection = index
                    self._activate_victory(self.victory_options[index]["id"])
                break
        if rl.IsKeyPressed(rl.KEY_ENTER) or rl.IsKeyPressed(rl.KEY_SPACE):
            self._activate_victory(self.victory_options[self.victory_selection]["id"])

    def _activate_victory(self, option_id: str) -> None:
        self.audio.play("ui_click", 0.6)
        if option_id == "title":
            self._return_to_title()
        elif option_id == "select":
            self._set_state(MISSION_SELECT)
            self.audio.start_music(False)
            self.audio.set_music_pitch(0.9)

    def _return_to_title(self) -> None:
        self._set_state(TITLE)
        self._refresh_title_options()
        self.audio.start_music(False)
        self.audio.set_music_pitch(0.9)
        self._save()

    # ------------------------------------------------------------------
    # Mission lifecycle
    # ------------------------------------------------------------------
    def _start_level(self, index: int) -> None:
        self.current_level_index = int(clamp(index, 0, len(LEVELS) - 1))
        self.level_def = LEVELS[self.current_level_index]
        self.game_map = GameMap(self.level_def)
        weapon_count = 1
        if self.highest_unlocked >= 1:
            weapon_count += 1
        if self.highest_unlocked >= 2:
            weapon_count += 1
        start_x, start_y = self.level_def.start
        exit_x, exit_y = self.level_def.exit
        self.player = Player(start_x, start_y, weapon_count)
        if self.level_def.boss is not None:
            boss_x, boss_y = self.level_def.boss
            self.player.angle = math.atan2(boss_y - start_y, boss_x - start_x)
        else:
            self.player.angle = math.atan2(exit_y - start_y, exit_x - start_x)
        self.player.energy = min(100, self.player.max_energy)
        self.enemies = []
        self.boss = None
        for spec in self.level_def.enemies:
            enemy = Enemy.from_spec(spec.kind, spec.x + 0.5, spec.y + 0.5, self.current_level_index)
            self.enemies.append(enemy)
        if self.level_def.boss is not None:
            bx, by = self.level_def.boss
            self.boss = Enemy.make_boss(
                bx,
                by,
                self.current_level_index,
                self.level_def.boss_hp,
            )
            self.boss.alerted = True
            self.enemies.append(self.boss)
        self.projectiles = []
        self.particles = []
        self.pickups = []
        for spec in self.level_def.pickups:
            amount = {"health": 32.0, "ammo": 40.0, "nova": 30.0}.get(spec.kind, 0.0)
            self.pickups.append(Pickup(spec.kind, spec.x + 0.5, spec.y + 0.5, phase=self.rng.random() * 6.28, amount=amount))
        self.intel_shards = [
            IntelShard(x, y, phase=self.rng.random() * 6.28) for x, y in self.level_def.intel
        ]
        self.hud_events = []
        self.total_enemies = sum(1 for enemy in self.enemies if not enemy.is_boss)
        self.kills = 0
        self.intel_collected = 0
        self.intel_total = len(self.intel_shards)
        self.shots_fired = 0
        self.shots_hit = 0
        self.score_earned = 0
        self.combo = 0
        self.combo_timer = 0.0
        self.best_combo_this_level = 1.0
        self.hit_marker_timer = 0.0
        self.nova_flash = 0.0
        self.level_time = 0.0
        self.intro_timer = 3.6
        self.portal_active = False
        self.level_finished = False
        self.pending_game_over = False
        self.flow_timer = 0.0
        self.ambient_timer = 0.0
        self.muzzle_light = 0.0
        self.player_in_hazard = False
        self.ignore_fire = 0.35
        self.ignore_mouse_frames = 6
        self.mission_stats = {}
        self.game_map.build_flow_field(self.player.x, self.player.y)
        self._set_state(PLAYING)
        self.audio.start_music(self.level_def.boss is not None)
        self.audio.set_music_pitch(self.level_def.music_pitch if not self.level_def.boss else 1.12)
        self._emit_event(f"MISSION {self.current_level_index + 1:02d} // {self.level_def.name}", self.level_def.theme.accent, 2.8, True)

    def _emit_event(self, text: str, color, life: float = 2.2, big: bool = False) -> None:
        event = HudEvent(text=text, color=color, life=life, max_life=life, big=big)
        self.hud_events.append(event)
        if len(self.hud_events) > 5:
            self.hud_events.pop(0)

    def objective_text(self) -> str:
        if self.boss is not None and not self.boss.dead:
            return "DESTROY OVERLORD VEX"
        if self.portal_active:
            return "REACH EXTRACTION BEACON"
        return "PURGE ALL HOSTILES"

    def objective_short(self) -> str:
        return self.objective_text()

    def hostiles_remaining(self) -> int:
        return sum(1 for enemy in self.enemies if not enemy.dead and not enemy.is_boss)

    def combo_multiplier(self) -> float:
        return min(4.0, 1.0 + max(0, self.combo - 1) * 0.2)

    @property
    def combo_multiplier_value(self) -> float:
        return self.combo_multiplier()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        while not rl.WindowShouldClose() and self.running:
            dt = min(rl.GetFrameTime(), MAX_FRAME_TIME)
            self.update(dt)
            rl.BeginDrawing()
            self.draw()
            self.audio.update()
            rl.EndDrawing()
        self._save()
        self.shutdown()

    def update(self, dt: float) -> None:
        self.time += dt
        self.state_time += dt
        self.fade_alpha = max(0.0, self.fade_alpha - dt * 2.4)
        self.hit_marker_timer = max(0.0, self.hit_marker_timer - dt)
        self.nova_flash = max(0.0, self.nova_flash - dt * 2.2)
        self.ignore_fire = max(0.0, self.ignore_fire - dt)
        self.muzzle_light = max(0.0, self.muzzle_light - dt * 16.0)
        if self.screenshot_notice > 0:
            self.screenshot_notice = max(0.0, self.screenshot_notice - dt)

        pointer = rl.GetMousePosition()
        pointer_x, pointer_y = float(pointer.x), float(pointer.y)
        self.mouse_moved = abs(pointer_x - self.mouse_pos[0]) + abs(pointer_y - self.mouse_pos[1]) > 0.5
        self.mouse_pos = (pointer_x, pointer_y)
        self.mouse_clicked = rl.IsMouseButtonPressed(rl.MOUSE_BUTTON_LEFT)

        # Global shortcuts.
        if rl.IsKeyPressed(rl.KEY_M):
            muted = self.audio.toggle_mute()
            if self.state in (PLAYING, PAUSED):
                self._emit_event("AUDIO MUTED" if muted else "AUDIO ONLINE", ORANGE if muted else CYAN, 1.2)
        if rl.IsKeyPressed(rl.KEY_F12):
            self._take_screenshot()

        if self.state == TITLE:
            self._update_title(dt)
        elif self.state == MISSION_SELECT:
            self._update_mission_select(dt)
        elif self.state == BRIEFING:
            self._update_briefing(dt)
        elif self.state == CONTROLS:
            self._update_controls(dt)
        elif self.state == PLAYING:
            self._update_playing(dt)
        elif self.state == PAUSED:
            self._update_pause(dt)
        elif self.state == LEVEL_COMPLETE:
            self._update_complete(dt)
        elif self.state == GAME_OVER:
            self._update_game_over(dt)
        elif self.state == VICTORY:
            self._update_victory(dt)

    def _take_screenshot(self) -> None:
        try:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = SCREENSHOT_DIR / f"nova_strike_{stamp}.png"
            rl.TakeScreenshot(str(path).encode("utf-8"))
            self.screenshot_notice = 2.0
            if self.state in (PLAYING, PAUSED):
                self._emit_event("SCREENSHOT SAVED", CYAN, 1.4)
            print(f"Screenshot: {path}")
        except Exception as exc:
            print(f"Screenshot failed: {exc}")

    # ------------------------------------------------------------------
    # Gameplay update
    # ------------------------------------------------------------------
    def _update_playing(self, dt: float) -> None:
        if rl.IsKeyPressed(rl.KEY_ESCAPE):
            self._set_state(PAUSED, fade=False)
            self.pause_selection = 0
            return
        if self.player is None:
            return
        player = self.player
        self.level_time += dt
        self.intro_timer = max(0.0, self.intro_timer - dt)
        player.update_timers(dt, self.level_time)

        if self.combo > 0:
            self.combo_timer = max(0.0, self.combo_timer - dt)
            if self.combo_timer <= 0:
                self.combo = 0

        # Events.
        for event in self.hud_events:
            event.life -= dt
            if event.life <= 0:
                event.dead = True
        self.hud_events = [event for event in self.hud_events if not event.dead]

        self._update_look(dt)
        self._update_movement(dt)
        self._update_abilities()
        self._update_weapon(dt)
        self._update_hazard(dt)
        self._update_flow(dt)
        # Give the hero a short grace period while the mission title fades in.
        if self.intro_timer <= 2.6:
            self._update_enemies(dt)
            self._update_projectiles(dt)
        self._update_pickups(dt)
        self._update_particles(dt)
        self._update_ambient(dt)
        self._update_portal(dt)

        if self.pending_game_over:
            self._trigger_game_over()
            return
        if player.health <= 0:
            self._trigger_game_over()

    def _update_look(self, dt: float) -> None:
        player = self.player
        if player is None:
            return
        turn_speed = 2.15
        look_speed = 130.0
        if rl.IsKeyDown(rl.KEY_RIGHT):
            player.angle += turn_speed * dt
        if rl.IsKeyDown(rl.KEY_LEFT):
            player.angle -= turn_speed * dt
        if rl.IsKeyDown(rl.KEY_UP):
            player.look = clamp(player.look + look_speed * dt, -112.0, 112.0)
        if rl.IsKeyDown(rl.KEY_DOWN):
            player.look = clamp(player.look - look_speed * dt, -112.0, 112.0)
        if self.ignore_mouse_frames > 0:
            self.ignore_mouse_frames -= 1
            rl.GetMouseDelta()
        else:
            delta = rl.GetMouseDelta()
            sens = 0.00215 * (0.7 if player.ads else 1.0)
            dx = float(delta.x)
            dy = float(delta.y)
            # Ignore implausible warp deltas from cursor capture/release.
            if abs(dx) < 180.0 and abs(dy) < 180.0:
                player.angle += dx * sens
                player.look = clamp(player.look - dy * 0.82, -112.0, 112.0)
        player.angle %= math.tau

    def _update_movement(self, dt: float) -> None:
        player = self.player
        if player is None:
            return
        player.ads = rl.IsMouseButtonDown(rl.MOUSE_BUTTON_RIGHT) and player.dash_time <= 0
        forward_input = 0.0
        strafe_input = 0.0
        if rl.IsKeyDown(rl.KEY_W):
            forward_input += 1.0
        if rl.IsKeyDown(rl.KEY_S):
            forward_input -= 1.0
        if rl.IsKeyDown(rl.KEY_D):
            strafe_input += 1.0
        if rl.IsKeyDown(rl.KEY_A):
            strafe_input -= 1.0
        length = math.hypot(forward_input, strafe_input)
        if length > 1.0:
            forward_input /= length
            strafe_input /= length
        forward_x = math.cos(player.angle)
        forward_y = math.sin(player.angle)
        right_x = -forward_y
        right_y = forward_x
        move_x = forward_x * forward_input + right_x * strafe_input
        move_y = forward_y * forward_input + right_y * strafe_input
        moving = abs(forward_input) + abs(strafe_input) > 0.01

        # Dash initiation.
        if rl.IsKeyPressed(rl.KEY_LEFT_SHIFT) and player.dash_cooldown <= 0 and player.dash_time <= 0:
            if moving and math.hypot(move_x, move_y) > 0.01:
                norm = math.hypot(move_x, move_y)
                player.dash_dir = (move_x / norm, move_y / norm)
            else:
                player.dash_dir = (forward_x, forward_y)
            player.dash_time = 0.18
            player.dash_cooldown = 2.2
            player.iframe = 0.36
            player.shake = max(player.shake, 0.22)
            self.audio.play("dash", 0.7)
            for index in range(14):
                angle = self.rng.uniform(0, math.tau)
                self.particles.append(
                    Particle(
                        player.x,
                        player.y,
                        self.rng.uniform(0.15, 0.9),
                        math.cos(angle) * self.rng.uniform(0.5, 2.2),
                        math.sin(angle) * self.rng.uniform(0.5, 2.2),
                        self.rng.uniform(0.0, 0.8),
                        0.38,
                        CYAN,
                        self.rng.uniform(0.05, 0.12),
                        gravity=1.0,
                        drag=2.8,
                        glow=True,
                    )
                )

        target_move = 1.0 if moving else 0.0
        player.move_amount = approach(player.move_amount, target_move, 8.0, dt)
        if player.dash_time > 0:
            player.dash_time = max(0.0, player.dash_time - dt)
            speed = 11.5
            dx = player.dash_dir[0] * speed * dt
            dy = player.dash_dir[1] * speed * dt
        else:
            speed = 2.05 if player.ads else 3.35
            dx = move_x * speed * dt
            dy = move_y * speed * dt
            if moving:
                player.bob_time += dt * (9.5 if not player.ads else 6.0)
        new_x, new_y = self.game_map.try_move(player.x, player.y, dx, dy, player.radius)
        blocked = abs((new_x - player.x) - dx) > 0.0001 or abs((new_y - player.y) - dy) > 0.0001
        player.x, player.y = new_x, new_y
        if blocked and player.dash_time > 0:
            player.dash_time = 0.0
            player.shake = max(player.shake, 0.3)
        if moving and player.dash_time <= 0:
            # Footstep-like micro camera motion and dust.
            if math.sin(player.bob_time * 2.0) > 0.985:
                self.particles.append(
                    Particle(
                        player.x - forward_x * 0.2 + self.rng.uniform(-0.16, 0.16),
                        player.y - forward_y * 0.2 + self.rng.uniform(-0.16, 0.16),
                        0.06,
                        self.rng.uniform(-0.2, 0.2),
                        self.rng.uniform(-0.2, 0.2),
                        0.15,
                        0.42,
                        (100, 120, 120, 55),
                        self.rng.uniform(0.02, 0.05),
                        gravity=0.1,
                        drag=2.0,
                    )
                )

    def _update_abilities(self) -> None:
        player = self.player
        if player is None:
            return
        if rl.IsKeyPressed(rl.KEY_E) and player.aegis_cooldown <= 0:
            player.aegis_time = 3.2
            player.aegis_cooldown = 10.0
            player.shield = min(player.max_shield, player.shield + 24.0)
            player.iframe = max(player.iframe, 0.2)
            player.shake = max(player.shake, 0.18)
            self.audio.play("shield", 0.8)
            self._emit_event("AEGIS ONLINE // DAMAGE NEGATED", CYAN, 2.0, True)
            for index in range(24):
                angle = index * math.tau / 24
                self.particles.append(
                    Particle(
                        player.x + math.cos(angle) * 0.5,
                        player.y + math.sin(angle) * 0.5,
                        0.25,
                        math.cos(angle) * 1.2,
                        math.sin(angle) * 1.2,
                        0.6,
                        0.55,
                        CYAN,
                        0.07,
                        gravity=0.2,
                        drag=2.2,
                        glow=True,
                    )
                )
        if rl.IsKeyPressed(rl.KEY_Q) and player.nova >= 100.0:
            self._trigger_nova()

    def _update_hazard(self, dt: float) -> None:
        player = self.player
        if player is None:
            return
        if self.game_map.hazard_at(player.x, player.y):
            self.player_in_hazard = True
            player.hazard_tick -= dt
            if player.hazard_tick <= 0:
                player.hazard_tick = 0.34
                amount = 7.0 * damage_scale_for_mission(self.current_level_index)
                if player.aegis_time > 0:
                    amount *= 0.22
                player.health -= amount
                player.last_damage_time = self.level_time
                player.hit_flash = max(player.hit_flash, 0.2)
                player.shake = max(player.shake, 0.12)
                self.audio.play("hurt", 0.25)
                if player.health <= 0:
                    self.pending_game_over = True
            if self.rng.random() < dt * 18:
                self.particles.append(
                    Particle(
                        player.x + self.rng.uniform(-0.4, 0.4),
                        player.y + self.rng.uniform(-0.4, 0.4),
                        0.05,
                        self.rng.uniform(-0.2, 0.2),
                        self.rng.uniform(-0.2, 0.2),
                        self.rng.uniform(0.5, 1.5),
                        0.5,
                        ORANGE,
                        0.06,
                        gravity=0.8,
                        drag=1.2,
                        glow=True,
                    )
                )
        else:
            self.player_in_hazard = False

    def _update_flow(self, dt: float) -> None:
        self.flow_timer -= dt
        if self.flow_timer <= 0 and self.player is not None:
            self.flow_timer = 0.42
            self.game_map.build_flow_field(self.player.x, self.player.y)

    def _update_weapon(self, dt: float) -> None:
        player = self.player
        if player is None:
            return
        # Weapon switching.
        for index, key in enumerate((rl.KEY_ONE, rl.KEY_TWO, rl.KEY_THREE)):
            if rl.IsKeyPressed(key):
                if index < player.weapon_count:
                    if player.switch_weapon(index):
                        self.audio.play("ui_move", 0.45)
                else:
                    self.audio.play("denied", 0.4)
                    self._emit_event("WEAPON LOCKED // CLEAR MORE SECTORS", ORANGE, 1.4)
        wheel = rl.GetMouseWheelMove()
        if abs(wheel) > 0.1:
            direction = 1 if wheel > 0 else -1
            if player.cycle_weapon(direction):
                self.audio.play("ui_move", 0.45)
        fire_pressed = rl.IsMouseButtonPressed(rl.MOUSE_BUTTON_LEFT)
        fire_down = rl.IsMouseButtonDown(rl.MOUSE_BUTTON_LEFT)
        wants_fire = fire_down if player.weapon.automatic else fire_pressed
        if self.ignore_fire > 0:
            wants_fire = False
        if wants_fire and player.weapon_cooldown <= 0 and player.switch_cooldown <= 0:
            self._fire_weapon()

    def _fire_weapon(self) -> None:
        player = self.player
        if player is None:
            return
        weapon = player.weapon
        if player.energy < weapon.ammo_cost:
            self.audio.play("denied", 0.6)
            self._emit_event("ENERGY DEPLETED // FIND A CELL", ORANGE, 1.8)
            player.weapon_cooldown = 0.35
            return
        player.energy -= weapon.ammo_cost
        player.weapon_cooldown = weapon.cooldown
        player.recoil = min(1.0, player.recoil + weapon.recoil)
        player.muzzle_flash = 1.0
        player.shake = max(player.shake, 0.08 + weapon.recoil * 0.12)
        self.muzzle_light = 1.0
        self.audio.play(weapon.sound, 0.7 if weapon.key != "lance" else 0.8)
        spread_mod = (1.0 + player.move_amount * 0.55) * (1.0 - player.ads_blend * 0.5)
        any_hit = False
        for pellet in range(weapon.pellets):
            angle = player.angle + self.rng.uniform(-weapon.spread, weapon.spread) * spread_mod
            if weapon.pellets == 1 and weapon.pierce == 0:
                angle = player.angle + self.rng.gauss(0.0, weapon.spread * 0.45) * spread_mod
            self.shots_fired += 1
            if self._hitscan(angle, weapon, player):
                any_hit = True
                self.shots_hit += 1
        if any_hit:
            self.hit_marker_timer = 0.13
            player.add_nova(1.8)
        player.weapon_cooldown = weapon.cooldown

    def _hitscan(self, angle: float, weapon, player: Player) -> bool:
        dir_x = math.cos(angle)
        dir_y = math.sin(angle)
        wall_hit = cast_ray(self.game_map.walls, player.x, player.y, angle, weapon.max_range)
        hits: list[tuple[float, Enemy]] = []
        for enemy in self.enemies:
            if enemy.dead:
                continue
            distance = ray_circle_intersection(
                player.x,
                player.y,
                dir_x,
                dir_y,
                enemy.x,
                enemy.y,
                enemy.kind.radius,
            )
            if distance is not None and distance < wall_hit.distance and distance <= weapon.max_range:
                hits.append((distance, enemy))
        hits.sort(key=lambda item: item[0])
        if not hits:
            if wall_hit.distance < weapon.max_range:
                hit_x = player.x + dir_x * wall_hit.distance
                hit_y = player.y + dir_y * wall_hit.distance
                self._spawn_impact(hit_x, hit_y, 0.55, weapon.color, 10)
            return False
        hit_any = False
        max_targets = weapon.pierce + 1
        for index, (distance, enemy) in enumerate(hits[:max_targets]):
            hit_x = player.x + dir_x * distance
            hit_y = player.y + dir_y * distance
            damage = weapon.damage
            if weapon.key == "scatter":
                damage *= 1.0 - 0.32 * clamp(distance / weapon.max_range, 0, 1)
            if weapon.key == "lance" and index > 0:
                damage *= 0.65
            self._spawn_impact(hit_x, hit_y, 0.55, weapon.muzzle_color, 8)
            self._damage_enemy(enemy, damage, angle)
            hit_any = True
            if enemy.dead:
                continue
        if hit_any:
            self.audio.play("hit", 0.32)
        return hit_any

    def _damage_enemy(self, enemy: Enemy, damage: float, angle: float) -> None:
        if enemy.dead:
            return
        player = self.player
        if player is None:
            return
        dealt = enemy.apply_damage(damage, angle)
        if dealt <= 0:
            return
        player.add_nova(1.0)
        player.shake = max(player.shake, 0.05)
        dist = max(0.2, math.hypot(enemy.x - player.x, enemy.y - player.y))
        if not enemy.is_boss:
            enemy.knockback_x += math.cos(angle) * (1.0 / dist) * 0.6
            enemy.knockback_y += math.sin(angle) * (1.0 / dist) * 0.6
        if enemy.hp <= 0:
            self._on_enemy_killed(enemy)

    def _spawn_impact(self, x: float, y: float, z: float, color, count: int) -> None:
        for _ in range(count):
            angle = self.rng.uniform(0, math.tau)
            speed = self.rng.uniform(0.5, 3.2)
            self.particles.append(
                Particle(
                    x,
                    y,
                    z,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    self.rng.uniform(-0.2, 2.0),
                    self.rng.uniform(0.18, 0.55),
                    color,
                    self.rng.uniform(0.035, 0.11),
                    gravity=4.0,
                    drag=1.5,
                    glow=True,
                )
            )

    def _on_enemy_killed(self, enemy: Enemy) -> None:
        if enemy.dead and getattr(enemy, "_counted", False):
            return
        enemy._counted = True
        self.kills += 1
        self.combo += 1
        self.combo_timer = 3.0
        multiplier = self.combo_multiplier()
        self.best_combo_this_level = max(self.best_combo_this_level, multiplier)
        self.save_data["best_combo"] = max(float(self.save_data.get("best_combo", 1.0)), multiplier)
        score = int((enemy.kind.score + (2500 if enemy.is_boss else 0)) * multiplier)
        self.score_earned += score
        self.player.add_nova(9.0 if not enemy.is_boss else 30.0)
        self.hit_marker_timer = max(self.hit_marker_timer, 0.18)
        self.audio.play("kill", 0.65)
        self._spawn_explosion(enemy)
        if self.combo in (3, 5, 8, 12):
            self._emit_event(f"HERO CHAIN x{self.combo_multiplier():.1f}", GOLD, 1.4)
        if enemy.is_boss:
            self._on_boss_killed(enemy)
        else:
            self._roll_drop(enemy)
            self._check_portal_activation()
        if self.player.nova >= 100.0:
            self._emit_event("NOVA BLAST READY // PRESS Q", MAGENTA, 2.0, True)

    def _spawn_explosion(self, enemy: Enemy) -> None:
        color = enemy.kind.accent
        count = 80 if enemy.is_boss else 26
        for _ in range(count):
            angle = self.rng.uniform(0, math.tau)
            speed = self.rng.uniform(0.6, 5.5 if enemy.is_boss else 3.0)
            self.particles.append(
                Particle(
                    enemy.x,
                    enemy.y,
                    self.rng.uniform(0.15, 1.0 if not enemy.is_boss else 1.7),
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    self.rng.uniform(0.3, 3.0 if enemy.is_boss else 1.6),
                    self.rng.uniform(0.4, 1.2),
                    color if self.rng.random() < 0.7 else WHITE,
                    self.rng.uniform(0.05, 0.18),
                    gravity=2.5 if not enemy.is_boss else 1.4,
                    drag=1.0,
                    glow=True,
                )
            )
        self.player.shake = max(self.player.shake, 0.8 if enemy.is_boss else 0.2)
        if enemy.is_boss:
            self.nova_flash = 1.0
            self.audio.play("boss", 0.9)

    def _roll_drop(self, enemy: Enemy) -> None:
        roll = self.rng.random()
        kind = None
        if roll < 0.10:
            kind = "health"
        elif roll < 0.34:
            kind = "ammo"
        elif roll < 0.40:
            kind = "nova"
        if kind:
            amount = {"health": 24.0, "ammo": 30.0, "nova": 24.0}[kind]
            self.pickups.append(
                Pickup(kind, enemy.x + self.rng.uniform(-0.2, 0.2), enemy.y + self.rng.uniform(-0.2, 0.2), phase=self.rng.random() * 6.28, amount=amount)
            )

    def _check_portal_activation(self) -> None:
        if self.portal_active or self.level_finished:
            return
        if self.boss is not None:
            if self.boss.dead:
                self._activate_portal()
            return
        if all(enemy.dead for enemy in self.enemies):
            self._activate_portal()

    def _activate_portal(self) -> None:
        if self.portal_active:
            return
        self.portal_active = True
        self.audio.play("portal", 0.85)
        self._emit_event("EXTRACTION BEACON ONLINE // REACH THE PAD", self.level_def.theme.accent, 3.0, True)
        for index in range(30):
            angle = self.rng.uniform(0, math.tau)
            self.particles.append(
                Particle(
                    self.level_def.exit[0],
                    self.level_def.exit[1],
                    self.rng.uniform(0.05, 1.0),
                    math.cos(angle) * self.rng.uniform(0.2, 1.5),
                    math.sin(angle) * self.rng.uniform(0.2, 1.5),
                    self.rng.uniform(0.5, 2.0),
                    1.2,
                    self.level_def.theme.accent,
                    self.rng.uniform(0.04, 0.1),
                    gravity=0.6,
                    drag=1.2,
                    glow=True,
                )
            )

    def _on_boss_killed(self, boss: Enemy) -> None:
        self._emit_event("OVERLORD VEX DESTROYED // THE TITAN FALLS", GOLD, 4.0, True)
        self.boss = boss
        self.audio.play("kill", 1.0)
        self._activate_portal()
        self.player.add_nova(35.0)

    def _update_enemies(self, dt: float) -> None:
        player = self.player
        if player is None:
            return
        for enemy in list(self.enemies):
            if enemy.dead:
                continue
            was_windup = enemy.windup > 0
            enemy.update_timers(dt, self.level_time)
            if was_windup and enemy.windup <= 0 and not enemy.dead:
                self._enemy_fire(enemy)
            if enemy.spawn_time < 0.3:
                continue
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            distance = math.hypot(dx, dy)
            if distance < 0.001:
                distance = 0.001
            line_of_sight = self.game_map.has_line_of_sight(enemy.x, enemy.y, player.x, player.y)
            if not enemy.alerted:
                if enemy.is_boss or distance < 10.5 or (line_of_sight and distance < 18.0):
                    enemy.alerted = True
                    enemy.alerted_once = True
                else:
                    continue
            if enemy.is_boss:
                self._update_boss(enemy)
            if enemy.dead:
                continue
            # Movement target.
            speed = enemy.kind.speed * (1.0 + self.current_level_index * 0.02)
            move_x = 0.0
            move_y = 0.0
            if enemy.is_boss:
                speed *= 0.75
            if not line_of_sight or distance > enemy.kind.preferred_range + 2.1:
                flow_x, flow_y = self.game_map.flow_direction(enemy.x, enemy.y)
                if abs(flow_x) + abs(flow_y) < 0.01:
                    flow_x = dx / distance
                    flow_y = dy / distance
                move_x += flow_x
                move_y += flow_y
            else:
                # Strafe around the player at the preferred range.
                right_x = -dy / distance
                right_y = dx / distance
                strafe = enemy.strafe
                move_x += right_x * strafe * 0.9
                move_y += right_y * strafe * 0.9
                if distance > enemy.kind.preferred_range + 0.5:
                    move_x += dx / distance * 0.45
                    move_y += dy / distance * 0.45
                elif distance < enemy.kind.preferred_range - 1.1 and not enemy.is_boss:
                    move_x -= dx / distance * 0.55
                    move_y -= dy / distance * 0.55
            # Separation from other enemies.
            for other in self.enemies:
                if other is enemy or other.dead:
                    continue
                ox = enemy.x - other.x
                oy = enemy.y - other.y
                dist_other = math.hypot(ox, oy)
                if 0.001 < dist_other < 1.1:
                    push = (1.1 - dist_other) * 1.2
                    move_x += ox / dist_other * push
                    move_y += oy / dist_other * push
            # Keep a little distance from the player's body.
            if distance < 0.8:
                move_x -= dx / distance * 1.2
                move_y -= dy / distance * 1.2
            move_x += enemy.knockback_x
            move_y += enemy.knockback_y
            enemy.knockback_x *= max(0.0, 1.0 - dt * 5.0)
            enemy.knockback_y *= max(0.0, 1.0 - dt * 5.0)
            length = math.hypot(move_x, move_y)
            if length > 0.001:
                move_x /= length
                move_y /= length
                dx_move = move_x * speed * dt
                dy_move = move_y * speed * dt
                nx, ny = self.game_map.try_move(enemy.x, enemy.y, dx_move, dy_move, enemy.kind.radius)
                if abs(nx - enemy.x) < 1e-5 and abs(ny - enemy.y) < 1e-5:
                    enemy.strafe *= -1.0
                enemy.x, enemy.y = nx, ny
            # Turn to face.
            enemy.hurt_source_angle = math.atan2(dy, dx)
            # Start an attack windup.
            if (
                line_of_sight
                and distance <= enemy.kind.attack_range
                and enemy.attack_timer <= 0
                and enemy.windup <= 0
                and not enemy.dead
            ):
                enemy.windup = enemy.kind.windup
                enemy.windup_total = max(0.001, enemy.kind.windup)
                enemy.attack_timer = enemy.kind.attack_cooldown + enemy.kind.windup
                enemy.aim_glow = 1.0
            # Brutes punish point-blank heroes.
            if (
                enemy.kind_key == "brute"
                and distance < 1.35
                and enemy.attack_timer <= 0
                and enemy.windup <= 0
                and player.iframe <= 0
            ):
                enemy.attack_timer = 1.4
                self._damage_player(14.0 * damage_scale_for_mission(self.current_level_index), enemy.x, enemy.y)
                player.iframe = max(player.iframe, 0.25)
                self.audio.play("hurt", 0.6)

    def _update_boss(self, boss: Enemy) -> None:
        ratio = boss.hp / max(1.0, boss.max_hp)
        if boss.phase == 1 and ratio <= 0.66:
            self._boss_phase_transition(boss, 2)
        elif boss.phase == 2 and ratio <= 0.33:
            self._boss_phase_transition(boss, 3)

    def _boss_phase_transition(self, boss: Enemy, phase: int) -> None:
        boss.phase = phase
        boss.invulnerable = 1.5
        boss.phase_banner = 2.0
        boss.attack_timer = max(boss.attack_timer, 1.2)
        boss.windup = 0.0
        self.audio.play("boss", 0.9)
        self.player.shake = max(self.player.shake, 0.7)
        self.nova_flash = max(self.nova_flash, 0.55)
        if phase == 2:
            self._emit_event("VEX: THE CITY ALREADY BELONGS TO ME.", VIOLET, 3.0, True)
            self._spawn_wave([("drone", 2.5, 5.5), ("drone", 18.5, 5.5), ("brute", 10.5, 15.5)])
        else:
            self._emit_event("VEX: THEN BURN WITH IT!", MAGENTA, 3.0, True)
            self._spawn_wave([("drone", 2.5, 13.5), ("drone", 18.5, 13.5), ("brute", 3.5, 9.5), ("brute", 18.5, 9.5)])
        # Phase shockwave.
        for index in range(36):
            angle = index * math.tau / 36
            self.particles.append(
                Particle(
                    boss.x,
                    boss.y,
                    self.rng.uniform(0.2, 1.6),
                    math.cos(angle) * self.rng.uniform(2.0, 5.0),
                    math.sin(angle) * self.rng.uniform(2.0, 5.0),
                    self.rng.uniform(0.0, 1.4),
                    0.8,
                    VIOLET,
                    self.rng.uniform(0.05, 0.16),
                    gravity=0.8,
                    drag=0.8,
                    glow=True,
                )
            )

    def _spawn_wave(self, specs: list[tuple[str, float, float]]) -> None:
        for kind, x, y in specs:
            if self.game_map.wall_at(int(x), int(y)):
                continue
            enemy = Enemy.from_spec(kind, x, y, self.current_level_index)
            enemy.alerted = True
            enemy.spawn_time = 0.0
            self.enemies.append(enemy)
            for _ in range(18):
                angle = self.rng.uniform(0, math.tau)
                self.particles.append(
                    Particle(
                        x,
                        y,
                        self.rng.uniform(0.1, 1.4),
                        math.cos(angle) * self.rng.uniform(0.5, 2.0),
                        math.sin(angle) * self.rng.uniform(0.5, 2.0),
                        self.rng.uniform(0.5, 2.0),
                        0.7,
                        VIOLET,
                        self.rng.uniform(0.04, 0.1),
                        gravity=0.8,
                        drag=1.0,
                        glow=True,
                    )
                )
        self._emit_event("VEX GUARD DEPLOYED", RED, 1.8)

    def _enemy_fire(self, enemy: Enemy) -> None:
        player = self.player
        if player is None:
            return
        base_angle = math.atan2(player.y - enemy.y, player.x - enemy.x)
        kind = enemy.kind
        count = kind.projectiles
        spread = kind.spread
        color = kind.accent
        damage = kind.damage * damage_scale_for_mission(self.current_level_index)
        if enemy.is_boss:
            enemy.special_timer += 1.0
            if enemy.phase >= 2 and int(enemy.special_timer) % 3 == 0:
                count = 12
                spread = 0.0
                color = VIOLET
                damage *= 0.8
            else:
                count = 5 if enemy.phase >= 2 else 3
                spread = 0.075
                color = MAGENTA
                damage *= 0.8
        angles = []
        if enemy.is_boss and count == 12:
            for index in range(12):
                angles.append(base_angle + index * math.tau / 12)
        else:
            for index in range(count):
                if count == 1:
                    offset = self.rng.uniform(-spread, spread)
                else:
                    offset = (index - (count - 1) * 0.5) * spread * 2.0 + self.rng.uniform(-spread, spread) * 0.3
                angles.append(base_angle + offset)
        spawn_x = enemy.x + math.cos(base_angle) * 0.35
        spawn_y = enemy.y + math.sin(base_angle) * 0.35
        for angle in angles:
            self.projectiles.append(
                Projectile(
                    spawn_x,
                    spawn_y,
                    math.cos(angle) * kind.projectile_speed,
                    math.sin(angle) * kind.projectile_speed,
                    damage,
                    color,
                    radius=0.14 if enemy.is_boss else 0.10,
                    life=4.5,
                    from_boss=enemy.is_boss,
                    size=0.20 if enemy.is_boss else 0.12,
                )
            )
        for _ in range(5):
            angle = self.rng.uniform(0, math.tau)
            self.particles.append(
                Particle(
                    spawn_x,
                    spawn_y,
                    0.55,
                    math.cos(angle) * 0.4,
                    math.sin(angle) * 0.4,
                    self.rng.uniform(0.0, 0.6),
                    0.25,
                    color,
                    0.035,
                    gravity=0.5,
                    drag=2.0,
                    glow=True,
                )
            )
        if enemy.is_boss:
            self.audio.play("boss_shot", 0.4)
        else:
            self.audio.play("enemy_shot", 0.24)

    def _update_projectiles(self, dt: float) -> None:
        player = self.player
        if player is None:
            return
        for projectile in self.projectiles:
            if projectile.dead:
                continue
            hit_player = projectile.update(dt, self.game_map, player)
            if hit_player:
                self._damage_player(projectile.damage, projectile.x, projectile.y)
                self._spawn_impact(projectile.x, projectile.y, 0.55, projectile.color, 8)
            elif projectile.dead:
                # Wall spark.
                self._spawn_impact(projectile.x, projectile.y, 0.5, projectile.color, 4)
        self.projectiles = [projectile for projectile in self.projectiles if not projectile.dead]

    def _damage_player(self, amount: float, source_x: float, source_y: float) -> None:
        player = self.player
        if player is None or player.health <= 0:
            return
        angle = math.atan2(source_y - player.y, source_x - player.x)
        shield_before = player.shield
        dealt = player.take_damage(amount, self.level_time, angle)
        if dealt <= 0:
            return
        self.audio.play("hurt", 0.55)
        self._emit_event(f"-{int(round(amount))} INTEGRITY", RED, 0.7)
        if shield_before > 0 and player.shield <= 0:
            self._emit_event("SHIELD BROKEN", ORANGE, 1.6, True)
        if player.health <= 0:
            self.pending_game_over = True
        self._spawn_impact(player.x, player.y, 0.5, RED, 5)

    def _trigger_nova(self) -> None:
        player = self.player
        if player is None:
            return
        player.nova = 0.0
        self.nova_flash = 1.0
        player.iframe = max(player.iframe, 0.7)
        player.shake = max(player.shake, 0.8)
        self.audio.play("nova", 1.0)
        self._emit_event("NOVA BLAST // CITY-SHAKER", MAGENTA, 2.4, True)
        for enemy in list(self.enemies):
            if enemy.dead:
                continue
            distance = math.hypot(enemy.x - player.x, enemy.y - player.y)
            if distance <= 9.5 and self.game_map.has_line_of_sight(player.x, player.y, enemy.x, enemy.y):
                self._spawn_impact(enemy.x, enemy.y, 0.55, MAGENTA, 16)
                self._damage_enemy(enemy, 160.0 if not enemy.is_boss else 210.0, math.atan2(enemy.y - player.y, enemy.x - player.x))
        for projectile in self.projectiles:
            if math.hypot(projectile.x - player.x, projectile.y - player.y) <= 9.5:
                projectile.dead = True
        self.projectiles = [projectile for projectile in self.projectiles if not projectile.dead]
        for index in range(70):
            angle = self.rng.uniform(0, math.tau)
            speed = self.rng.uniform(2.0, 8.0)
            self.particles.append(
                Particle(
                    player.x,
                    player.y,
                    self.rng.uniform(0.15, 1.7),
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    self.rng.uniform(-0.2, 2.2),
                    self.rng.uniform(0.4, 1.1),
                    MAGENTA if self.rng.random() < 0.6 else WHITE,
                    self.rng.uniform(0.04, 0.14),
                    gravity=1.0,
                    drag=1.0,
                    glow=True,
                )
            )

    def _update_pickups(self, dt: float) -> None:
        player = self.player
        if player is None:
            return
        for pickup in self.pickups:
            if pickup.dead:
                continue
            pickup.phase += dt
            pickup.life -= dt
            if pickup.life <= 0:
                pickup.dead = True
                continue
            if math.hypot(pickup.x - player.x, pickup.y - player.y) <= 0.62:
                if pickup.kind == "health":
                    if player.health >= player.max_health:
                        continue
                    healed = player.heal(pickup.amount)
                    self._emit_event(f"+{int(healed)} HEALTH", GREEN, 1.4)
                elif pickup.kind == "ammo":
                    if player.energy >= player.max_energy:
                        continue
                    gained = player.add_energy(int(pickup.amount))
                    self._emit_event(f"+{int(gained)} ENERGY", ORANGE, 1.4)
                else:
                    if player.nova >= 100.0:
                        continue
                    gained = player.add_nova(pickup.amount)
                    self._emit_event(f"+{int(gained)} NOVA", MAGENTA, 1.4)
                pickup.dead = True
                self.audio.play("pickup", 0.55)
                self.score_earned += 50
                for index in range(14):
                    angle = index * math.tau / 14
                    self.particles.append(
                        Particle(
                            pickup.x,
                            pickup.y,
                            self.rng.uniform(0.2, 0.8),
                            math.cos(angle) * self.rng.uniform(0.3, 1.4),
                            math.sin(angle) * self.rng.uniform(0.3, 1.4),
                            self.rng.uniform(0.3, 1.0),
                            0.55,
                            {"health": GREEN, "ammo": ORANGE, "nova": MAGENTA}.get(pickup.kind, CYAN),
                            0.06,
                            gravity=0.4,
                            drag=2.0,
                            glow=True,
                        )
                    )
        self.pickups = [pickup for pickup in self.pickups if not pickup.dead]
        for shard in self.intel_shards:
            if shard.collected:
                continue
            shard.phase += dt
            if math.hypot(shard.x - player.x, shard.y - player.y) <= 0.65:
                shard.collected = True
                self.intel_collected += 1
                self.audio.play("pickup", 0.8)
                self.score_earned += 650
                self._emit_event(f"INTEL SHARD {self.intel_collected}/{self.intel_total} // DATA SECURED", GOLD, 2.0, True)
                if self.intel_collected == self.intel_total:
                    self._emit_event("SECTOR INTEL COMPLETE // +1500 BONUS", GOLD, 2.4, True)
                for index in range(22):
                    angle = index * math.tau / 22
                    self.particles.append(
                        Particle(
                            shard.x,
                            shard.y,
                            self.rng.uniform(0.2, 1.0),
                            math.cos(angle) * self.rng.uniform(0.4, 1.8),
                            math.sin(angle) * self.rng.uniform(0.4, 1.8),
                            self.rng.uniform(0.3, 1.5),
                            0.8,
                            GOLD,
                            0.07,
                            gravity=0.4,
                            drag=1.8,
                            glow=True,
                        )
                    )

    def _update_particles(self, dt: float) -> None:
        for particle in self.particles:
            if not particle.dead:
                particle.update(dt)
        if len(self.particles) > 420:
            self.particles = [particle for particle in self.particles if not particle.dead][-420:]
        else:
            self.particles = [particle for particle in self.particles if not particle.dead]

    def _update_ambient(self, dt: float) -> None:
        self.ambient_timer -= dt
        if self.ambient_timer > 0 or self.player is None or len(self.particles) > 260:
            return
        self.ambient_timer = 0.09 if self.level_def.theme.ambient_particles == "embers" else 0.16
        player = self.player
        angle = self.rng.uniform(0, math.tau)
        distance = self.rng.uniform(1.2, 8.0)
        x = player.x + math.cos(angle) * distance
        y = player.y + math.sin(angle) * distance
        if self.game_map.wall_at(int(x), int(y)):
            return
        if self.level_def.theme.ambient_particles == "embers":
            color = self.level_def.theme.accent_2 if self.rng.random() < 0.3 else ORANGE
            z = self.rng.uniform(0.05, 0.8)
            vz = self.rng.uniform(0.2, 0.9)
            size = self.rng.uniform(0.025, 0.06)
            life = self.rng.uniform(1.2, 2.8)
        elif self.level_def.theme.ambient_particles == "rain":
            color = (104, 172, 196, 80)
            z = self.rng.uniform(0.3, 1.8)
            vz = -1.6
            size = self.rng.uniform(0.012, 0.03)
            life = 0.9
        else:
            color = (140, 155, 180, 40)
            z = self.rng.uniform(0.1, 1.6)
            vz = self.rng.uniform(-0.05, 0.2)
            size = self.rng.uniform(0.02, 0.05)
            life = self.rng.uniform(1.5, 3.5)
        self.particles.append(
            Particle(
                x,
                y,
                z,
                self.rng.uniform(-0.15, 0.15),
                self.rng.uniform(-0.15, 0.15),
                vz,
                life,
                color,
                size,
                gravity=0.0,
                drag=0.2,
                glow=False,
            )
        )

    def _update_portal(self, dt: float) -> None:
        if not self.portal_active or self.player is None or self.level_finished:
            return
        exit_x, exit_y = self.level_def.exit
        if math.hypot(self.player.x - exit_x, self.player.y - exit_y) < 0.72:
            self._complete_level()

    # ------------------------------------------------------------------
    # Mission completion
    # ------------------------------------------------------------------
    def _complete_level(self) -> None:
        if self.level_finished:
            return
        self.level_finished = True
        accuracy = 100.0 * self.shots_hit / max(1, self.shots_fired)
        accuracy = clamp(accuracy, 0.0, 100.0)
        time_bonus = int(max(0, 2600 - self.level_time * 11.0))
        intel_bonus = self.intel_collected * 750
        if self.intel_collected == self.intel_total:
            intel_bonus += 1500
        completion_bonus = 1200
        accuracy_bonus = int(accuracy * 4.0)
        total_score = int(self.score_earned + time_bonus + intel_bonus + completion_bonus + accuracy_bonus)
        previous_best = self.best_score_for(self.current_level_index)
        new_best = total_score > previous_best
        rank = self._rank_for_score(self.current_level_index, total_score)
        self.mission_stats = {
            "score": total_score,
            "time": self.level_time,
            "accuracy": accuracy,
            "kills": self.kills,
            "intel": self.intel_collected,
            "rank": rank,
            "new_best": new_best,
            "time_bonus": time_bonus,
            "intel_bonus": intel_bonus,
            "completion_bonus": completion_bonus,
            "accuracy_bonus": accuracy_bonus,
        }
        self.save_data["best_scores"][str(self.current_level_index)] = max(previous_best, total_score)
        cleared = set(self.save_data.get("cleared_missions", []))
        cleared.add(self.current_level_index)
        self.save_data["cleared_missions"] = sorted(cleared)
        self.save_data["highest_unlocked"] = min(len(LEVELS) - 1, max(self.highest_unlocked, self.current_level_index + 1))
        self.save_data["career_kills"] = int(self.save_data.get("career_kills", 0)) + self.kills
        self.save_data["career_intel"] = int(self.save_data.get("career_intel", 0)) + self.intel_collected
        self.save_data["best_combo"] = max(float(self.save_data.get("best_combo", 1.0)), self.best_combo_this_level)
        self.campaign_totals = self._build_campaign_totals()
        self._save()
        self.audio.stop_music()
        self.audio.play("complete", 0.85)
        self._emit_event("SECTOR CLEARED", self.level_def.theme.accent, 2.0, True)
        if self.current_level_index >= len(LEVELS) - 1:
            self.complete_options = [
                {"id": "victory", "label": "VIEW EPILOGUE", "sub": "THE ECLIPSE PROTOCOL ENDS"},
                {"id": "replay", "label": "REPLAY FINAL SECTOR", "sub": "FACE VEX AGAIN"},
                {"id": "select", "label": "MISSION SELECT", "sub": "RETURN TO THE AEGIS ARCHIVE"},
            ]
        else:
            self.complete_options = [
                {"id": "next", "label": "NEXT SECTOR", "sub": LEVELS[self.current_level_index + 1].name},
                {"id": "replay", "label": "REPLAY SECTOR", "sub": "CHASE A HIGHER SCORE"},
                {"id": "select", "label": "MISSION SELECT", "sub": "RETURN TO THE AEGIS ARCHIVE"},
            ]
        self.complete_selection = 0
        self._set_state(LEVEL_COMPLETE)
        rl.EnableCursor()

    def _trigger_game_over(self) -> None:
        if self.state == GAME_OVER:
            return
        self.pending_game_over = False
        self.audio.stop_music()
        self.audio.play("game_over", 0.8)
        self.gameover_selection = 0
        self._set_state(GAME_OVER)
        rl.EnableCursor()
        self._save()

    def _enter_victory(self) -> None:
        totals = self._build_campaign_totals()
        new_best = totals["score"] > int(self.save_data.get("best_campaign_score", 0))
        totals["new_best"] = new_best
        self.campaign_totals = totals
        if new_best:
            self.save_data["best_campaign_score"] = int(totals["score"])
        self.save_data["campaigns_completed"] = int(self.save_data.get("campaigns_completed", 0)) + 1
        self._save()
        self.victory_selection = 0
        self._set_state(VICTORY)
        rl.EnableCursor()
        self.audio.start_music(False)
        self.audio.set_music_pitch(1.0)
        self.audio.play("complete", 0.8)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(self) -> None:
        rl.ClearBackground(BLACK)
        if self.state in (PLAYING, PAUSED):
            self._draw_world()
            if self.player is not None:
                if self.level_def.theme.outdoor and self.level_def.theme.ambient_particles == "rain":
                    self.ui._draw_rain(self.time, 13)
                self.ui.draw_weapon(self)
                self.ui.draw_gameplay_overlay(self)
                self.ui.draw_hud(self)
            if self.state == PAUSED:
                self.ui.draw_pause(self)
        elif self.state == TITLE:
            self.ui.draw_title(self)
        elif self.state == MISSION_SELECT:
            self.ui.draw_mission_select(self)
        elif self.state == BRIEFING:
            self.ui.draw_briefing(self)
        elif self.state == CONTROLS:
            self.ui.draw_controls(self)
        elif self.state == LEVEL_COMPLETE:
            self.ui.draw_complete(self)
        elif self.state == GAME_OVER:
            self.ui.draw_game_over(self)
        elif self.state == VICTORY:
            self.ui.draw_victory(self)
        self.ui.draw_screen_effects(self)

    def _draw_world(self) -> None:
        if self.player is None:
            return
        rl.BeginTextureMode(self.world_target)
        rl.ClearBackground(BLACK)
        self.renderer.render(self.player, self.game_map, self.time, self.player.shake)
        self._draw_world_shadows()
        self._draw_world_objects()
        self._draw_world_effects()
        rl.EndTextureMode()
        rl.DrawTexturePro(
            self.world_target.texture,
            (0, 0, WORLD_W, -WORLD_H),
            (0, 0, WINDOW_W, WINDOW_H),
            (0, 0),
            0.0,
            WHITE,
        )

    def _draw_world_shadows(self) -> None:
        if self.player is None:
            return
        for enemy in self.enemies:
            if enemy.dead:
                continue
            self.renderer.draw_shadow(self.player, enemy.x, enemy.y, enemy.kind.radius * 1.2)
        for pickup in self.pickups:
            if not pickup.dead:
                self.renderer.draw_shadow(self.player, pickup.x, pickup.y, 0.12)
        for shard in self.intel_shards:
            if not shard.collected:
                self.renderer.draw_shadow(self.player, shard.x, shard.y, 0.10)

    def _draw_world_objects(self) -> None:
        if self.player is None:
            return
        player = self.player
        drawables: list[tuple[float, str, object]] = []
        for enemy in self.enemies:
            if enemy.dead:
                continue
            projection = self.renderer.project(player, enemy.x, enemy.y, 0.0)
            if projection is None:
                continue
            drawables.append((projection[2], "enemy", enemy))
        for pickup in self.pickups:
            if pickup.dead:
                continue
            projection = self.renderer.project(player, pickup.x, pickup.y, 0.0)
            if projection is None:
                continue
            drawables.append((projection[2], "pickup", pickup))
        for shard in self.intel_shards:
            if shard.collected:
                continue
            projection = self.renderer.project(player, shard.x, shard.y, 0.0)
            if projection is None:
                continue
            drawables.append((projection[2], "intel", shard))
        exit_x, exit_y = self.level_def.exit
        projection = self.renderer.project(player, exit_x, exit_y, 0.0)
        if projection is not None:
            drawables.append((projection[2], "portal", (exit_x, exit_y)))
        drawables.sort(key=lambda item: item[0], reverse=True)
        for depth, kind, obj in drawables:
            if kind == "enemy":
                self._draw_enemy(obj)
            elif kind == "pickup":
                self._draw_pickup(obj)
            elif kind == "intel":
                self._draw_intel(obj)
            elif kind == "portal":
                self.renderer.draw_portal(player, obj[0], obj[1], self.time, self.portal_active, self.level_def.theme.accent)

    def _draw_enemy(self, enemy: Enemy) -> None:
        if self.player is None:
            return
        frames = self.textures.enemy.get(enemy.kind_key)
        if not frames:
            return
        frame = int(enemy.animation * (2.5 if not enemy.is_boss else 2.0)) % len(frames)
        texture = frames[frame]
        bob = 0.0
        if enemy.kind_key == "drone":
            bob = 0.03 + math.sin(enemy.animation * 4.0 + enemy.x) * 0.025
        elif enemy.kind_key in ("trooper", "brute"):
            bob = abs(math.sin(enemy.animation * 7.0)) * 0.018
        if enemy.windup > 0:
            charge = 1.0 - clamp(enemy.windup / max(0.001, enemy.windup_total), 0, 1)
            self.renderer.draw_glow_point(
                self.player,
                enemy.x,
                enemy.y,
                enemy.kind.height * 0.55,
                1.2 + charge * 1.5,
                with_alpha(enemy.kind.accent, int(90 + 90 * charge)),
            )
        alpha_value = 255
        if enemy.spawn_time < 0.3:
            alpha_value = int(255 * clamp(enemy.spawn_time / 0.3, 0, 1))
        tint = WHITE
        if enemy.kind_key == "boss" and enemy.invulnerable > 0:
            tint = (190, 210, 255, 255)
        self.renderer.draw_sprite(
            texture,
            self.player,
            enemy.x,
            enemy.y,
            enemy.kind.height,
            enemy.kind.floor_offset + bob,
            tint,
            alpha_value,
            enemy.hurt_flash,
        )
        if enemy.is_boss and enemy.invulnerable > 0:
            projection = self.renderer.project(self.player, enemy.x, enemy.y, 0.55)
            if projection:
                sx, sy, depth, line_h = projection
                if self.renderer.sprite_visible(sx, depth, 0.1):
                    rl.BeginBlendMode(rl.BLEND_ADDITIVE)
                    rl.DrawCircleGradient((sx, sy), line_h * 0.45, (110, 180, 255, 55), CLEAR)
                    rl.EndBlendMode()

    def _draw_pickup(self, pickup: Pickup) -> None:
        if self.player is None:
            return
        texture = self.textures.pickups.get(pickup.kind)
        if not texture:
            return
        bob = 0.25 + math.sin(self.time * 2.1 + pickup.phase) * 0.06
        alpha_value = 255
        if pickup.life < 5.0:
            alpha_value = int(255 * (0.55 + 0.45 * math.sin(self.time * 10.0)))
        self.renderer.draw_glow_point(
            self.player, pickup.x, pickup.y, 0.3,
            0.7, with_alpha({"health": GREEN, "ammo": ORANGE, "nova": MAGENTA}.get(pickup.kind, CYAN), 60),
        )
        self.renderer.draw_sprite(texture, self.player, pickup.x, pickup.y, 0.30, bob, WHITE, alpha_value)

    def _draw_intel(self, shard: IntelShard) -> None:
        if self.player is None:
            return
        texture = self.textures.pickups.get("intel")
        if not texture:
            return
        bob = 0.34 + math.sin(self.time * 2.6 + shard.phase) * 0.08
        self.renderer.draw_glow_point(self.player, shard.x, shard.y, 0.4, 0.8, (255, 206, 92, 70))
        self.renderer.draw_sprite(texture, self.player, shard.x, shard.y, 0.28, bob, WHITE, 255)

    def _draw_world_effects(self) -> None:
        if self.player is None:
            return
        player = self.player
        for projectile in self.projectiles:
            if projectile.dead:
                continue
            self.renderer.draw_glow_point(
                player,
                projectile.x,
                projectile.y,
                0.55,
                1.0 if not projectile.from_boss else 1.7,
                with_alpha(projectile.color, 90),
            )
            self.renderer.draw_particle(
                player,
                projectile.x,
                projectile.y,
                0.55,
                projectile.size * 1.4,
                with_alpha(projectile.color, 255),
            )
        for particle in self.particles:
            if particle.dead:
                continue
            ratio = clamp(particle.life / 0.8, 0, 1)
            color = with_alpha(particle.color, int(particle.color[3] * ratio))
            if particle.glow:
                self.renderer.draw_glow_point(
                    player, particle.x, particle.y, particle.z, particle.size * 4.9, with_alpha(color, int(color[3] * 0.35))
                )
            self.renderer.draw_particle(player, particle.x, particle.y, particle.z, particle.size, color)
        if player.muzzle_flash > 0:
            self.renderer.draw_muzzle_light(
                player,
                player.x + math.cos(player.angle) * 0.7,
                player.y + math.sin(player.angle) * 0.7,
                player.weapon.muzzle_color,
            )
        if self.boss is not None and self.boss.phase_banner > 0 and not self.boss.dead:
            projection = self.renderer.project(player, self.boss.x, self.boss.y, 1.8)
            if projection:
                sx, sy, depth, line_h = projection
                if self.renderer.sprite_visible(sx, depth):
                    rl.DrawCircleLines(int(sx), int(sy), int(line_h * 0.35), with_alpha(VIOLET, 120))

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------
    def shutdown(self) -> None:
        self._save()
        try:
            self.audio.shutdown()
        except Exception:
            pass
        try:
            self.textures.unload()
        except Exception:
            pass
        try:
            self.fonts.unload()
        except Exception:
            pass
        try:
            rl.UnloadRenderTexture(self.world_target)
        except Exception:
            pass
        try:
            rl.EnableCursor()
            rl.CloseWindow()
        except Exception:
            pass
