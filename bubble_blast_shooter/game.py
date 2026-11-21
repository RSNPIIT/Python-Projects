"""Bubble Blast Shooter - Main Engine, State Machine, Game Loop & UI"""
import math
import random
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_CARD_BG, COLOR_TEXT_WHITE,
    COLOR_TEXT_GOLD, COLOR_TEXT_MUTED, COLOR_DEADLINE,
    DEADLINE_Y, GRID_TOP_MARGIN, BUBBLE_RADIUS,
    BUBBLE_COLORS
)
from core.bubble import Bubble
from core.grid import BubbleGrid
from core.shooter import Shooter
from core.projectile import Projectile
from core.levels import CAMPAIGN_LEVELS, generate_endless_board
from systems.particles import ParticleSystem
from systems.sound import SoundManager

class BubbleBlastGame:
    def __init__(self):
        self.particles = ParticleSystem()
        self.sound = SoundManager()
        self.grid = BubbleGrid()
        self.shooter = Shooter(start_ammo=45)

        # Cross-Platform Safe Fonts
        pygame.font.init()
        font_names = ["Arial", "Trebuchet MS", "Helvetica", "DejaVu Sans", "sans-serif"]
        self.font_hero = pygame.font.SysFont(font_names, 36, bold=True)
        self.font_title = pygame.font.SysFont(font_names, 26, bold=True)
        self.font_subtitle = pygame.font.SysFont(font_names, 15)
        self.font_main = pygame.font.SysFont(font_names, 18, bold=True)
        self.font_small = pygame.font.SysFont(font_names, 13, bold=True)
        self.font_ammo = pygame.font.SysFont(font_names, 22, bold=True)
        self.font_badge = pygame.font.SysFont(font_names, 11, bold=True)

        # States: "MENU", "PLAYING", "VICTORY", "DEFEAT"
        self.state = "MENU"
        self.mode = "CAMPAIGN"  # "CAMPAIGN" or "ENDLESS"

        # Game Progress
        self.current_level_idx = 0
        self.endless_wave = 1
        self.score = 0
        self.high_score = 0
        self.combo = 0
        self.misses_in_endless = 0

        # Projectile currently in flight
        self.active_projectile: Projectile | None = None

        # Modal Dialogs
        self.show_quit_dialog = False
        self.should_exit = False

        # UI Buttons
        # Main Menu Buttons (540 x 860)
        self.btn_menu_campaign = pygame.Rect(70, 360, 400, 68)
        self.btn_menu_endless = pygame.Rect(70, 445, 400, 68)
        self.btn_menu_quit = pygame.Rect(170, 545, 200, 46)

        # In-game Top Bar Buttons
        self.btn_ingame_menu = pygame.Rect(16, 16, 85, 34)
        self.btn_ingame_retry = pygame.Rect(SCREEN_WIDTH - 101, 16, 85, 34)

    def start_campaign(self, level_idx: int = 0):
        self.mode = "CAMPAIGN"
        self.current_level_idx = max(0, min(level_idx, len(CAMPAIGN_LEVELS) - 1))
        self.score = 0
        self.combo = 0
        self.active_projectile = None

        lvl = CAMPAIGN_LEVELS[self.current_level_idx]
        lvl.load_into(self.grid)

        self.shooter = Shooter(start_ammo=lvl.ammo)
        self.shooter.init_colors(self.grid.get_remaining_colors())
        self.state = "PLAYING"

    def start_endless(self):
        self.mode = "ENDLESS"
        self.endless_wave = 1
        self.score = 0
        self.combo = 0
        self.misses_in_endless = 0
        self.active_projectile = None

        generate_endless_board(self.grid, self.endless_wave)
        self.shooter = Shooter(start_ammo=50)
        self.shooter.init_colors(self.grid.get_remaining_colors())
        self.state = "PLAYING"

    def shoot_bubble(self):
        """Launches the loaded bubble from the shooter."""
        if self.state != "PLAYING" or self.active_projectile is not None:
            return

        if self.shooter.ammo <= 0:
            return

        self.active_projectile = Projectile(
            self.shooter.x,
            self.shooter.y - 14.0,
            self.shooter.aim_angle,
            self.shooter.current_color
        )
        self.shooter.ammo -= 1
        self.sound.play("shoot")

        # Reload shooter with available remaining colors
        self.shooter.reload(self.grid.get_remaining_colors())

    def swap_bubble(self):
        """Swaps current bubble with the previewed next bubble."""
        if self.state == "PLAYING" and self.active_projectile is None:
            self.shooter.swap_bubbles()
            self.sound.play("snap")

    def handle_keydown(self, key):
        if self.show_quit_dialog:
            if key in (pygame.K_y, pygame.K_RETURN):
                self.should_exit = True
            elif key in (pygame.K_n, pygame.K_ESCAPE):
                self.show_quit_dialog = False
            return

        if key == pygame.K_ESCAPE:
            if self.state in ("PLAYING", "VICTORY", "DEFEAT"):
                self.state = "MENU"
            else:
                self.show_quit_dialog = True
            return

        if self.state == "PLAYING":
            if key in (pygame.K_c, pygame.K_TAB):
                self.swap_bubble()
            elif key == pygame.K_r:
                if self.mode == "CAMPAIGN":
                    self.start_campaign(self.current_level_idx)
                else:
                    self.start_endless()

        elif self.state in ("VICTORY", "DEFEAT"):
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.state == "VICTORY":
                    self.next_level()
                else:
                    if self.mode == "CAMPAIGN":
                        self.start_campaign(self.current_level_idx)
                    else:
                        self.start_endless()
            elif key == pygame.K_m:
                self.state = "MENU"

    def handle_click(self, pos: tuple[int, int], button: int = 1):
        if self.show_quit_dialog:
            # Quit dialog buttons
            dialog_w, dialog_h = 360, 200
            dx = (SCREEN_WIDTH - dialog_w) // 2
            dy = (SCREEN_HEIGHT - dialog_h) // 2
            btn_confirm = pygame.Rect(dx + 30, dy + 125, 140, 44)
            btn_cancel = pygame.Rect(dx + 190, dy + 125, 140, 44)

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
            if self.btn_ingame_retry.collidepoint(pos):
                if self.mode == "CAMPAIGN":
                    self.start_campaign(self.current_level_idx)
                else:
                    self.start_endless()
                return

            # Right click swaps bubble
            if button == 3:
                self.swap_bubble()
                return

            # Clicking on preview bubble swaps
            dx = pos[0] - self.shooter.preview_x
            dy = pos[1] - self.shooter.preview_y
            if dx * dx + dy * dy < (self.shooter.preview_radius + 10) ** 2:
                self.swap_bubble()
                return

            # Left click fires projectile
            if button == 1:
                self.shoot_bubble()
                return

        if self.state == "VICTORY":
            btn_next = pygame.Rect(SCREEN_WIDTH // 2 - 140, 490, 280, 50)
            btn_menu = pygame.Rect(SCREEN_WIDTH // 2 - 100, 555, 200, 42)
            if btn_next.collidepoint(pos):
                self.next_level()
            elif btn_menu.collidepoint(pos):
                self.state = "MENU"
            return

        if self.state == "DEFEAT":
            btn_retry = pygame.Rect(SCREEN_WIDTH // 2 - 140, 490, 280, 50)
            btn_menu = pygame.Rect(SCREEN_WIDTH // 2 - 100, 555, 200, 42)
            if btn_retry.collidepoint(pos):
                if self.mode == "CAMPAIGN":
                    self.start_campaign(self.current_level_idx)
                else:
                    self.start_endless()
            elif btn_menu.collidepoint(pos):
                self.state = "MENU"
            return

    def next_level(self):
        if self.mode == "CAMPAIGN":
            if self.current_level_idx + 1 < len(CAMPAIGN_LEVELS):
                self.current_level_idx += 1
                self.start_campaign(self.current_level_idx)
            else:
                self.state = "MENU"
        else:
            self.endless_wave += 1
            generate_endless_board(self.grid, self.endless_wave)
            self.shooter.ammo = 50
            self.shooter.init_colors(self.grid.get_remaining_colors())
            self.state = "PLAYING"

    def update(self, dt: float, mouse_pos: tuple[int, int]):
        if self.show_quit_dialog:
            return

        self.particles.update(dt)

        if self.state != "PLAYING":
            return

        # Update Aim
        self.shooter.update_aim(mouse_pos)

        # Update Flying Projectile
        if self.active_projectile:
            p_alive = self.active_projectile.update(dt, sound_mgr=self.sound)

            # Check if projectile reached ceiling or collided with existing bubble
            has_collided = (
                not p_alive or
                self.grid.check_collision_with_bubble(
                    self.active_projectile.x,
                    self.active_projectile.y,
                    BUBBLE_RADIUS * 0.95
                )
            )

            if has_collided:
                self._snap_and_resolve_match(self.active_projectile)
                self.active_projectile = None

    def _snap_and_resolve_match(self, projectile: Projectile):
        # 1. Snap to nearest hexagonal slot
        r, c = self.grid.snap_to_nearest_slot(projectile.x, projectile.y)
        self.grid.set_bubble(r, c, Bubble(projectile.color_id))
        self.sound.play("snap")

        # 2. Check Match-3+
        cluster = self.grid.find_matching_cluster(r, c)
        if len(cluster) >= 3:
            # Successful Match!
            self.combo += 1
            pts = len(cluster) * 30 * min(self.combo, 4)
            self.score += pts
            if self.score > self.high_score:
                self.high_score = self.score

            self.sound.play("pop")

            # Pop all bubbles in cluster
            for pr, pc in cluster:
                b = self.grid.get_bubble(pr, pc)
                if b:
                    cx, cy = self.grid.get_slot_center(pr, pc)
                    color = BUBBLE_COLORS.get(b.color_id, (255, 255, 255))
                    self.particles.emit_burst(cx, cy, color, count=16)
                    self.grid.set_bubble(pr, pc, None)

            # Floating score text
            last_cx, last_cy = self.grid.get_slot_center(r, c)
            self.particles.add_score(
                last_cx - 15, last_cy - 10,
                f"+{pts}", COLOR_TEXT_GOLD, self.font_small
            )

            # 3. Check for Detached / Floating Orphan Bubbles (Avalanche)
            orphans = self.grid.find_floating_bubbles()
            if orphans:
                self.sound.play("avalanche")
                orphan_pts = len(orphans) * 100
                self.score += orphan_pts
                if self.score > self.high_score:
                    self.high_score = self.score

                for or_r, or_c, or_bubble in orphans:
                    cx, cy = self.grid.get_slot_center(or_r, or_c)
                    self.particles.add_falling_bubble(cx, cy, or_bubble.color_id)

                self.particles.add_score(
                    last_cx - 40, last_cy + 15,
                    f"AVALANCHE! +{orphan_pts}", (100, 255, 180), self.font_main
                )

        else:
            # Missed match
            self.combo = 0
            if self.mode == "ENDLESS":
                self.misses_in_endless += 1

        # 4. Check Win / Loss Conditions
        if self.grid.is_empty():
            self.state = "VICTORY"
            self.sound.play("victory")
            return

        if self.grid.reached_deadline():
            self.state = "DEFEAT"
            self.sound.play("game_over")
            return

        if self.shooter.ammo <= 0:
            self.state = "DEFEAT"
            self.sound.play("game_over")
            return

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        surface.fill(COLOR_BG)

        # 1. Subtle Background Bokeh / Star Orbs
        self._draw_ambient_background(surface)

        # 2. Draw Hexagonal Honeycomb Grid & Bubbles
        self.grid.draw(surface)

        # 3. Draw Danger Deadline Line
        self._draw_danger_line(surface)

        # 4. Draw Particles (Droplets, Falling Avalanche Bubbles, Scores)
        self.particles.draw(surface)

        # 5. Draw Flying Projectile
        if self.active_projectile:
            self.active_projectile.draw(surface)

        # 6. Draw Shooter & Laser Aim (when playing)
        if self.state == "PLAYING":
            self.shooter.draw(surface, self.font_ammo, self.grid)
            self._draw_hud(surface, mouse_pos)
        elif self.state == "MENU":
            self._draw_main_menu(surface, mouse_pos)
        elif self.state == "VICTORY":
            self._draw_hud(surface, mouse_pos)
            self._draw_victory_card(surface, mouse_pos)
        elif self.state == "DEFEAT":
            self._draw_hud(surface, mouse_pos)
            self._draw_defeat_card(surface, mouse_pos)

        # Quit Dialog Overlay (topmost)
        if self.show_quit_dialog:
            self._draw_quit_dialog(surface, mouse_pos)

    def _draw_ambient_background(self, surface: pygame.Surface):
        # Soft dark gradient orbs for that luminous mobile arcade atmosphere
        orbs = [
            (SCREEN_WIDTH // 2, 220, 240, (30, 45, 90, 40)),
            (100, 600, 180, (40, 25, 75, 30)),
            (440, 700, 200, (20, 50, 95, 35))
        ]
        for ox, oy, rad, col in orbs:
            orb_surf = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
            pygame.draw.circle(orb_surf, col, (rad, rad), rad)
            surface.blit(orb_surf, (ox - rad, oy - rad))

    def _draw_danger_line(self, surface: pygame.Surface):
        # Soft red warning glow band
        glow_surf = pygame.Surface((SCREEN_WIDTH, 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 50, 80, 35), (0, 0, SCREEN_WIDTH, 20))
        surface.blit(glow_surf, (0, DEADLINE_Y - 10))

        # Laser deadline
        pygame.draw.line(surface, (255, 60, 90), (0, DEADLINE_Y), (SCREEN_WIDTH, DEADLINE_Y), 2)
        pygame.draw.line(surface, (255, 200, 220), (0, DEADLINE_Y), (SCREEN_WIDTH, DEADLINE_Y), 1)

        # Centered Sleek Danger Badge with Vector Caution Triangles
        badge_w = 140
        badge_h = 20
        badge_x = (SCREEN_WIDTH - badge_w) // 2
        badge_y = DEADLINE_Y + 4

        pygame.draw.rect(surface, (28, 18, 26), (badge_x, badge_y, badge_w, badge_h), border_radius=10)
        pygame.draw.rect(surface, (255, 60, 90), (badge_x, badge_y, badge_w, badge_h), width=1, border_radius=10)

        # Left & Right Vector Warning Triangles (Guaranteed NO tofu glyphs)
        lt_pts = [(badge_x + 12, badge_y + 5), (badge_x + 8, badge_y + 15), (badge_x + 16, badge_y + 15)]
        pygame.draw.polygon(surface, (255, 75, 100), lt_pts)

        rt_pts = [(badge_x + badge_w - 12, badge_y + 5), (badge_x + badge_w - 16, badge_y + 15), (badge_x + badge_w - 8, badge_y + 15)]
        pygame.draw.polygon(surface, (255, 75, 100), rt_pts)

        lbl = self.font_badge.render("DANGER LINE", True, (255, 170, 190))
        surface.blit(lbl, (badge_x + (badge_w - lbl.get_width()) // 2, badge_y + 3))

    def _draw_hud(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        # Dark Glass Header
        header = pygame.Rect(12, 10, SCREEN_WIDTH - 24, 46)
        pygame.draw.rect(surface, (20, 26, 44), header, border_radius=12)
        pygame.draw.rect(surface, (38, 50, 78), header, width=1, border_radius=12)

        # Menu Button
        h_menu = self.btn_ingame_menu.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 60, 90) if h_menu else (30, 40, 62), self.btn_ingame_menu, border_radius=8)
        pygame.draw.rect(surface, (70, 90, 130), self.btn_ingame_menu, width=1, border_radius=8)
        m_txt = self.font_small.render("MENU", True, COLOR_TEXT_WHITE)
        surface.blit(m_txt, m_txt.get_rect(center=self.btn_ingame_menu.center))

        # Retry Button
        h_retry = self.btn_ingame_retry.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 60, 90) if h_retry else (30, 40, 62), self.btn_ingame_retry, border_radius=8)
        pygame.draw.rect(surface, (70, 90, 130), self.btn_ingame_retry, width=1, border_radius=8)
        r_txt = self.font_small.render("RETRY", True, COLOR_TEXT_WHITE)
        surface.blit(r_txt, r_txt.get_rect(center=self.btn_ingame_retry.center))

        # Center Level / Wave Badge
        if self.mode == "CAMPAIGN":
            lvl_name = f"STAGE {self.current_level_idx + 1}"
        else:
            lvl_name = f"ENDLESS WAVE {self.endless_wave}"

        info_txt = self.font_main.render(lvl_name, True, (80, 220, 255))
        surface.blit(info_txt, info_txt.get_rect(center=(SCREEN_WIDTH // 2, 24)))

        score_txt = self.font_small.render(f"SCORE: {self.score:,}", True, COLOR_TEXT_WHITE)
        surface.blit(score_txt, score_txt.get_rect(center=(SCREEN_WIDTH // 2, 44)))

    def _draw_main_menu(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        # Header & Hero Title
        title = self.font_hero.render("BUBBLE BLAST", True, COLOR_TEXT_GOLD)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 170)))

        subtitle = self.font_subtitle.render("CLASSIC HEXAGONAL BUBBLE SHOOTER", True, (130, 180, 255))
        surface.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 215)))

        # Decorative Mini Honeycomb Cluster in Menu
        mini_colors = [0, 1, 2, 3, 4, 5]
        for idx, col_id in enumerate(mini_colors):
            angle = idx * (math.pi / 3)
            mx = SCREEN_WIDTH // 2 + int(math.cos(angle) * 38)
            my = 285 + int(math.sin(angle) * 38)
            from core.bubble import get_bubble_surface
            b_surf = get_bubble_surface(col_id, radius=16)
            surface.blit(b_surf, b_surf.get_rect(center=(mx, my)))

        # Center Bubble
        b_center = get_bubble_surface(4, radius=18)
        surface.blit(b_center, b_center.get_rect(center=(SCREEN_WIDTH // 2, 285)))

        # Menu Buttons
        buttons = [
            (self.btn_menu_campaign, "CAMPAIGN STAGES", "Clear 5 handcrafted color patterns", (50, 140, 255)),
            (self.btn_menu_endless, "ENDLESS SURVIVAL", "Survive escalating waves of bubbles", (50, 215, 120)),
            (self.btn_menu_quit, "QUIT", "", (200, 60, 80))
        ]

        for rect, label, desc, accent in buttons:
            is_hover = rect.collidepoint(mouse_pos)
            bg_col = (32, 42, 68) if is_hover else (22, 28, 46)
            border_col = accent if is_hover else (45, 60, 95)

            pygame.draw.rect(surface, bg_col, rect, border_radius=14)
            pygame.draw.rect(surface, border_col, rect, width=2 if is_hover else 1, border_radius=14)

            if desc:
                b_lbl = self.font_title.render(label, True, COLOR_TEXT_WHITE)
                surface.blit(b_lbl, (rect.x + 24, rect.y + 12))
                b_desc = self.font_badge.render(desc, True, COLOR_TEXT_MUTED)
                surface.blit(b_desc, (rect.x + 24, rect.y + 42))
            else:
                b_lbl = self.font_main.render(label, True, COLOR_TEXT_WHITE)
                surface.blit(b_lbl, b_lbl.get_rect(center=rect.center))

    def _draw_victory_card(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        card = pygame.Rect(SCREEN_WIDTH // 2 - 190, 240, 380, 390)
        pygame.draw.rect(surface, (18, 26, 42), card, border_radius=18)
        pygame.draw.rect(surface, (50, 220, 130), card, width=2, border_radius=18)

        t = self.font_title.render("STAGE CLEARED!", True, (50, 220, 130))
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 305)))

        sub = self.font_subtitle.render(f"Score: {self.score:,}  |  Shots Left: {self.shooter.ammo}", True, COLOR_TEXT_WHITE)
        surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 360)))

        # Next Level Button
        btn_next = pygame.Rect(SCREEN_WIDTH // 2 - 140, 430, 280, 52)
        hover_next = btn_next.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (30, 160, 90) if hover_next else (22, 120, 70), btn_next, border_radius=12)
        next_lbl = self.font_main.render("NEXT STAGE [SPACE]", True, COLOR_TEXT_WHITE)
        surface.blit(next_lbl, next_lbl.get_rect(center=btn_next.center))

        # Menu Button
        btn_menu = pygame.Rect(SCREEN_WIDTH // 2 - 100, 505, 200, 42)
        hover_menu = btn_menu.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 58, 85) if hover_menu else (30, 38, 56), btn_menu, border_radius=10)
        menu_lbl = self.font_small.render("MAIN MENU [M]", True, COLOR_TEXT_MUTED)
        surface.blit(menu_lbl, menu_lbl.get_rect(center=btn_menu.center))

    def _draw_defeat_card(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        card = pygame.Rect(SCREEN_WIDTH // 2 - 190, 240, 380, 390)
        pygame.draw.rect(surface, (26, 18, 26), card, border_radius=18)
        pygame.draw.rect(surface, (255, 60, 90), card, width=2, border_radius=18)

        t = self.font_title.render("GAME OVER", True, (255, 70, 95))
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 305)))

        msg = "Out of Ammo!" if self.shooter.ammo <= 0 else "Deadline Breached!"
        sub = self.font_subtitle.render(f"{msg}  |  Final: {self.score:,}", True, COLOR_TEXT_WHITE)
        surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 360)))

        # Retry Button
        btn_retry = pygame.Rect(SCREEN_WIDTH // 2 - 140, 430, 280, 52)
        hover_retry = btn_retry.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (180, 50, 75) if hover_retry else (140, 38, 58), btn_retry, border_radius=12)
        retry_lbl = self.font_main.render("TRY AGAIN [SPACE]", True, COLOR_TEXT_WHITE)
        surface.blit(retry_lbl, retry_lbl.get_rect(center=btn_retry.center))

        # Menu Button
        btn_menu = pygame.Rect(SCREEN_WIDTH // 2 - 100, 505, 200, 42)
        hover_menu = btn_menu.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 58, 85) if hover_menu else (30, 38, 56), btn_menu, border_radius=10)
        menu_lbl = self.font_small.render("MAIN MENU [M]", True, COLOR_TEXT_MUTED)
        surface.blit(menu_lbl, menu_lbl.get_rect(center=btn_menu.center))

    def _draw_quit_dialog(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        scrim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(scrim, (8, 10, 16, 205), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.blit(scrim, (0, 0))

        dialog_w, dialog_h = 360, 200
        dx = (SCREEN_WIDTH - dialog_w) // 2
        dy = (SCREEN_HEIGHT - dialog_h) // 2
        d_rect = pygame.Rect(dx, dy, dialog_w, dialog_h)

        pygame.draw.rect(surface, (20, 25, 40), d_rect, border_radius=16)
        pygame.draw.rect(surface, (255, 80, 100), d_rect, width=2, border_radius=16)

        t = self.font_title.render("QUIT GAME?", True, COLOR_TEXT_WHITE)
        surface.blit(t, t.get_rect(center=(dx + dialog_w // 2, dy + 45)))

        msg = self.font_small.render("Are you sure you want to exit?", True, COLOR_TEXT_MUTED)
        surface.blit(msg, msg.get_rect(center=(dx + dialog_w // 2, dy + 85)))

        btn_confirm = pygame.Rect(dx + 30, dy + 125, 140, 44)
        btn_cancel = pygame.Rect(dx + 190, dy + 125, 140, 44)

        h_conf = btn_confirm.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (200, 50, 70) if h_conf else (150, 35, 50), btn_confirm, border_radius=10)
        c_lbl = self.font_main.render("QUIT [Y]", True, COLOR_TEXT_WHITE)
        surface.blit(c_lbl, c_lbl.get_rect(center=btn_confirm.center))

        h_canc = btn_cancel.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 60, 90) if h_canc else (30, 42, 65), btn_cancel, border_radius=10)
        can_lbl = self.font_main.render("CANCEL [N]", True, COLOR_TEXT_WHITE)
        surface.blit(can_lbl, can_lbl.get_rect(center=btn_cancel.center))
