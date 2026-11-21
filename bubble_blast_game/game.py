"""Archer Bubble Blast - Game Engine, State Machine, Arena & UI"""
import math
import random
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ARENA_LEFT, ARENA_RIGHT, ARENA_TOP, ARENA_FLOOR,
    COLOR_BG, COLOR_ARENA_WALL, COLOR_FLOOR,
    COLOR_TEXT_WHITE, COLOR_TEXT_GOLD, COLOR_TEXT_MUTED,
    PowerUpType
)
from core.archer import Archer
from core.arrow import Arrow
from core.bouncing_bubble import BouncingBubble
from core.powerup import PowerUp
from core.levels import CAMPAIGN_LEVELS, generate_endless_wave
from systems.particles import ParticleSystem
from systems.sound import SoundManager

class BubbleBlastGame:
    def __init__(self):
        self.particles = ParticleSystem()
        self.sound = SoundManager()

        # Cross-Platform Fonts (Safe system fonts)
        pygame.font.init()
        font_names = ["Arial", "Trebuchet MS", "Helvetica", "DejaVu Sans", "sans-serif"]
        self.font_hero = pygame.font.SysFont(font_names, 42, bold=True)
        self.font_title = pygame.font.SysFont(font_names, 28, bold=True)
        self.font_subtitle = pygame.font.SysFont(font_names, 16)
        self.font_main = pygame.font.SysFont(font_names, 18, bold=True)
        self.font_small = pygame.font.SysFont(font_names, 13, bold=True)
        self.font_badge = pygame.font.SysFont(font_names, 11, bold=True)

        # Game State: "MENU", "PLAYING", "VICTORY", "DEFEAT"
        self.state = "MENU"
        self.mode = "CAMPAIGN"  # "CAMPAIGN" or "ENDLESS"

        # Campaign & Wave Progress
        self.current_level_idx = 0
        self.endless_wave = 1
        self.score = 0
        self.high_score = 0

        # Entities
        self.archer = Archer(SCREEN_WIDTH / 2)
        self.arrows: list[Arrow] = []
        self.bubbles: list[BouncingBubble] = []
        self.powerups: list[PowerUp] = []

        # Modifiers
        self.slow_mo_timer = 0.0
        self.screen_shake = 0.0

        # Modal / Dialogs
        self.show_quit_dialog = False
        self.should_exit = False

        # UI Rectangles
        # Main Menu Buttons (Landscape 960 x 640)
        self.btn_menu_campaign = pygame.Rect(SCREEN_WIDTH // 2 - 200, 260, 400, 64)
        self.btn_menu_endless = pygame.Rect(SCREEN_WIDTH // 2 - 200, 345, 400, 64)
        self.btn_menu_quit = pygame.Rect(SCREEN_WIDTH // 2 - 120, 435, 240, 50)

        # In-game Top Navigation Buttons
        self.btn_ingame_menu = pygame.Rect(20, 16, 85, 32)
        self.btn_ingame_restart = pygame.Rect(SCREEN_WIDTH - 105, 16, 85, 32)

    def start_campaign(self, level_idx: int = 0):
        self.mode = "CAMPAIGN"
        self.current_level_idx = level_idx
        self.score = 0
        self.archer = Archer(SCREEN_WIDTH / 2)
        self.arrows.clear()
        self.powerups.clear()
        self.slow_mo_timer = 0.0
        self._load_campaign_level(self.current_level_idx)
        self.state = "PLAYING"

    def start_endless(self):
        self.mode = "ENDLESS"
        self.endless_wave = 1
        self.score = 0
        self.archer = Archer(SCREEN_WIDTH / 2)
        self.arrows.clear()
        self.powerups.clear()
        self.slow_mo_timer = 0.0
        self._load_endless_wave(self.endless_wave)
        self.state = "PLAYING"

    def _load_campaign_level(self, idx: int):
        idx = max(0, min(idx, len(CAMPAIGN_LEVELS) - 1))
        lvl = CAMPAIGN_LEVELS[idx]
        self.bubbles = lvl.spawn()
        self.arrows.clear()
        self.powerups.clear()
        self.archer.x = SCREEN_WIDTH / 2
        self.archer.vx = 0.0
        self.archer.invulnerable_timer = 1.0

    def _load_endless_wave(self, wave: int):
        self.bubbles = generate_endless_wave(wave)
        self.arrows.clear()
        self.powerups.clear()
        self.archer.invulnerable_timer = 1.0

    def fire_arrow(self):
        if self.state != "PLAYING" or not self.archer.alive:
            return

        max_arrows = 2 if self.archer.has_double_arrow else 1
        if len(self.arrows) < max_arrows:
            arrow = Arrow(self.archer.x, start_y=ARENA_FLOOR)
            self.arrows.append(arrow)
            self.sound.play("shoot")

    def handle_keydown(self, key):
        if self.show_quit_dialog:
            if key == pygame.K_y or key == pygame.K_RETURN:
                self.should_exit = True
            elif key == pygame.K_n or key == pygame.K_ESCAPE:
                self.show_quit_dialog = False
            return

        if key in (pygame.K_ESCAPE,):
            self.show_quit_dialog = True
            return

        if self.state == "PLAYING":
            if key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self.fire_arrow()
            elif key == pygame.K_r:
                if self.mode == "CAMPAIGN":
                    self._load_campaign_level(self.current_level_idx)
                else:
                    self.start_endless()
        elif self.state in ("VICTORY", "DEFEAT"):
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.state == "VICTORY":
                    self.next_level_or_menu()
                else:
                    if self.mode == "CAMPAIGN":
                        self.start_campaign(self.current_level_idx)
                    else:
                        self.start_endless()
            elif key == pygame.K_m:
                self.state = "MENU"

    def handle_click(self, pos: tuple[int, int]):
        if self.show_quit_dialog:
            # Quit dialog buttons
            dialog_w, dialog_h = 360, 200
            dx = (SCREEN_WIDTH - dialog_w) // 2
            dy = (SCREEN_HEIGHT - dialog_h) // 2
            btn_confirm = pygame.Rect(dx + 30, dy + 130, 140, 44)
            btn_cancel = pygame.Rect(dx + 190, dy + 130, 140, 44)

            if btn_confirm.collidepoint(pos):
                self.should_exit = True
            elif btn_cancel.collidepoint(pos):
                self.show_quit_dialog = False
            return

        if self.state == "MENU":
            if self.btn_menu_campaign.collidepoint(pos):
                self.start_campaign(0)
            elif self.btn_menu_endless.collidepoint(pos):
                self.start_endless()
            elif self.btn_menu_quit.collidepoint(pos):
                self.show_quit_dialog = True
            return

        if self.state == "PLAYING":
            if self.btn_ingame_menu.collidepoint(pos):
                self.state = "MENU"
                return
            if self.btn_ingame_restart.collidepoint(pos):
                if self.mode == "CAMPAIGN":
                    self._load_campaign_level(self.current_level_idx)
                else:
                    self.start_endless()
                return

        if self.state == "VICTORY":
            btn_next = pygame.Rect(SCREEN_WIDTH // 2 - 160, 370, 320, 50)
            btn_menu = pygame.Rect(SCREEN_WIDTH // 2 - 100, 435, 200, 42)
            if btn_next.collidepoint(pos):
                self.next_level_or_menu()
            elif btn_menu.collidepoint(pos):
                self.state = "MENU"
            return

        if self.state == "DEFEAT":
            btn_retry = pygame.Rect(SCREEN_WIDTH // 2 - 160, 370, 320, 50)
            btn_menu = pygame.Rect(SCREEN_WIDTH // 2 - 100, 435, 200, 42)
            if btn_retry.collidepoint(pos):
                if self.mode == "CAMPAIGN":
                    self.start_campaign(self.current_level_idx)
                else:
                    self.start_endless()
            elif btn_menu.collidepoint(pos):
                self.state = "MENU"
            return

    def next_level_or_menu(self):
        if self.mode == "CAMPAIGN":
            if self.current_level_idx + 1 < len(CAMPAIGN_LEVELS):
                self.current_level_idx += 1
                self._load_campaign_level(self.current_level_idx)
                self.state = "PLAYING"
            else:
                self.state = "MENU"
        else:
            self.endless_wave += 1
            self._load_endless_wave(self.endless_wave)
            self.state = "PLAYING"

    def update(self, dt: float):
        if self.show_quit_dialog:
            return

        if self.screen_shake > 0:
            self.screen_shake = max(0.0, self.screen_shake - dt * 25.0)

        self.particles.update(dt)

        if self.state != "PLAYING":
            return

        # Slow motion modifier
        effective_dt = dt
        if self.slow_mo_timer > 0:
            self.slow_mo_timer -= dt
            effective_dt = dt * 0.52

        # 1. Update Player Movement via Key Polling
        keys = pygame.key.get_pressed()
        moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        if moving_left and not moving_right:
            self.archer.move_left()
        elif moving_right and not moving_left:
            self.archer.move_right()
        else:
            self.archer.stop_moving()

        self.archer.update(dt)

        # 2. Update Harpoon Arrows
        alive_arrows = []
        for arrow in self.arrows:
            if arrow.update(effective_dt):
                alive_arrows.append(arrow)
        self.arrows = alive_arrows

        # 3. Update Bouncing Bubbles
        for b in self.bubbles:
            b.update(effective_dt, sound_mgr=self.sound)

        # 4. Update Powerups
        self.powerups = [p for p in self.powerups if p.update(effective_dt)]

        # 5. Collision: Arrow vs Bouncing Bubble
        new_bubbles = []
        for arrow in list(self.arrows):
            if not arrow.alive:
                continue

            hit_bubble = None
            for b in self.bubbles:
                if b.alive and arrow.collides_with_bubble(b.x, b.y, b.radius):
                    hit_bubble = b
                    break

            if hit_bubble:
                arrow.alive = False
                self.sound.play("pop")
                self.particles.emit_bubble_pop(hit_bubble.x, hit_bubble.y, hit_bubble.color, count=22)
                self.particles.add_floating_text(
                    hit_bubble.x - 16, hit_bubble.y - 10,
                    f"+{hit_bubble.points}", COLOR_TEXT_GOLD, self.font_small
                )
                self.score += hit_bubble.points
                if self.score > self.high_score:
                    self.high_score = self.score

                # Chance to spawn a powerup drop (18%)
                if random.random() < 0.18:
                    ptype = random.choice([
                        PowerUpType.DOUBLE_ARROW,
                        PowerUpType.SHIELD,
                        PowerUpType.SLOW_MO,
                        PowerUpType.DYNAMITE,
                        PowerUpType.EXTRA_LIFE
                    ])
                    self.powerups.append(PowerUp(hit_bubble.x, hit_bubble.y, ptype))

                # Split bubble
                children = hit_bubble.split()
                new_bubbles.extend(children)

        # Filter out popped bubbles and append split children
        self.bubbles = [b for b in self.bubbles if b.alive] + new_bubbles
        self.arrows = [a for a in self.arrows if a.alive]

        # 6. Collision: Bubble vs Archer
        archer_rect = self.archer.rect
        for b in self.bubbles:
            if not b.alive:
                continue
            # Circle vs AABB collision
            closest_x = max(archer_rect.left, min(b.x, archer_rect.right))
            closest_y = max(archer_rect.top, min(b.y, archer_rect.bottom))
            dist_sq = (b.x - closest_x) ** 2 + (b.y - closest_y) ** 2

            if dist_sq < (b.radius ** 2):
                damaged = self.archer.take_hit()
                if damaged:
                    self.sound.play("hurt")
                    self.screen_shake = 12.0
                    self.particles.emit_bubble_pop(self.archer.x, self.archer.y - 26, (255, 60, 60), count=16)

                    if self.archer.lives <= 0:
                        self.archer.alive = False
                        self.state = "DEFEAT"
                        self.sound.play("game_over")
                        return
                elif self.archer.has_shield:
                    # Pop sound for shield absorbing hit
                    self.sound.play("bounce")
                break

        # 7. Collision: Archer vs Powerup
        for p in list(self.powerups):
            if not p.alive:
                continue
            dx = abs(p.x - self.archer.x)
            dy = abs(p.y - (self.archer.y - self.archer.height / 2))
            if dx < (p.radius + self.archer.width / 2) and dy < (p.radius + self.archer.height / 2):
                p.alive = False
                self.sound.play("powerup")
                self._apply_powerup(p.type)
                self.particles.add_floating_text(
                    p.x - 20, p.y - 12, p.label, (100, 255, 180), self.font_small
                )

        self.powerups = [p for p in self.powerups if p.alive]

        # 8. Check Victory Condition
        if len(self.bubbles) == 0:
            self.state = "VICTORY"
            self.sound.play("victory")

    def _apply_powerup(self, ptype: str):
        if ptype == PowerUpType.DOUBLE_ARROW:
            self.archer.double_arrow_timer = 14.0
        elif ptype == PowerUpType.SHIELD:
            self.archer.has_shield = True
        elif ptype == PowerUpType.SLOW_MO:
            self.slow_mo_timer = 6.0
        elif ptype == PowerUpType.EXTRA_LIFE:
            self.archer.lives = min(self.archer.lives + 1, 5)
        elif ptype == PowerUpType.DYNAMITE:
            # TNT splits all bubbles currently on screen!
            new_split = []
            for b in self.bubbles:
                if b.alive:
                    self.particles.emit_bubble_pop(b.x, b.y, b.color, count=14)
                    new_split.extend(b.split())
            self.bubbles = [b for b in self.bubbles if b.alive] + new_split
            self.screen_shake = 10.0

    def draw(self, surface: pygame.Surface):
        # Calculate screen shake offset
        offset_x = random.uniform(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        offset_y = random.uniform(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0

        # Background Fill
        surface.fill(COLOR_BG)

        # Draw Arena Architecture
        self._draw_arena(surface, (offset_x, offset_y))

        # Draw Entities
        for p in self.powerups:
            p.draw(surface, self.font_badge)

        for arrow in self.arrows:
            arrow.draw(surface)

        if self.state in ("PLAYING", "VICTORY", "DEFEAT"):
            self.archer.draw(surface)

        for b in self.bubbles:
            b.draw(surface)

        self.particles.draw(surface)

        # Draw Mode/State Overlays
        if self.state == "PLAYING":
            self._draw_hud(surface)
        elif self.state == "MENU":
            self._draw_main_menu(surface)
        elif self.state == "VICTORY":
            self._draw_hud(surface)
            self._draw_victory_card(surface)
        elif self.state == "DEFEAT":
            self._draw_hud(surface)
            self._draw_defeat_card(surface)

        # Quit Modal Dialog (drawn topmost)
        if self.show_quit_dialog:
            self._draw_quit_dialog(surface)

    def _draw_arena(self, surface: pygame.Surface, offset: tuple[float, float]):
        ox, oy = int(offset[0]), int(offset[1])

        # Floor Barrier
        floor_y = ARENA_FLOOR + oy
        pygame.draw.rect(surface, COLOR_FLOOR, (0, floor_y, SCREEN_WIDTH, SCREEN_HEIGHT - floor_y))
        pygame.draw.line(surface, (50, 68, 105), (0, floor_y), (SCREEN_WIDTH, floor_y), 3)
        pygame.draw.line(surface, (80, 110, 160), (0, floor_y), (SCREEN_WIDTH, floor_y), 1)

        # Left / Right Boundary Walls
        pygame.draw.rect(surface, COLOR_ARENA_WALL, (0, 0, ARENA_LEFT + ox, SCREEN_HEIGHT))
        pygame.draw.rect(surface, COLOR_ARENA_WALL, (ARENA_RIGHT + ox, 0, SCREEN_WIDTH - ARENA_RIGHT, SCREEN_HEIGHT))
        pygame.draw.line(surface, (60, 80, 120), (ARENA_LEFT + ox, 0), (ARENA_LEFT + ox, SCREEN_HEIGHT), 2)
        pygame.draw.line(surface, (60, 80, 120), (ARENA_RIGHT + ox, 0), (ARENA_RIGHT + ox, SCREEN_HEIGHT), 2)

        # Ceiling Line
        pygame.draw.line(surface, (45, 60, 95), (ARENA_LEFT + ox, ARENA_TOP + oy), (ARENA_RIGHT + ox, ARENA_TOP + oy), 2)

    def _draw_hud(self, surface: pygame.Surface):
        # Top Glass HUD Bar
        hud_bar = pygame.Rect(18, 12, SCREEN_WIDTH - 36, 42)
        pygame.draw.rect(surface, (20, 25, 38), hud_bar, border_radius=10)
        pygame.draw.rect(surface, (40, 52, 78), hud_bar, width=1, border_radius=10)

        # In-game buttons (Menu, Restart)
        mouse_pos = pygame.mouse.get_pos()
        for btn, label in [(self.btn_ingame_menu, "MENU"), (self.btn_ingame_restart, "RETRY")]:
            is_hover = btn.collidepoint(mouse_pos)
            bg_col = (45, 58, 85) if is_hover else (30, 38, 56)
            pygame.draw.rect(surface, bg_col, btn, border_radius=8)
            pygame.draw.rect(surface, (70, 90, 130), btn, width=1, border_radius=8)
            txt = self.font_small.render(label, True, COLOR_TEXT_WHITE)
            surface.blit(txt, txt.get_rect(center=btn.center))

        # Lives Counter (Rendered with clean geometric vector hearts)
        lives_x = 125
        lives_y = 24
        lbl_lives = self.font_badge.render("LIVES", True, COLOR_TEXT_MUTED)
        surface.blit(lbl_lives, (lives_x, lives_y + 3))

        for i in range(5):
            hx = lives_x + 46 + i * 22
            hy = lives_y + 8
            filled = (i < self.archer.lives)
            col = (255, 65, 95) if filled else (60, 40, 50)
            self._draw_vector_heart(surface, hx, hy, size=8, color=col)

        # Active Powerup Badges
        badge_x = 310
        if self.archer.has_double_arrow:
            badge_rect = pygame.Rect(badge_x, 18, 70, 28)
            pygame.draw.rect(surface, (45, 40, 20), badge_rect, border_radius=6)
            pygame.draw.rect(surface, (255, 205, 50), badge_rect, width=1, border_radius=6)
            b_txt = self.font_badge.render(f"2X ({int(self.archer.double_arrow_timer)}s)", True, (255, 220, 80))
            surface.blit(b_txt, b_txt.get_rect(center=badge_rect.center))
            badge_x += 78

        if self.archer.has_shield:
            badge_rect = pygame.Rect(badge_x, 18, 64, 28)
            pygame.draw.rect(surface, (20, 42, 55), badge_rect, border_radius=6)
            pygame.draw.rect(surface, (80, 225, 255), badge_rect, width=1, border_radius=6)
            b_txt = self.font_badge.render("SHIELD", True, (120, 240, 255))
            surface.blit(b_txt, b_txt.get_rect(center=badge_rect.center))
            badge_x += 72

        if self.slow_mo_timer > 0:
            badge_rect = pygame.Rect(badge_x, 18, 76, 28)
            pygame.draw.rect(surface, (40, 24, 52), badge_rect, border_radius=6)
            pygame.draw.rect(surface, (180, 100, 255), badge_rect, width=1, border_radius=6)
            b_txt = self.font_badge.render(f"SLOW ({int(self.slow_mo_timer)}s)", True, (210, 160, 255))
            surface.blit(b_txt, b_txt.get_rect(center=badge_rect.center))

        # Level / Wave Badge
        center_x = SCREEN_WIDTH // 2
        if self.mode == "CAMPAIGN":
            lvl_name = CAMPAIGN_LEVELS[self.current_level_idx].name
        else:
            lvl_name = f"ENDLESS WAVE {self.endless_wave}"

        info_txt = self.font_small.render(lvl_name, True, (90, 220, 255))
        surface.blit(info_txt, info_txt.get_rect(center=(center_x + 80, 32)))

        # Score
        score_txt = self.font_main.render(f"SCORE: {self.score:,}", True, COLOR_TEXT_WHITE)
        surface.blit(score_txt, (SCREEN_WIDTH - 280, 22))

    def _draw_vector_heart(self, surface: pygame.Surface, cx: int, cy: int, size: int, color: tuple[int, int, int]):
        """Draws an anti-aliased geometric heart icon (Guaranteed NO tofu box glyphs)."""
        left_circle = (cx - size // 2, cy - size // 3)
        right_circle = (cx + size // 2, cy - size // 3)
        radius = size // 2 + 1
        pygame.draw.circle(surface, color, left_circle, radius)
        pygame.draw.circle(surface, color, right_circle, radius)

        poly_pts = [
            (cx - size, cy - size // 4),
            (cx + size, cy - size // 4),
            (cx, cy + size)
        ]
        pygame.draw.polygon(surface, color, poly_pts)

    def _draw_main_menu(self, surface: pygame.Surface):
        # Soft dark backdrop with glowing aura
        glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (35, 75, 140, 45), (SCREEN_WIDTH // 2, 220), 280)
        surface.blit(glow_surf, (0, 0))

        # Title Hero
        title = self.font_hero.render("BUBBLE BLAST", True, COLOR_TEXT_GOLD)
        t_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 130))
        surface.blit(title, t_rect)

        subtitle = self.font_subtitle.render("CLASSIC ARCHER HARPOON ARCADE", True, (130, 180, 255))
        s_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 172))
        surface.blit(subtitle, s_rect)

        # Instruction Pill
        p_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, 200, 480, 32)
        pygame.draw.rect(surface, (22, 28, 44), p_rect, border_radius=16)
        pygame.draw.rect(surface, (45, 60, 95), p_rect, width=1, border_radius=16)
        tip = self.font_badge.render("AIM UP & POP SPLITTING BUBBLES  |  [A/D] MOVE  |  [SPACE] SHOOT", True, COLOR_TEXT_MUTED)
        surface.blit(tip, tip.get_rect(center=p_rect.center))

        mouse_pos = pygame.mouse.get_pos()

        # Menu Buttons
        buttons = [
            (self.btn_menu_campaign, "CAMPAIGN LEVELS", "Play 8 escalating challenge stages", (40, 120, 220)),
            (self.btn_menu_endless, "ENDLESS SURVIVAL", "Survive infinite waves of bouncing bubbles", (50, 200, 130)),
            (self.btn_menu_quit, "QUIT", "", (180, 60, 80))
        ]

        for rect, label, desc, accent_col in buttons:
            is_hover = rect.collidepoint(mouse_pos)
            bg_col = (34, 44, 68) if is_hover else (22, 28, 44)
            border_col = accent_col if is_hover else (45, 60, 95)

            pygame.draw.rect(surface, bg_col, rect, border_radius=14)
            pygame.draw.rect(surface, border_col, rect, width=2 if is_hover else 1, border_radius=14)

            if desc:
                # Button title
                b_lbl = self.font_title.render(label, True, COLOR_TEXT_WHITE)
                surface.blit(b_lbl, (rect.x + 28, rect.y + 12))
                # Button description
                b_desc = self.font_badge.render(desc, True, COLOR_TEXT_MUTED)
                surface.blit(b_desc, (rect.x + 28, rect.y + 40))
            else:
                b_lbl = self.font_main.render(label, True, COLOR_TEXT_WHITE)
                surface.blit(b_lbl, b_lbl.get_rect(center=rect.center))

    def _draw_victory_card(self, surface: pygame.Surface):
        # Dark Modal Card
        card = pygame.Rect(SCREEN_WIDTH // 2 - 220, 150, 440, 360)
        pygame.draw.rect(surface, (18, 24, 38), card, border_radius=18)
        pygame.draw.rect(surface, (50, 220, 130), card, width=2, border_radius=18)

        t = self.font_title.render("LEVEL CLEARED!", True, (50, 220, 130))
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 205)))

        sub = self.font_subtitle.render(f"Score: {self.score:,}  |  Lives Remaining: {self.archer.lives}", True, COLOR_TEXT_WHITE)
        surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 255)))

        # Next Level Button
        btn_next = pygame.Rect(SCREEN_WIDTH // 2 - 160, 310, 320, 52)
        mouse_pos = pygame.mouse.get_pos()
        hover_next = btn_next.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (30, 160, 90) if hover_next else (22, 120, 70), btn_next, border_radius=12)
        next_lbl = self.font_main.render("NEXT LEVEL [SPACE]", True, COLOR_TEXT_WHITE)
        surface.blit(next_lbl, next_lbl.get_rect(center=btn_next.center))

        # Menu Button
        btn_menu = pygame.Rect(SCREEN_WIDTH // 2 - 110, 380, 220, 42)
        hover_menu = btn_menu.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 58, 85) if hover_menu else (30, 38, 56), btn_menu, border_radius=10)
        menu_lbl = self.font_small.render("MAIN MENU [M]", True, COLOR_TEXT_MUTED)
        surface.blit(menu_lbl, menu_lbl.get_rect(center=btn_menu.center))

    def _draw_defeat_card(self, surface: pygame.Surface):
        # Dark Modal Card
        card = pygame.Rect(SCREEN_WIDTH // 2 - 220, 150, 440, 360)
        pygame.draw.rect(surface, (26, 18, 26), card, border_radius=18)
        pygame.draw.rect(surface, (255, 60, 90), card, width=2, border_radius=18)

        t = self.font_title.render("GAME OVER", True, (255, 70, 95))
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 205)))

        sub = self.font_subtitle.render(f"Final Score: {self.score:,}  |  Best: {self.high_score:,}", True, COLOR_TEXT_WHITE)
        surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 255)))

        # Retry Button
        btn_retry = pygame.Rect(SCREEN_WIDTH // 2 - 160, 310, 320, 52)
        mouse_pos = pygame.mouse.get_pos()
        hover_retry = btn_retry.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (180, 50, 75) if hover_retry else (140, 38, 58), btn_retry, border_radius=12)
        retry_lbl = self.font_main.render("TRY AGAIN [SPACE]", True, COLOR_TEXT_WHITE)
        surface.blit(retry_lbl, retry_lbl.get_rect(center=btn_retry.center))

        # Menu Button
        btn_menu = pygame.Rect(SCREEN_WIDTH // 2 - 110, 380, 220, 42)
        hover_menu = btn_menu.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 58, 85) if hover_menu else (30, 38, 56), btn_menu, border_radius=10)
        menu_lbl = self.font_small.render("MAIN MENU [M]", True, COLOR_TEXT_MUTED)
        surface.blit(menu_lbl, menu_lbl.get_rect(center=btn_menu.center))

    def _draw_quit_dialog(self, surface: pygame.Surface):
        # Scrim Backdrop
        scrim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(scrim, (8, 10, 16, 200), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.blit(scrim, (0, 0))

        # Dialog Box
        dialog_w, dialog_h = 380, 200
        dx = (SCREEN_WIDTH - dialog_w) // 2
        dy = (SCREEN_HEIGHT - dialog_h) // 2
        d_rect = pygame.Rect(dx, dy, dialog_w, dialog_h)

        pygame.draw.rect(surface, (20, 25, 38), d_rect, border_radius=16)
        pygame.draw.rect(surface, (255, 80, 100), d_rect, width=2, border_radius=16)

        # Dialog Text
        t = self.font_title.render("QUIT GAME?", True, COLOR_TEXT_WHITE)
        surface.blit(t, t.get_rect(center=(dx + dialog_w // 2, dy + 45)))

        msg = self.font_small.render("Are you sure you want to exit?", True, COLOR_TEXT_MUTED)
        surface.blit(msg, msg.get_rect(center=(dx + dialog_w // 2, dy + 85)))

        mouse_pos = pygame.mouse.get_pos()
        btn_confirm = pygame.Rect(dx + 35, dy + 125, 145, 46)
        btn_cancel = pygame.Rect(dx + 200, dy + 125, 145, 46)

        # Quit Button
        h_conf = btn_confirm.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (200, 50, 70) if h_conf else (150, 35, 50), btn_confirm, border_radius=10)
        c_lbl = self.font_main.render("QUIT [Y]", True, COLOR_TEXT_WHITE)
        surface.blit(c_lbl, c_lbl.get_rect(center=btn_confirm.center))

        # Cancel Button
        h_canc = btn_cancel.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 60, 90) if h_canc else (30, 42, 65), btn_cancel, border_radius=10)
        can_lbl = self.font_main.render("CANCEL [N]", True, COLOR_TEXT_WHITE)
        surface.blit(can_lbl, can_lbl.get_rect(center=btn_cancel.center))
