"""
game_state.py - Gameplay Coordinator, Input DAS/ARR Handling, Lock Delay & Mode Rules.
"""

import pygame
from config import (
    DEFAULT_COLS, DEFAULT_ROWS, WIDE_COLS, CELL_SIZE, CELL_SIZE_WIDE,
    DAS_DELAY, ARR_RATE, SOFT_DROP_FACTOR, LOCK_DELAY, MAX_LOCK_RESETS
)
from src.engine.board import Board
from src.engine.randomizer import SevenBagRandomizer
from src.engine.score_manager import ScoreManager
from src.graphics.particles import ParticleManager


class GameState:
    def __init__(self, sound_manager, shader_manager, mode='marathon'):
        self.sound_mgr = sound_manager
        self.shader_mgr = shader_manager
        self.mode = mode
        self.particle_mgr = ParticleManager()

        # Board sizing based on mode
        self.is_wide = (mode == 'wide')
        self.cols = WIDE_COLS if self.is_wide else DEFAULT_COLS
        self.rows = DEFAULT_ROWS
        self.cell_size = CELL_SIZE_WIDE if self.is_wide else CELL_SIZE

        self.board = Board(cols=self.cols, rows=self.rows)
        self.randomizer = SevenBagRandomizer(cols=self.cols)
        self.score_mgr = ScoreManager(mode=self.mode)

        # Active piece states
        self.active_piece = None
        self.held_kind = None
        self.swapped_this_drop = False

        # Drop & Lock Timers
        self.gravity_timer = 0.0
        self.lock_timer = 0
        self.lock_delay = LOCK_DELAY
        self.lock_resets = 0
        self.touching_surface = False

        # Input DAS / ARR Timers
        self.key_states = {'left': False, 'right': False, 'soft_drop': False}
        self.das_timer = {'left': 0, 'right': 0}

        # Game session metrics
        self.elapsed_time = 0.0
        self.is_game_over = False
        self.is_victory = False
        self.is_paused = False
        self.show_ghost = True

        # Line clear delay state
        self.is_clearing_lines = False
        self.clear_delay_timer = 0.0
        self.pending_clear_rows = []
        self.last_tspin_result = 'none'

        self.spawn_next_piece()

    def spawn_next_piece(self):
        self.active_piece = self.randomizer.pop_next()
        self.swapped_this_drop = False
        self.lock_timer = 0
        self.lock_resets = 0
        self.gravity_timer = 0.0
        self.touching_surface = False
        self.last_tspin_result = 'none'

        # Check immediate spawn block out (Game Over)
        if not self.board.is_valid_position(self.active_piece):
            self.trigger_game_over()

    def swap_hold(self):
        if self.swapped_this_drop or self.is_game_over or self.is_clearing_lines:
            return

        current_kind = self.active_piece.kind
        self.sound_mgr.play('hold')

        if self.held_kind is None:
            self.held_kind = current_kind
            self.spawn_next_piece()
        else:
            spawn_x, spawn_y = self.randomizer.get_spawn_coords(self.held_kind)
            from src.engine.tetromino import Tetromino
            self.active_piece = Tetromino(self.held_kind, spawn_x, spawn_y, rotation=0)
            self.held_kind = current_kind
            self.lock_timer = 0
            self.lock_resets = 0
            self.gravity_timer = 0.0

        self.swapped_this_drop = True

    def move_lateral(self, dx):
        if self.is_game_over or self.is_clearing_lines or not self.active_piece:
            return False

        if self.board.is_valid_position(self.active_piece, offset_x=self.active_piece.x + dx):
            self.active_piece.x += dx
            self.active_piece.last_move_was_rotation = False
            self.sound_mgr.play('move')

            # Reset lock delay if piece moved while grounded
            if self.touching_surface and self.lock_resets < MAX_LOCK_RESETS:
                self.lock_timer = 0
                self.lock_resets += 1
            return True
        return False

    def rotate_piece(self, clockwise=True):
        if self.is_game_over or self.is_clearing_lines or not self.active_piece:
            return False

        from_rot = self.active_piece.rotation
        to_rot = (from_rot + 1) % 4 if clockwise else (from_rot - 1) % 4
        kicks = self.active_piece.get_wall_kicks(from_rot, to_rot)

        for kick_idx, (kx, ky) in enumerate(kicks):
            cand_x = self.active_piece.x + kx
            cand_y = self.active_piece.y + ky
            if self.board.is_valid_position(self.active_piece, offset_x=cand_x, offset_y=cand_y, rotation=to_rot):
                self.active_piece.x = cand_x
                self.active_piece.y = cand_y
                self.active_piece.rotation = to_rot
                self.active_piece.last_move_was_rotation = True
                self.active_piece.last_kick_index = kick_idx
                self.sound_mgr.play('rotate')

                if self.touching_surface and self.lock_resets < MAX_LOCK_RESETS:
                    self.lock_timer = 0
                    self.lock_resets += 1
                return True
        return False

    def hard_drop(self):
        if self.is_game_over or self.is_clearing_lines or not self.active_piece:
            return

        ghost_y = self.board.get_ghost_y(self.active_piece)
        dropped_rows = ghost_y - self.active_piece.y
        self.active_piece.y = ghost_y
        self.score_mgr.add_hard_drop_points(dropped_rows)

        # VFX & Audio
        self.sound_mgr.play('hard_drop')
        if self.shader_mgr:
            self.shader_mgr.trigger_impact(shockwave=0.35, chromatic=0.55)

        # Particle splash at landing coordinates
        board_x = (1200 - self.cols * self.cell_size) // 2
        board_y = (800 - self.rows * self.cell_size) // 2 + 20
        screen_blocks = [
            (board_x + bx * self.cell_size, board_y + (by - self.board.buffer_rows) * self.cell_size)
            for bx, by in self.active_piece.get_blocks()
        ]
        self.particle_mgr.spawn_hard_drop_impact(screen_blocks, self.active_piece.color, self.cell_size)

        self.lock_active_piece()

    def lock_active_piece(self):
        # Check for T-spin before locking into matrix
        tspin_result = self.board.check_t_spin(self.active_piece)
        self.last_tspin_result = tspin_result

        game_over = self.board.lock_piece(self.active_piece)
        if game_over:
            self.trigger_game_over()
            return

        self.sound_mgr.play('lock')

        # Find line clears
        full_rows = self.board.find_completed_lines()
        if full_rows:
            self.pending_clear_rows = full_rows
            self.is_clearing_lines = True
            self.clear_delay_timer = 0.18

            # Spawn laser / particle disintegration along each cleared row
            board_x = (1200 - self.cols * self.cell_size) // 2
            board_y = (800 - self.rows * self.cell_size) // 2 + 20
            matrix_w = self.cols * self.cell_size
            for r in full_rows:
                disp_r = r - self.board.buffer_rows
                row_y = board_y + disp_r * self.cell_size
                self.particle_mgr.spawn_line_clear_explosion(row_y, board_x, matrix_w, self.cell_size)
        else:
            self.score_mgr.register_lock_without_clear()
            self.spawn_next_piece()

    def finish_line_clears(self):
        cleared_count = self.board.remove_lines(self.pending_clear_rows)
        self.pending_clear_rows.clear()
        self.is_clearing_lines = False

        is_perfect = self.board.is_perfect_clear()
        result = self.score_mgr.register_line_clear(cleared_count, tspin_type=self.last_tspin_result, is_perfect_clear=is_perfect)

        if result:
            # Play line clear sound & combo
            if result['combo'] > 0:
                self.sound_mgr.play('combo', combo_count=result['combo'])
            self.sound_mgr.play_line_clear(cleared_count)

            if result['level_up']:
                self.sound_mgr.play('levelup')

            if self.shader_mgr:
                chroma = 0.4 + cleared_count * 0.15
                self.shader_mgr.trigger_impact(shockwave=0.25 + cleared_count * 0.1, chromatic=chroma)

            # Floating text
            board_x = (1200 - self.cols * self.cell_size) // 2
            board_y = (800 - self.rows * self.cell_size) // 2 + 20
            cx = board_x + (self.cols * self.cell_size) // 2
            cy = board_y + (self.rows * self.cell_size) // 2

            if result['action_name']:
                self.particle_mgr.add_floating_text(cx, cy - 20, result['action_name'], color=(255, 230, 60), font_size=28)
            if result['b2b']:
                self.particle_mgr.add_floating_text(cx, cy + 15, "BACK-TO-BACK!", color=(255, 180, 50), font_size=20)
            if result['is_perfect_clear']:
                self.particle_mgr.add_floating_text(cx, cy - 55, "★ ALL CLEAR! ★", color=(0, 240, 255), font_size=32)

        # Check mode win conditions
        if self.mode == 'sprint' and self.score_mgr.lines >= 40:
            self.trigger_victory()
            return
        elif self.mode == 'marathon' and self.score_mgr.level > 15:
            self.trigger_victory()
            return

        self.spawn_next_piece()

    def trigger_game_over(self):
        self.is_game_over = True
        self.sound_mgr.play('gameover')
        self.score_mgr.save_high_score()

    def trigger_victory(self):
        self.is_victory = True
        self.sound_mgr.play('levelup')
        self.score_mgr.save_high_score()

    def handle_event(self, event):
        if self.is_game_over or self.is_victory:
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.key_states['left'] = True
                self.das_timer['left'] = 0
                self.move_lateral(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.key_states['right'] = True
                self.das_timer['right'] = 0
                self.move_lateral(1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.key_states['soft_drop'] = True
            elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_x):
                self.rotate_piece(clockwise=True)
            elif event.key in (pygame.K_z, pygame.K_q):
                self.rotate_piece(clockwise=False)
            elif event.key == pygame.K_SPACE:
                self.hard_drop()
            elif event.key in (pygame.K_c, pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.swap_hold()
            elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.is_paused = not self.is_paused

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.key_states['left'] = False
                self.das_timer['left'] = 0
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.key_states['right'] = False
                self.das_timer['right'] = 0
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.key_states['soft_drop'] = False

    def update(self, dt):
        if self.is_paused or self.is_game_over or self.is_victory:
            return

        self.elapsed_time += dt
        self.particle_mgr.update(dt)

        # Ultra mode: 3-minute time limit (180s)
        if self.mode == 'ultra' and self.elapsed_time >= 180.0:
            self.trigger_victory()
            return

        # Handle line clear delay
        if self.is_clearing_lines:
            self.clear_delay_timer -= dt
            if self.clear_delay_timer <= 0:
                self.finish_line_clears()
            return

        if not self.active_piece:
            return

        # DAS & ARR Lateral movement
        for key, dir_val in (('left', -1), ('right', 1)):
            if self.key_states[key]:
                self.das_timer[key] += 1
                if self.das_timer[key] >= DAS_DELAY:
                    if (self.das_timer[key] - DAS_DELAY) % ARR_RATE == 0:
                        self.move_lateral(dir_val)

        # Check if active piece is touching the surface below
        can_drop_one = self.board.is_valid_position(self.active_piece, offset_y=self.active_piece.y + 1)
        self.touching_surface = not can_drop_one

        # Gravity & Soft Drop calculation
        interval = self.score_mgr.gravity_interval
        if self.key_states['soft_drop']:
            interval /= SOFT_DROP_FACTOR

        self.gravity_timer += dt
        while self.gravity_timer >= interval:
            self.gravity_timer -= interval
            if can_drop_one:
                self.active_piece.y += 1
                self.active_piece.last_move_was_rotation = False
                if self.key_states['soft_drop']:
                    self.score_mgr.add_soft_drop_points(1)
                    self.sound_mgr.play('soft_drop')
                can_drop_one = self.board.is_valid_position(self.active_piece, offset_y=self.active_piece.y + 1)
                self.touching_surface = not can_drop_one
            else:
                break

        # Lock delay timer when resting on surface
        if self.touching_surface:
            self.lock_timer += 1
            if self.lock_timer >= self.lock_delay:
                self.lock_active_piece()
        else:
            self.lock_timer = 0
