"""2048 Game - Visual Renderer: Anti-Aliased Rounded Rects, Glows, HUD & Overlays"""
import math
import pygame
from core.constants import (
    GRID_SIZE, TILE_SIZE, GRID_GAP,
    BOARD_WIDTH, BOARD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    BOARD_OFFSET_X, BOARD_OFFSET_Y,
    THEME_LIGHT, THEME_DARK, PALETTE_LIGHT, PALETTE_DARK,
    TILE_COLORS, TILE_BORDER_RADIUS, BOARD_BORDER_RADIUS,
    BUTTON_BORDER_RADIUS, BADGE_BORDER_RADIUS
)
from core.board import Board
from core.tile import AnimatedTile

class GameRenderer:
    def __init__(self):
        self.theme = THEME_LIGHT
        pygame.font.init()

        # Cross-platform crisp typography
        font_names = ["Clear Sans", "Arial", "Trebuchet MS", "Helvetica", "DejaVu Sans", "sans-serif"]
        self.font_logo = pygame.font.SysFont(font_names, 48, bold=True)
        self.font_subtitle = pygame.font.SysFont(font_names, 13, bold=False)
        self.font_badge_title = pygame.font.SysFont(font_names, 11, bold=True)
        self.font_badge_val = pygame.font.SysFont(font_names, 20, bold=True)
        self.font_btn = pygame.font.SysFont(font_names, 14, bold=True)
        self.font_overlay_title = pygame.font.SysFont(font_names, 42, bold=True)
        self.font_overlay_sub = pygame.font.SysFont(font_names, 16, bold=False)

        # Precached tile font sizes (from 2-digit to 6-digit numbers)
        self.tile_fonts = {
            1: pygame.font.SysFont(font_names, 52, bold=True),  # 2, 4, 8
            2: pygame.font.SysFont(font_names, 46, bold=True),  # 16, 32, 64
            3: pygame.font.SysFont(font_names, 38, bold=True),  # 128, 256, 512
            4: pygame.font.SysFont(font_names, 30, bold=True),  # 1024, 2048
            5: pygame.font.SysFont(font_names, 24, bold=True),  # 16384
            6: pygame.font.SysFont(font_names, 20, bold=True),  # 131072
        }

        # Header UI Button Rects
        # Row 1: Logo (left), Score & Best badges (right)
        self.rect_score_badge = pygame.Rect(SCREEN_WIDTH - BOARD_OFFSET_X - 190, 24, 90, 52)
        self.rect_best_badge = pygame.Rect(SCREEN_WIDTH - BOARD_OFFSET_X - 92, 24, 92, 52)

        # Row 2: Actions
        btn_y = 135
        self.rect_btn_new = pygame.Rect(SCREEN_WIDTH - BOARD_OFFSET_X - 105, btn_y, 105, 38)
        self.rect_btn_undo = pygame.Rect(SCREEN_WIDTH - BOARD_OFFSET_X - 180, btn_y, 68, 38)
        self.rect_btn_theme = pygame.Rect(SCREEN_WIDTH - BOARD_OFFSET_X - 265, btn_y, 78, 38)
        self.rect_btn_sound = pygame.Rect(SCREEN_WIDTH - BOARD_OFFSET_X - 325, btn_y, 52, 38)

    @property
    def palette(self) -> dict:
        return PALETTE_LIGHT if self.theme == THEME_LIGHT else PALETTE_DARK

    def toggle_theme(self) -> str:
        self.theme = THEME_DARK if self.theme == THEME_LIGHT else THEME_LIGHT
        return self.theme

    def render(self, surface: pygame.Surface, board: Board, anim_time: float, sound_enabled: bool, show_quit: bool):
        pal = self.palette
        surface.fill(pal["bg"])

        # 1. Header (Logo, Subtitle, Score & Best badges, Action buttons)
        self._draw_header(surface, board, sound_enabled)

        # 2. Main Board Grid Background & Empty Cells
        self._draw_board_grid(surface)

        # 3. Active & Sliding Animated Tiles
        self._draw_tiles(surface, board, anim_time)

        # 4. Modals and Overlays
        if board.has_won and not board.keep_playing:
            self._draw_victory_overlay(surface)
        elif board.game_over:
            self._draw_game_over_overlay(surface)

        if show_quit:
            self._draw_quit_dialog(surface)

    def _draw_header(self, surface: pygame.Surface, board: Board, sound_enabled: bool):
        pal = self.palette
        mouse_pos = pygame.mouse.get_pos()

        # Logo "2048"
        logo_surf = self.font_logo.render("2048", True, pal["text_dark"])
        surface.blit(logo_surf, (BOARD_OFFSET_X, 22))

        # Subtitle
        sub_surf = self.font_subtitle.render("Join the numbers to get to 2048!", True, pal["text_dark"])
        surface.blit(sub_surf, (BOARD_OFFSET_X, 82))

        # Score Badge
        self._draw_badge(surface, self.rect_score_badge, "SCORE", str(board.score))

        # Best Score Badge
        self._draw_badge(surface, self.rect_best_badge, "BEST", str(board.best_score))

        # Action Buttons
        # New Game Button
        self._draw_button(surface, self.rect_btn_new, "New Game", mouse_pos)

        # Undo Button (dimmed if cannot undo)
        undo_active = board.can_undo()
        self._draw_button(surface, self.rect_btn_undo, "Undo", mouse_pos, enabled=undo_active)

        # Theme Toggle Button
        theme_label = "Dark" if self.theme == THEME_LIGHT else "Light"
        self._draw_button(surface, self.rect_btn_theme, theme_label, mouse_pos)

        # Sound Toggle Button
        sound_label = "Mute" if sound_enabled else "Unmute"
        self._draw_button(surface, self.rect_btn_sound, "Snd", mouse_pos, alt_active=sound_enabled)

    def _draw_badge(self, surface: pygame.Surface, rect: pygame.Rect, title: str, value: str):
        pal = self.palette
        pygame.draw.rect(surface, pal["badge_bg"], rect, border_radius=BADGE_BORDER_RADIUS)

        t_surf = self.font_badge_title.render(title, True, pal["badge_title"])
        t_rect = t_surf.get_rect(center=(rect.centerx, rect.y + 14))
        surface.blit(t_surf, t_rect)

        v_surf = self.font_badge_val.render(value, True, pal["badge_val"])
        v_rect = v_surf.get_rect(center=(rect.centerx, rect.y + 34))
        surface.blit(v_surf, v_rect)

    def _draw_button(self, surface: pygame.Surface, rect: pygame.Rect, text: str, mouse_pos: tuple[int, int], enabled: bool = True, alt_active: bool = True):
        pal = self.palette
        is_hover = rect.collidepoint(mouse_pos) and enabled

        if not enabled:
            bg_col = (pal["button_bg"][0], pal["button_bg"][1], pal["button_bg"][2])
            alpha = 110
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*bg_col, alpha), (0, 0, rect.width, rect.height), border_radius=BUTTON_BORDER_RADIUS)
            surface.blit(s, rect.topleft)
            txt_col = (200, 200, 200)
        else:
            bg_col = pal["button_hover"] if is_hover else pal["button_bg"]
            pygame.draw.rect(surface, bg_col, rect, border_radius=BUTTON_BORDER_RADIUS)
            txt_col = pal["button_text"]

        t_surf = self.font_btn.render(text, True, txt_col)
        t_rect = t_surf.get_rect(center=rect.center)
        surface.blit(t_surf, t_rect)

    def _draw_board_grid(self, surface: pygame.Surface):
        pal = self.palette
        board_rect = pygame.Rect(BOARD_OFFSET_X, BOARD_OFFSET_Y, BOARD_WIDTH, BOARD_HEIGHT)
        pygame.draw.rect(surface, pal["board_bg"], board_rect, border_radius=BOARD_BORDER_RADIUS)

        # Empty grid cells
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cx = BOARD_OFFSET_X + GRID_GAP + c * (TILE_SIZE + GRID_GAP)
                cy = BOARD_OFFSET_Y + GRID_GAP + r * (TILE_SIZE + GRID_GAP)
                cell_rect = pygame.Rect(cx, cy, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, pal["cell_empty"], cell_rect, border_radius=TILE_BORDER_RADIUS)

    def _draw_tiles(self, surface: pygame.Surface, board: Board, anim_time: float):
        # 1. Draw dying sliding tiles first (underneath merged partners)
        for dtile in board.dying_tiles:
            self._draw_single_tile(surface, dtile, anim_time)

        # 2. Draw active board tiles
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                tile = board.tiles[r][c]
                if tile:
                    self._draw_single_tile(surface, tile, anim_time)

    def _draw_single_tile(self, surface: pygame.Surface, tile: AnimatedTile, anim_time: float):
        val = tile.value
        style = TILE_COLORS.get(val, TILE_COLORS[65536])
        bg_col = style["bg"]
        text_col = style["text"]

        scale = tile.scale
        if scale <= 0.01:
            return

        w = int(TILE_SIZE * scale)
        h = int(TILE_SIZE * scale)
        cx = tile.current_x + TILE_SIZE / 2.0
        cy = tile.current_y + TILE_SIZE / 2.0
        rect = pygame.Rect(int(cx - w / 2.0), int(cy - h / 2.0), w, h)

        # Golden radiant glow for high-tier tiles (128+)
        if style.get("glow", False):
            glow_intensity = 0.5 + 0.5 * math.sin(anim_time * 6.0) if style.get("pulse", False) else 0.8
            glow_pad = int(4 * scale)
            glow_surf = pygame.Surface((w + glow_pad * 2, h + glow_pad * 2), pygame.SRCALPHA)
            glow_alpha = int(70 * glow_intensity)
            pygame.draw.rect(
                glow_surf,
                (243, 215, 116, glow_alpha),
                (0, 0, w + glow_pad * 2, h + glow_pad * 2),
                border_radius=TILE_BORDER_RADIUS + 2
            )
            surface.blit(glow_surf, (rect.x - glow_pad, rect.y - glow_pad))

        # Main tile body
        pygame.draw.rect(surface, bg_col, rect, border_radius=TILE_BORDER_RADIUS)

        # Render value text
        val_str = str(val)
        num_digits = len(val_str)
        font = self.tile_fonts.get(min(num_digits, 6), self.tile_fonts[6])

        # If scaling is active, render at scaled font size
        txt_surf = font.render(val_str, True, text_col)
        if abs(scale - 1.0) > 0.05:
            sw = max(1, int(txt_surf.get_width() * scale))
            sh = max(1, int(txt_surf.get_height() * scale))
            txt_surf = pygame.transform.smoothscale(txt_surf, (sw, sh))

        txt_rect = txt_surf.get_rect(center=rect.center)
        surface.blit(txt_surf, txt_rect)

    def _draw_victory_overlay(self, surface: pygame.Surface):
        pal = self.palette
        board_rect = pygame.Rect(BOARD_OFFSET_X, BOARD_OFFSET_Y, BOARD_WIDTH, BOARD_HEIGHT)

        # Translucent overlay
        overlay = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
        overlay.fill((237, 194, 46, 210))  # Radiant 2048 Gold
        surface.blit(overlay, board_rect.topleft)

        # Message
        title = self.font_overlay_title.render("You Win!", True, (255, 255, 255))
        t_rect = title.get_rect(center=(board_rect.centerx, board_rect.centery - 45))
        surface.blit(title, t_rect)

        sub = self.font_overlay_sub.render("You reached 2048! Continue or start fresh?", True, (255, 255, 255))
        s_rect = sub.get_rect(center=(board_rect.centerx, board_rect.centery))
        surface.blit(sub, s_rect)

        # Action Buttons
        mouse_pos = pygame.mouse.get_pos()
        btn_keep = pygame.Rect(board_rect.centerx - 145, board_rect.centery + 35, 135, 42)
        btn_new = pygame.Rect(board_rect.centerx + 10, board_rect.centery + 35, 135, 42)

        self._draw_button(surface, btn_keep, "Keep Going", mouse_pos)
        self._draw_button(surface, btn_new, "New Game", mouse_pos)

    def _draw_game_over_overlay(self, surface: pygame.Surface):
        pal = self.palette
        board_rect = pygame.Rect(BOARD_OFFSET_X, BOARD_OFFSET_Y, BOARD_WIDTH, BOARD_HEIGHT)

        overlay = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
        overlay.fill(pal["overlay_bg"])
        surface.blit(overlay, board_rect.topleft)

        title = self.font_overlay_title.render("Game Over!", True, pal["overlay_text"])
        t_rect = title.get_rect(center=(board_rect.centerx, board_rect.centery - 35))
        surface.blit(title, t_rect)

        # Try Again button
        mouse_pos = pygame.mouse.get_pos()
        btn_retry = pygame.Rect(board_rect.centerx - 70, board_rect.centery + 25, 140, 44)
        self._draw_button(surface, btn_retry, "Try Again", mouse_pos)

    def _draw_quit_dialog(self, surface: pygame.Surface):
        # Dim full screen
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 150))
        surface.blit(dim, (0, 0))

        # Modal box
        modal_w, modal_h = 360, 180
        mx = (SCREEN_WIDTH - modal_w) // 2
        my = (SCREEN_HEIGHT - modal_h) // 2
        modal_rect = pygame.Rect(mx, my, modal_w, modal_h)

        pygame.draw.rect(surface, (250, 248, 239), modal_rect, border_radius=12)
        pygame.draw.rect(surface, (187, 173, 160), modal_rect, width=3, border_radius=12)

        title = self.font_btn.render("Are you sure you want to quit?", True, (119, 110, 101))
        surface.blit(title, title.get_rect(center=(mx + modal_w // 2, my + 45)))

        sub = self.font_subtitle.render("Your current game progress will be saved.", True, (143, 122, 102))
        surface.blit(sub, sub.get_rect(center=(mx + modal_w // 2, my + 72)))

        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        btn_yes = pygame.Rect(mx + 35, my + 110, 135, 42)
        btn_cancel = pygame.Rect(mx + 190, my + 110, 135, 42)

        self._draw_button(surface, btn_yes, "Quit (Y)", mouse_pos)
        self._draw_button(surface, btn_cancel, "Cancel (N)", mouse_pos)
