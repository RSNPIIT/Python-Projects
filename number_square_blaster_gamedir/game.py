"""Block Blast - Polished Game Engine and High-End Arcade UI"""
import math
import random
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    GRID_COLS, BLOCK_PADDING, BOARD_TOP_MARGIN,
    DEADLINE_Y, BLOCK_WIDTH, BLOCK_HEIGHT,
    COLOR_BG, COLOR_DEADLINE, COLOR_TEXT_WHITE, COLOR_TEXT_GOLD, COLOR_TEXT_MUTED,
    PowerUpType
)
from core.block import Block
from core.cannon import Cannon
from core.rocket import Rocket
from core.powerup import PowerUp
from systems.particles import ParticleSystem
from systems.sound import SoundManager
from systems.screen_shake import ScreenShake

class BlockBlastGame:
    def __init__(self):
        self.particles = ParticleSystem()
        self.sound = SoundManager()
        self.screen_shake = ScreenShake()
        self.cannon = Cannon()

        # Reliable Cross-Platform Fonts
        pygame.font.init()
        font_names = ["Arial", "Trebuchet MS", "Helvetica", "DejaVu Sans", "sans-serif"]
        self.font_title = pygame.font.SysFont(font_names, 34, bold=True)
        self.font_score = pygame.font.SysFont(font_names, 22, bold=True)
        self.font_block = pygame.font.SysFont(font_names, 17, bold=True)
        self.font_small = pygame.font.SysFont(font_names, 12, bold=True)
        self.font_popup = pygame.font.SysFont(font_names, 15, bold=True)
        self.font_badge = pygame.font.SysFont(font_names, 11, bold=True)

        self.score = 0
        self.high_score = 0
        self.wave = 1
        self.game_over = False
        self.is_firing = False
        self.show_quit_dialog = False

        # Quit dialog buttons
        card_w, card_h = 390, 220
        card_x = (SCREEN_WIDTH - card_w) // 2
        card_y = (SCREEN_HEIGHT - card_h) // 2
        btn_w, btn_h = 150, 44
        btn_y = card_y + card_h - 66
        self.btn_quit_rect = pygame.Rect(card_x + 28, btn_y, btn_w, btn_h)
        self.btn_cancel_rect = pygame.Rect(card_x + card_w - btn_w - 28, btn_y, btn_w, btn_h)
        
        self.wave_interval = 7.5
        self.wave_timer = self.wave_interval
        self.pulse_time = 0.0

        self.blocks: list[Block] = []
        self.rockets: list[Rocket] = []
        self.powerups: list[PowerUp] = []

        self.start_new_game()

    def request_quit(self):
        self.show_quit_dialog = True
        self.is_firing = False

    def cancel_quit(self):
        self.show_quit_dialog = False

    def handle_quit_click(self, mouse_pos: tuple[int, int]) -> str | None:
        if not self.show_quit_dialog:
            return None
        if self.btn_quit_rect.collidepoint(mouse_pos):
            return "quit"
        if self.btn_cancel_rect.collidepoint(mouse_pos):
            self.cancel_quit()
            return "cancel"
        return None

    def start_new_game(self):
        self.score = 0
        self.wave = 1
        self.game_over = False
        self.wave_timer = self.wave_interval
        self.blocks.clear()
        self.rockets.clear()
        self.powerups.clear()
        self.cannon = Cannon()

        # Spawn initial 3 rows
        for r in range(3):
            self._spawn_row(row_idx=r, offset_y=BOARD_TOP_MARGIN + r * (BLOCK_HEIGHT + BLOCK_PADDING))

    def _spawn_row(self, row_idx: int = 0, offset_y: float = BOARD_TOP_MARGIN):
        col_indices = list(range(GRID_COLS))
        random.shuffle(col_indices)
        num_blocks = random.randint(3, 5)

        for col in col_indices[:num_blocks]:
            bx = BLOCK_PADDING + col * (BLOCK_WIDTH + BLOCK_PADDING)
            by = offset_y
            
            min_hp = max(3, self.wave * 2)
            max_hp = max(8, self.wave * 5 + random.randint(0, 10))
            hp = random.randint(min_hp, max_hp)

            is_bomb = random.random() < 0.12
            self.blocks.append(Block(col, row_idx, bx, by, hp, is_bomb=is_bomb))

    def advance_wave(self):
        shift_y = BLOCK_HEIGHT + BLOCK_PADDING
        for b in self.blocks:
            b.y += shift_y

        self.wave += 1
        self._spawn_row(row_idx=0, offset_y=BOARD_TOP_MARGIN)
        self.wave_timer = max(5.0, self.wave_interval - self.wave * 0.15)

        for b in self.blocks:
            if b.y + b.height >= DEADLINE_Y:
                self.trigger_game_over()
                break

    def trigger_game_over(self):
        self.game_over = True
        self.sound.play("game_over")
        self.screen_shake.add_shake(16.0, duration=0.6)
        if self.score > self.high_score:
            self.high_score = self.score

    def trigger_bomb_explosion(self, center_block: Block):
        cx = center_block.x + center_block.width / 2
        cy = center_block.y + center_block.height / 2
        blast_radius = BLOCK_WIDTH * 1.8

        self.screen_shake.add_shake(12.0, duration=0.4)
        self.particles.emit_explosion(cx, cy, (255, 60, 40), count=50)
        self.sound.play("explode")

        for b in list(self.blocks):
            if b == center_block:
                continue
            bcx = b.x + b.width / 2
            bcy = b.y + b.height / 2
            dist = ((bcx - cx)**2 + (bcy - cy)**2)**0.5
            if dist <= blast_radius:
                destroyed = b.hit(damage=35)
                if destroyed and b in self.blocks:
                    self.blocks.remove(b)
                    self.score += b.max_hp * 5
                    self.particles.emit_explosion(bcx, bcy, b.color, count=25)

    def trigger_vicinity_blast(self, knocked_block: Block):
        """
        Vicinity Blast Mechanic:
        When a block with a bigger number is knocked down,
        any neighboring blocks in its vicinity with a LESSER number
        are automatically blasted in a cascading chain reaction!
        """
        queue = [knocked_block]
        chain_count = 0

        # Vicinity distance threshold (8-neighborhood: horizontal, vertical, diagonal)
        max_dist_x = (BLOCK_WIDTH + BLOCK_PADDING) * 1.35
        max_dist_y = (BLOCK_HEIGHT + BLOCK_PADDING) * 1.35

        while queue:
            source = queue.pop(0)
            src_cx = source.x + source.width / 2
            src_cy = source.y + source.height / 2
            src_val = source.max_hp

            # Find all neighbors in vicinity
            for nb in list(self.blocks):
                nb_cx = nb.x + nb.width / 2
                nb_cy = nb.y + nb.height / 2

                dx = abs(nb_cx - src_cx)
                dy = abs(nb_cy - src_cy)

                if dx <= max_dist_x and dy <= max_dist_y and (dx > 4 or dy > 4):
                    # Lesser number condition: neighbor's remaining HP or max_hp is less than the knocked block!
                    if nb.hp < src_val or nb.max_hp < src_val:
                        if nb in self.blocks:
                            self.blocks.remove(nb)
                            chain_count += 1

                            # Visual electric arc connecting source to blasted neighbor
                            self.particles.emit_lightning_arc((src_cx, src_cy), (nb_cx, nb_cy), color=(255, 225, 60))
                            self.particles.emit_explosion(nb_cx, nb_cy, nb.color, count=28)
                            self.sound.play("explode")
                            self.screen_shake.add_shake(4.0 + min(6.0, chain_count * 1.2), duration=0.2)

                            bonus_pts = nb.max_hp * (4 + chain_count)
                            self.score += bonus_pts

                            combo_tag = f"VICINITY BLAST! +{bonus_pts}" if chain_count == 1 else f"{chain_count}x CHAIN! +{bonus_pts}"
                            self.particles.add_floating_text(nb.x, nb.y, combo_tag, (255, 230, 80), self.font_popup)

                            if nb.is_bomb:
                                self.trigger_bomb_explosion(nb)

                            # Continue cascade
                            queue.append(nb)

    def trigger_freeze_pushback(self):
        shift_y = BLOCK_HEIGHT + BLOCK_PADDING
        for b in self.blocks:
            b.y = max(BOARD_TOP_MARGIN, b.y - shift_y)
        self.particles.add_floating_text(SCREEN_WIDTH / 2 - 45, SCREEN_HEIGHT / 2, "PUSHBACK!", (100, 240, 255), self.font_popup)

    def update(self, dt: float, mouse_pos: tuple[int, int]):
        self.pulse_time += dt

        if self.show_quit_dialog:
            return

        if self.game_over:
            self.particles.update(dt)
            return

        # 1. Update Cannon Aim
        self.cannon.aim_at(mouse_pos[0], mouse_pos[1])
        self.cannon.update(dt)

        # 2. Continuous Firing when held
        if self.is_firing:
            new_rockets = self.cannon.shoot()
            if new_rockets:
                self.rockets.extend(new_rockets)
                self.sound.play("shoot")

        # 3. Wave Timer
        self.wave_timer -= dt
        if self.wave_timer <= 0:
            self.advance_wave()

        # Warning pulse when near deadline
        for b in self.blocks:
            if b.y + b.height >= DEADLINE_Y - (BLOCK_HEIGHT + BLOCK_PADDING):
                if random.random() < 0.025:
                    self.sound.play("warning")
                break

        # 4. Update Rockets & Collisions
        for r in list(self.rockets):
            if not r.update(dt):
                self.rockets.remove(r)
                continue

            self.particles.emit_rocket_trail(r.x, r.y)

            rocket_rect = pygame.Rect(r.x - r.radius, r.y - r.radius, r.radius * 2, r.radius * 2)
            for b in list(self.blocks):
                if rocket_rect.colliderect(b.rect):
                    self.particles.emit_sparks(r.x, r.y, b.color, count=8)
                    self.sound.play("hit")
                    destroyed = b.hit(r.damage)

                    if destroyed and b in self.blocks:
                        self.blocks.remove(b)
                        self.score += b.max_hp * 3
                        self.sound.play("explode")
                        self.screen_shake.add_shake(5.0, duration=0.18)
                        self.particles.emit_explosion(b.x + b.width / 2, b.y + b.height / 2, b.color, count=30)
                        self.particles.add_floating_text(b.x + 10, b.y, f"+{b.max_hp * 3}", COLOR_TEXT_GOLD, self.font_popup)

                        if b.is_bomb:
                            self.trigger_bomb_explosion(b)

                        # Trigger vicinity chain blast on neighboring lesser numbers
                        self.trigger_vicinity_blast(b)

                        # 20% Powerup Drop Chance
                        if random.random() < 0.20:
                            p_type = random.choice([
                                PowerUpType.SPREAD_SHOT,
                                PowerUpType.PIERCE,
                                PowerUpType.RAPID_FIRE,
                                PowerUpType.FREEZE
                            ])
                            self.powerups.append(PowerUp(b.x + b.width / 2, b.y + b.height / 2, p_type))

                    if not r.is_piercing:
                        if r in self.rockets:
                            self.rockets.remove(r)
                        break

        # 5. Update Powerups
        cannon_rect = pygame.Rect(self.cannon.x - 45, self.cannon.y - 45, 90, 90)
        for p in list(self.powerups):
            if not p.update(dt):
                self.powerups.remove(p)
                continue

            p_rect = pygame.Rect(p.x - p.radius, p.y - p.radius, p.radius * 2, p.radius * 2)
            if p_rect.colliderect(cannon_rect) or p.y >= self.cannon.y - 10:
                self.powerups.remove(p)
                self.sound.play("powerup")
                if p.type == PowerUpType.FREEZE:
                    self.trigger_freeze_pushback()
                else:
                    self.cannon.activate_powerup(p.type, duration=8.0)
                self.particles.add_floating_text(self.cannon.x - 45, self.cannon.y - 70, f"{p.label}!", p.color, self.font_popup)
                self.particles.emit_explosion(p.x, p.y, p.color, count=25)

        for b in self.blocks:
            b.update(dt)

        self.particles.update(dt)

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        shake_offset = self.screen_shake.update(1.0 / 60.0)

        # 1. Sleek Dark Canvas Background
        surface.fill(COLOR_BG)

        # Subtle vertical grid line accents
        for col in range(GRID_COLS + 1):
            gx = BLOCK_PADDING + col * (BLOCK_WIDTH + BLOCK_PADDING) - BLOCK_PADDING / 2
            pygame.draw.line(surface, (20, 24, 36), (gx, BOARD_TOP_MARGIN), (gx, DEADLINE_Y), 1)

        # 2. Polished Danger Barrier (No tofu boxes, pure glowing vector graphics)
        self._draw_danger_barrier(surface, shake_offset)

        # 3. Blocks
        for b in self.blocks:
            b.draw(surface, shake_offset, self.font_block)

        # 4. Powerups
        for p in self.powerups:
            p.draw(surface, shake_offset, self.font_badge)

        # 5. Rockets
        for r in self.rockets:
            r.draw(surface, shake_offset)

        # 6. Particles
        self.particles.draw(surface, shake_offset)

        # 7. Cannon
        self.cannon.draw(surface, shake_offset, mouse_pos)

        # 8. HUD & Top Bar
        self._draw_hud(surface)

        # 9. Game Over Overlay
        if self.game_over:
            self._draw_game_over(surface)

        # 10. Quit Confirmation Dialog Overlay
        if self.show_quit_dialog:
            self._draw_quit_dialog(surface, mouse_pos)

    def _draw_danger_barrier(self, surface: pygame.Surface, offset: tuple[float, float]):
        danger_y = int(DEADLINE_Y + offset[1])

        # Soft red warning glow band
        glow_surf = pygame.Surface((SCREEN_WIDTH, 24), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 40, 70, 35), (0, 0, SCREEN_WIDTH, 24))
        surface.blit(glow_surf, (0, danger_y - 12))

        # Main laser deadline
        pygame.draw.line(surface, (255, 50, 80), (0, danger_y), (SCREEN_WIDTH, danger_y), 2)
        # Inner white laser core
        pygame.draw.line(surface, (255, 200, 215), (0, danger_y), (SCREEN_WIDTH, danger_y), 1)

        # Centered Sleek Danger Badge
        badge_w = 140
        badge_h = 20
        badge_x = (SCREEN_WIDTH - badge_w) // 2
        badge_y = danger_y + 4

        # Badge pill
        pygame.draw.rect(surface, (28, 18, 26), (badge_x, badge_y, badge_w, badge_h), border_radius=10)
        pygame.draw.rect(surface, (255, 60, 90), (badge_x, badge_y, badge_w, badge_h), width=1, border_radius=10)

        # Hand-drawn antialiased triangle caution markers (guaranteed NO tofu squares)
        # Left warning triangle: ▲
        lt_pts = [(badge_x + 12, badge_y + 5), (badge_x + 8, badge_y + 15), (badge_x + 16, badge_y + 15)]
        pygame.draw.polygon(surface, (255, 75, 100), lt_pts)

        # Right warning triangle: ▲
        rt_pts = [(badge_x + badge_w - 12, badge_y + 5), (badge_x + badge_w - 16, badge_y + 15), (badge_x + badge_w - 8, badge_y + 15)]
        pygame.draw.polygon(surface, (255, 75, 100), rt_pts)

        # Clean ASCII text label
        lbl = self.font_badge.render("DANGER LINE", True, (255, 160, 180))
        surface.blit(lbl, (badge_x + (badge_w - lbl.get_width()) // 2, badge_y + 3))

    def _draw_hud(self, surface: pygame.Surface):
        # 1. Dark Glass Header Card
        header_h = BOARD_TOP_MARGIN - 16
        header_rect = pygame.Rect(12, 10, SCREEN_WIDTH - 24, header_h)
        
        # Rounded header container
        pygame.draw.rect(surface, (22, 27, 40), header_rect, border_radius=14)
        pygame.draw.rect(surface, (38, 46, 68), header_rect, width=1, border_radius=14)

        # Score Section
        s_lbl = self.font_small.render("SCORE", True, COLOR_TEXT_MUTED)
        s_val = self.font_score.render(f"{self.score:,}", True, COLOR_TEXT_WHITE)
        surface.blit(s_lbl, (30, 16))
        surface.blit(s_val, (30, 32))

        # Wave Pill Badge in Center
        w_text = self.font_score.render(f"WAVE {self.wave}", True, (50, 220, 255))
        w_rect = w_text.get_rect(center=(SCREEN_WIDTH // 2, 38))
        pill_rect = pygame.Rect(w_rect.x - 14, w_rect.y - 4, w_rect.width + 28, w_rect.height + 8)
        pygame.draw.rect(surface, (14, 18, 28), pill_rect, border_radius=12)
        pygame.draw.rect(surface, (40, 180, 220), pill_rect, width=1, border_radius=12)
        surface.blit(w_text, w_rect)

        # Best Score Section
        hi_lbl = self.font_small.render("BEST", True, COLOR_TEXT_MUTED)
        hi_val = self.font_score.render(f"{max(self.score, self.high_score):,}", True, COLOR_TEXT_GOLD)
        surface.blit(hi_lbl, (SCREEN_WIDTH - 110, 16))
        surface.blit(hi_val, (SCREEN_WIDTH - 110, 32))

        # 2. Wave Countdown Progress Bar
        progress = max(0.0, min(1.0, self.wave_timer / self.wave_interval))
        bar_w = SCREEN_WIDTH - 50
        bar_h = 3
        bar_x = 25
        bar_y = 66
        pygame.draw.rect(surface, (35, 42, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=2)
        fill_w = int(bar_w * (1.0 - progress))
        if fill_w > 0:
            pygame.draw.rect(surface, (255, 95, 65), (bar_x, bar_y, fill_w, bar_h), border_radius=2)

        # 3. Active Power-Up Badges at Bottom
        badge_x = 20
        badge_y = SCREEN_HEIGHT - 32
        for ptype, timer in self.cannon.powerup_timers.items():
            if timer > 0:
                name = {
                    PowerUpType.SPREAD_SHOT: "3X SPREAD",
                    PowerUpType.PIERCE: "LASER DRILL",
                    PowerUpType.RAPID_FIRE: "RAPID FIRE",
                }.get(ptype, "")
                badge_text = self.font_small.render(f"{name} {timer:.1f}s", True, (255, 255, 255))
                bw = badge_text.get_width() + 18
                # Glowing badge
                pygame.draw.rect(surface, (32, 42, 64), (badge_x, badge_y, bw, 22), border_radius=6)
                pygame.draw.rect(surface, (60, 190, 240), (badge_x, badge_y, bw, 22), width=1, border_radius=6)
                surface.blit(badge_text, (badge_x + 9, badge_y + 3))
                badge_x += bw + 8

    def _draw_game_over(self, surface: pygame.Surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 12, 18, 225))
        surface.blit(overlay, (0, 0))

        card_w = 380
        card_h = 260
        card_rect = pygame.Rect((SCREEN_WIDTH - card_w) / 2, (SCREEN_HEIGHT - card_h) / 2, card_w, card_h)
        pygame.draw.rect(surface, (24, 28, 42), card_rect, border_radius=18)
        pygame.draw.rect(surface, COLOR_DEADLINE, card_rect, width=2, border_radius=18)

        t = self.font_title.render("GAME OVER", True, COLOR_DEADLINE)
        tr = t.get_rect(center=(SCREEN_WIDTH / 2, card_rect.top + 45))
        surface.blit(t, tr)

        s = self.font_score.render(f"Final Score: {self.score:,}", True, COLOR_TEXT_WHITE)
        sr = s.get_rect(center=(SCREEN_WIDTH / 2, card_rect.top + 100))
        surface.blit(s, sr)

        w = self.font_block.render(f"Reached Wave {self.wave}", True, COLOR_TEXT_MUTED)
        wr = w.get_rect(center=(SCREEN_WIDTH / 2, card_rect.top + 138))
        surface.blit(w, wr)

        r_text = self.font_popup.render("Click Anywhere or Press [R] to Play Again", True, COLOR_TEXT_GOLD)
        rr = r_text.get_rect(center=(SCREEN_WIDTH / 2, card_rect.top + 205))
        surface.blit(r_text, rr)

    def _draw_quit_dialog(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        # Dim backdrop
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 220))
        surface.blit(overlay, (0, 0))

        # Modal Card
        card_w, card_h = 390, 220
        card_x = (SCREEN_WIDTH - card_w) // 2
        card_y = (SCREEN_HEIGHT - card_h) // 2
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # Drop shadow
        shadow_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 150), (0, 0, card_w, card_h), border_radius=18)
        surface.blit(shadow_surf, (card_x + 3, card_y + 6))

        # Card container
        pygame.draw.rect(surface, (22, 27, 40), card_rect, border_radius=18)
        pygame.draw.rect(surface, (255, 65, 95), card_rect, width=2, border_radius=18)

        # Title
        title_text = self.font_title.render("QUIT GAME?", True, (255, 75, 105))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, card_y + 45))
        surface.blit(title_text, title_rect)

        # Message
        msg_text = self.font_popup.render("Are you sure you want to quit?", True, (230, 235, 245))
        msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, card_y + 92))
        surface.blit(msg_text, msg_rect)

        # Buttons
        # 1. QUIT Button
        is_quit_hover = self.btn_quit_rect.collidepoint(mouse_pos)
        quit_bg = (235, 55, 80) if is_quit_hover else (175, 38, 56)
        pygame.draw.rect(surface, quit_bg, self.btn_quit_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 120, 140), self.btn_quit_rect, width=1, border_radius=10)
        q_label = self.font_popup.render("YES, QUIT [Y]", True, (255, 255, 255))
        surface.blit(q_label, q_label.get_rect(center=self.btn_quit_rect.center))

        # 2. CANCEL Button
        is_cancel_hover = self.btn_cancel_rect.collidepoint(mouse_pos)
        cancel_bg = (55, 68, 95) if is_cancel_hover else (35, 44, 62)
        pygame.draw.rect(surface, cancel_bg, self.btn_cancel_rect, border_radius=10)
        pygame.draw.rect(surface, (80, 105, 145), self.btn_cancel_rect, width=1, border_radius=10)
        c_label = self.font_popup.render("CANCEL [Esc]", True, (255, 255, 255))
        surface.blit(c_label, c_label.get_rect(center=self.btn_cancel_rect.center))
