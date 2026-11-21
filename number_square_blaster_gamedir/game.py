"""Block Blast - Main Game Engine, Waves, and Collision Coordinator"""
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
        # Subsystems
        self.particles = ParticleSystem()
        self.sound = SoundManager()
        self.screen_shake = ScreenShake()
        self.cannon = Cannon()

        # Fonts
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Helvetica Neue, Arial, sans-serif", 32, bold=True)
        self.font_score = pygame.font.SysFont("Helvetica Neue, Arial, sans-serif", 24, bold=True)
        self.font_block = pygame.font.SysFont("Helvetica Neue, Arial, sans-serif", 18, bold=True)
        self.font_small = pygame.font.SysFont("Helvetica Neue, Arial, sans-serif", 13)
        self.font_popup = pygame.font.SysFont("Helvetica Neue, Arial, sans-serif", 16, bold=True)

        # Game State
        self.score = 0
        self.high_score = 0
        self.wave = 1
        self.game_over = False
        self.is_firing = False
        
        # Wave Timing
        self.wave_interval = 7.5  # Seconds between new row descending
        self.wave_timer = self.wave_interval

        # Entities
        self.blocks: list[Block] = []
        self.rockets: list[Rocket] = []
        self.powerups: list[PowerUp] = []

        # Start game
        self.start_new_game()

    def start_new_game(self):
        self.score = 0
        self.wave = 1
        self.game_over = False
        self.wave_timer = self.wave_interval
        self.blocks.clear()
        self.rockets.clear()
        self.powerups.clear()
        self.cannon = Cannon()

        # Initial 3 rows of blocks
        for r in range(3):
            self._spawn_row(row_idx=r, offset_y=BOARD_TOP_MARGIN + r * (BLOCK_HEIGHT + BLOCK_PADDING))

    def _spawn_row(self, row_idx: int = 0, offset_y: float = BOARD_TOP_MARGIN):
        """Spawn a new row of blocks at the top."""
        # 1 to 5 blocks per row with varying health
        col_indices = list(range(GRID_COLS))
        random.shuffle(col_indices)
        num_blocks = random.randint(3, 5)

        for col in col_indices[:num_blocks]:
            bx = BLOCK_PADDING + col * (BLOCK_WIDTH + BLOCK_PADDING)
            by = offset_y
            
            # Base HP scales with wave number
            min_hp = max(3, self.wave * 2)
            max_hp = max(8, self.wave * 5 + random.randint(0, 10))
            hp = random.randint(min_hp, max_hp)

            # 12% chance of being a Bomb block
            is_bomb = random.random() < 0.12
            self.blocks.append(Block(col, row_idx, bx, by, hp, is_bomb=is_bomb))

    def advance_wave(self):
        """Push all active blocks down by 1 row step."""
        shift_y = BLOCK_HEIGHT + BLOCK_PADDING
        for b in self.blocks:
            b.y += shift_y

        # Spawn new top row
        self.wave += 1
        self._spawn_row(row_idx=0, offset_y=BOARD_TOP_MARGIN)
        self.wave_timer = max(5.0, self.wave_interval - self.wave * 0.15)

        # Check if blocks hit deadline
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
        """Detonate 3x3 surrounding radius of blocks."""
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
                destroyed = b.hit(damage=30)
                if destroyed and b in self.blocks:
                    self.blocks.remove(b)
                    self.score += b.max_hp * 5
                    self.particles.emit_explosion(bcx, bcy, b.color, count=25)

    def trigger_freeze_pushback(self):
        """Push all blocks up by 1 row (giving breathing room)."""
        shift_y = BLOCK_HEIGHT + BLOCK_PADDING
        for b in self.blocks:
            b.y = max(BOARD_TOP_MARGIN, b.y - shift_y)
        self.particles.add_floating_text(SCREEN_WIDTH / 2 - 40, SCREEN_HEIGHT / 2, "PUSHBACK!", (100, 240, 255), self.font_popup)

    def update(self, dt: float, mouse_pos: tuple[int, int]):
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

        # Warning sound when near deadline
        for b in self.blocks:
            if b.y + b.height >= DEADLINE_Y - (BLOCK_HEIGHT + BLOCK_PADDING):
                if random.random() < 0.03:
                    self.sound.play("warning")
                break

        # 4. Update Rockets & Collisions
        for r in list(self.rockets):
            if not r.update(dt):
                self.rockets.remove(r)
                continue

            # Emit smoke/fire trail
            self.particles.emit_rocket_trail(r.x, r.y)

            # Check collision with blocks
            rocket_rect = pygame.Rect(r.x - r.radius, r.y - r.radius, r.radius * 2, r.radius * 2)
            for b in list(self.blocks):
                if rocket_rect.colliderect(b.rect):
                    # Hit block
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

                        # Bomb detonation
                        if b.is_bomb:
                            self.trigger_bomb_explosion(b)

                        # Powerup Drop Chance (20%)
                        if random.random() < 0.20:
                            p_type = random.choice([
                                PowerUpType.SPREAD_SHOT,
                                PowerUpType.PIERCE,
                                PowerUpType.RAPID_FIRE,
                                PowerUpType.FREEZE
                            ])
                            self.powerups.append(PowerUp(b.x + b.width / 2, b.y + b.height / 2, p_type))

                    # Non-piercing rocket vanishes on hit
                    if not r.is_piercing:
                        if r in self.rockets:
                            self.rockets.remove(r)
                        break

        # 5. Update Powerups & Collection
        cannon_rect = pygame.Rect(self.cannon.x - 40, self.cannon.y - 40, 80, 80)
        for p in list(self.powerups):
            if not p.update(dt):
                self.powerups.remove(p)
                continue

            # Collect when it reaches near the player launcher
            p_rect = pygame.Rect(p.x - p.radius, p.y - p.radius, p.radius * 2, p.radius * 2)
            if p_rect.colliderect(cannon_rect) or p.y >= self.cannon.y - 15:
                self.powerups.remove(p)
                self.sound.play("powerup")
                if p.type == PowerUpType.FREEZE:
                    self.trigger_freeze_pushback()
                else:
                    self.cannon.activate_powerup(p.type, duration=8.0)
                self.particles.add_floating_text(self.cannon.x - 30, self.cannon.y - 60, f"{p.label} ACTIVE!", p.color, self.font_popup)
                self.particles.emit_explosion(p.x, p.y, p.color, count=25)

        # 6. Update Blocks & Particles
        for b in self.blocks:
            b.update(dt)

        self.particles.update(dt)

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        shake_offset = self.screen_shake.update(1.0 / 60.0)

        # 1. Background
        surface.fill(COLOR_BG)

        # 2. Danger Deadline Line
        danger_y = DEADLINE_Y + shake_offset[1]
        pygame.draw.line(surface, COLOR_DEADLINE, (0, danger_y), (SCREEN_WIDTH, danger_y), 3)
        
        # Danger warning label
        danger_text = self.font_small.render("▼ DANGER DEADLINE ▼", True, (255, 80, 100))
        surface.blit(danger_text, (SCREEN_WIDTH / 2 - danger_text.get_width() / 2, danger_y + 6))

        # 3. Draw Blocks
        for b in self.blocks:
            b.draw(surface, shake_offset, self.font_block)

        # 4. Draw Powerups
        for p in self.powerups:
            p.draw(surface, shake_offset, self.font_popup)

        # 5. Draw Rockets
        for r in self.rockets:
            r.draw(surface, shake_offset)

        # 6. Draw Particles and Floating Texts
        self.particles.draw(surface, shake_offset)

        # 7. Draw Cannon Launcher
        self.cannon.draw(surface, shake_offset, mouse_pos)

        # 8. Draw HUD / Top Bar
        self._draw_hud(surface)

        # 9. Draw Game Over Overlay
        if self.game_over:
            self._draw_game_over(surface)

    def _draw_hud(self, surface: pygame.Surface):
        # Header banner
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, BOARD_TOP_MARGIN - 15)
        pygame.draw.rect(surface, (20, 24, 36), header_rect)
        pygame.draw.line(surface, (40, 48, 68), (0, BOARD_TOP_MARGIN - 15), (SCREEN_WIDTH, BOARD_TOP_MARGIN - 15), 1)

        # Score
        score_lbl = self.font_small.render("SCORE", True, COLOR_TEXT_MUTED)
        score_val = self.font_score.render(f"{self.score:,}", True, COLOR_TEXT_WHITE)
        surface.blit(score_lbl, (20, 12))
        surface.blit(score_val, (20, 28))

        # Wave
        wave_lbl = self.font_small.render("WAVE", True, COLOR_TEXT_MUTED)
        wave_val = self.font_score.render(f"{self.wave}", True, (50, 220, 255))
        surface.blit(wave_lbl, (SCREEN_WIDTH / 2 - 25, 12))
        surface.blit(wave_val, (SCREEN_WIDTH / 2 - 25, 28))

        # High Score
        hi_lbl = self.font_small.render("BEST", True, COLOR_TEXT_MUTED)
        hi_val = self.font_score.render(f"{max(self.score, self.high_score):,}", True, COLOR_TEXT_GOLD)
        surface.blit(hi_lbl, (SCREEN_WIDTH - 110, 12))
        surface.blit(hi_val, (SCREEN_WIDTH - 110, 28))

        # Wave progress countdown bar
        progress = max(0.0, min(1.0, self.wave_timer / self.wave_interval))
        bar_w = SCREEN_WIDTH - 40
        bar_h = 4
        bar_x = 20
        bar_y = 66
        pygame.draw.rect(surface, (35, 42, 58), (bar_x, bar_y, bar_w, bar_h), border_radius=2)
        pygame.draw.rect(surface, (255, 100, 60), (bar_x, bar_y, bar_w * (1.0 - progress), bar_h), border_radius=2)

        # Active Powerup Badges
        badge_x = 20
        badge_y = SCREEN_HEIGHT - 32
        for ptype, timer in self.cannon.powerup_timers.items():
            if timer > 0:
                name = {
                    PowerUpType.SPREAD_SHOT: "3X SPREAD",
                    PowerUpType.PIERCE: "PIERCE",
                    PowerUpType.RAPID_FIRE: "RAPID",
                }.get(ptype, "")
                badge_text = self.font_small.render(f"{name} {timer:.1f}s", True, (255, 255, 255))
                bw = badge_text.get_width() + 16
                pygame.draw.rect(surface, (40, 50, 75), (badge_x, badge_y, bw, 22), border_radius=4)
                surface.blit(badge_text, (badge_x + 8, badge_y + 3))
                badge_x += bw + 8

    def _draw_game_over(self, surface: pygame.Surface):
        # Dark modal overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 12, 18, 220))
        surface.blit(overlay, (0, 0))

        # Game Over Card
        card_w = 400
        card_h = 280
        card_rect = pygame.Rect((SCREEN_WIDTH - card_w) / 2, (SCREEN_HEIGHT - card_h) / 2, card_w, card_h)
        pygame.draw.rect(surface, (25, 28, 42), card_rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_DEADLINE, card_rect, width=2, border_radius=16)

        # Title
        t = self.font_title.render("GAME OVER", True, COLOR_DEADLINE)
        tr = t.get_rect(center=(SCREEN_WIDTH / 2, card_rect.top + 45))
        surface.blit(t, tr)

        # Final Score
        s = self.font_score.render(f"Final Score: {self.score:,}", True, COLOR_TEXT_WHITE)
        sr = s.get_rect(center=(SCREEN_WIDTH / 2, card_rect.top + 105))
        surface.blit(s, sr)

        # Wave Reached
        w = self.font_block.render(f"Reached Wave {self.wave}", True, COLOR_TEXT_MUTED)
        wr = w.get_rect(center=(SCREEN_WIDTH / 2, card_rect.top + 145))
        surface.blit(w, wr)

        # Restart Instruction
        r_text = self.font_popup.render("Click Anywhere or Press [R] to Play Again", True, COLOR_TEXT_GOLD)
        rr = r_text.get_rect(center=(SCREEN_WIDTH / 2, card_rect.top + 215))
        surface.blit(r_text, rr)
