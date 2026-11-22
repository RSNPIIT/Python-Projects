"""Kapman Game - Visual Renderer: 3D Beveled Egyptian Tomb & Classic Themes"""
import math
import pygame
from core.constants import (
    TILE_SIZE, MAZE_COLS, MAZE_ROWS, MAZE_WIDTH, MAZE_HEIGHT,
    TILE_WALL, TILE_PILL, TILE_ENERGIZER, TILE_GATE,
    THEME_EGYPTIAN, THEME_CLASSIC,
    EGYPT_WALL_BASE, EGYPT_WALL_LIGHT, EGYPT_WALL_DARK, EGYPT_PILL_COLOR, EGYPT_ENERGIZER_COLOR,
    CLASSIC_WALL_BASE, CLASSIC_WALL_LIGHT, CLASSIC_WALL_DARK, CLASSIC_PILL_COLOR, CLASSIC_ENERGIZER_COLOR,
    GHOST_FRIGHTENED, GHOST_EATEN, GHOST_ENTERING,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    FRIGHTENED_FLASH_TIME
)
from core.maze import Maze
from core.kapman import Kapman
from core.ghost import Ghost, GHOST_RED, GHOST_PINK, GHOST_CYAN, GHOST_ORANGE
from core.items import BonusItem, BONUS_SCARAB, BONUS_ANKH, BONUS_EYE, BONUS_RUBY

class GameRenderer:
    def __init__(self):
        self.theme = THEME_EGYPTIAN
        self._prebaked_maze_surface: pygame.Surface | None = None
        self._last_baked_theme: str | None = None

    def toggle_theme(self):
        self.theme = THEME_CLASSIC if self.theme == THEME_EGYPTIAN else THEME_EGYPTIAN
        self._prebaked_maze_surface = None

    def draw_maze(self, surface: pygame.Surface, maze: Maze, offset_y: int, anim_time: float, fright_timer: float):
        # 1. Check or bake wall background surface (for 60 FPS performance)
        if self._prebaked_maze_surface is None or self._last_baked_theme != self.theme:
            self._bake_walls(maze)

        surface.blit(self._prebaked_maze_surface, (0, offset_y))

        # 2. Draw dynamic items: Pills, Energizers, Ghost Gate
        pill_col = EGYPT_PILL_COLOR if self.theme == THEME_EGYPTIAN else CLASSIC_PILL_COLOR
        energizer_col = EGYPT_ENERGIZER_COLOR if self.theme == THEME_EGYPTIAN else CLASSIC_ENERGIZER_COLOR

        pulse = 0.5 + 0.5 * math.sin(anim_time * 8.0)
        e_radius = 5 + int(3 * pulse)

        for r in range(maze.rows):
            for c in range(maze.cols):
                tile = maze.get_tile(r, c)
                cx = int((c + 0.5) * TILE_SIZE)
                cy = int((r + 0.5) * TILE_SIZE + offset_y)

                if tile == TILE_PILL:
                    pygame.draw.circle(surface, pill_col, (cx, cy), 2)
                elif tile == TILE_ENERGIZER:
                    # Glowing pulsing sun orb
                    halo_surf = pygame.Surface((e_radius * 4, e_radius * 4), pygame.SRCALPHA)
                    pygame.draw.circle(halo_surf, (*energizer_col, 80), (e_radius * 2, e_radius * 2), e_radius + 4)
                    surface.blit(halo_surf, (cx - e_radius * 2, cy - e_radius * 2))

                    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), e_radius)
                    pygame.draw.circle(surface, energizer_col, (cx, cy), e_radius, width=2)
                elif tile == TILE_GATE:
                    # Pink/Gold ghost house gate
                    gate_col = (255, 180, 200) if self.theme == THEME_CLASSIC else (235, 195, 110)
                    gy = int((r + 0.5) * TILE_SIZE + offset_y)
                    pygame.draw.line(surface, gate_col, (c * TILE_SIZE, gy), ((c + 1) * TILE_SIZE, gy), 3)

        # 3. Draw Sarcophagus / Tomb chambers on left and right warp tunnels (Egyptian theme)
        if self.theme == THEME_EGYPTIAN:
            self._draw_sarcophagus_tunnel(surface, 0, 14, offset_y, is_left=True)
            self._draw_sarcophagus_tunnel(surface, 23, 14, offset_y, is_left=False)

    def _bake_walls(self, maze: Maze):
        """Pre-renders 3D beveled sandstone/neon maze walls onto a single cached surface."""
        surf = pygame.Surface((MAZE_WIDTH, MAZE_HEIGHT))
        surf.fill((10, 12, 18))  # Deep midnight void

        is_egypt = (self.theme == THEME_EGYPTIAN)
        wall_base = EGYPT_WALL_BASE if is_egypt else CLASSIC_WALL_BASE
        wall_light = EGYPT_WALL_LIGHT if is_egypt else CLASSIC_WALL_LIGHT
        wall_dark = EGYPT_WALL_DARK if is_egypt else CLASSIC_WALL_DARK

        for r in range(maze.rows):
            for c in range(maze.cols):
                if maze.get_tile(r, c) == TILE_WALL:
                    x = c * TILE_SIZE
                    y = r * TILE_SIZE
                    w = TILE_SIZE
                    h = TILE_SIZE

                    # Main face
                    pygame.draw.rect(surf, wall_base, (x, y, w, h))

                    # 3D Bevel Highlights: Top & Left edges
                    pygame.draw.line(surf, wall_light, (x, y), (x + w - 1, y), 2)
                    pygame.draw.line(surf, wall_light, (x, y), (x, y + h - 1), 2)

                    # 3D Bevel Shadows: Bottom & Right edges
                    pygame.draw.line(surf, wall_dark, (x, y + h - 1), (x + w - 1, y + h - 1), 2)
                    pygame.draw.line(surf, wall_dark, (x + w - 1, y), (x + w - 1, y + h - 1), 2)

                    if is_egypt:
                        # Subtle brick joint texture for ancient Egyptian sandstone
                        if (r + c) % 3 == 0:
                            pygame.draw.line(surf, wall_dark, (x + 4, y + h // 2), (x + w - 4, y + h // 2), 1)

        self._prebaked_maze_surface = surf
        self._last_baked_theme = self.theme

    def _draw_sarcophagus_tunnel(self, surface: pygame.Surface, col_start: int, row: int, offset_y: int, is_left: bool):
        """Draws the iconic Egyptian Sarcophagus entrance chamber shown in Image 1."""
        box_w = TILE_SIZE * 5
        box_h = TILE_SIZE * 3
        bx = col_start * TILE_SIZE
        by = (row - 1) * TILE_SIZE + offset_y

        # Ornate golden portal box
        pygame.draw.rect(surface, (140, 95, 30), (bx, by, box_w, box_h), border_radius=4)
        pygame.draw.rect(surface, (230, 185, 75), (bx + 2, by + 2, box_w - 4, box_h - 4), border_radius=4)
        pygame.draw.rect(surface, (180, 130, 40), (bx + 4, by + 4, box_w - 8, box_h - 8), border_radius=3)

        # Mummy relief carving inside
        relief_cx = bx + (box_w // 4 if is_left else (box_w * 3) // 4)
        relief_cy = by + box_h // 2
        # Mummy head
        pygame.draw.circle(surface, (245, 230, 190), (relief_cx, relief_cy - 8), 7)
        # Sarcophagus nemes headdress
        pygame.draw.polygon(surface, (40, 70, 160), [
            (relief_cx - 9, relief_cy - 12),
            (relief_cx + 9, relief_cy - 12),
            (relief_cx + 11, relief_cy - 3),
            (relief_cx - 11, relief_cy - 3)
        ])
        # Mummy wrapped torso
        pygame.draw.rect(surface, (230, 215, 175), (relief_cx - 7, relief_cy - 1, 14, 15), border_radius=3)
        for band_y in range(relief_cy + 2, relief_cy + 13, 3):
            pygame.draw.line(surface, (160, 130, 90), (relief_cx - 6, band_y), (relief_cx + 6, band_y), 1)

    def draw_kapman(self, surface: pygame.Surface, kapman: Kapman, offset_y: int):
        cx = int(kapman.x)
        cy = int(kapman.y + offset_y)
        r = int(TILE_SIZE * 0.65)  # 13px radius

        if kapman.dying:
            # Death dissolving spin animation
            prog = kapman.death_progress
            dissolve_r = max(1, int(r * (1.0 - prog)))
            alpha = int(255 * (1.0 - prog))
            d_surf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            rot = prog * 720.0
            pygame.draw.circle(d_surf, (255, 215, 50, alpha), (r * 2, r * 2), dissolve_r)
            surface.blit(d_surf, (cx - r * 2, cy - r * 2))
            return

        if self.theme == THEME_EGYPTIAN:
            # Explorer Kapman (Indiana style adventurer shown in Image 1)
            self._draw_explorer(surface, cx, cy, kapman)
        else:
            # Classic Yellow Chomp Kapman
            self._draw_classic_kapman(surface, cx, cy, r, kapman)

    def _draw_explorer(self, surface: pygame.Surface, cx: int, cy: int, kapman: Kapman):
        # 1. Animated walking strides
        walk_offset = int(math.sin(kapman.anim_time * 1.5) * 2) if kapman.direction != (0, 0) else 0

        # Boots & Legs
        pygame.draw.rect(surface, (45, 65, 110), (cx - 5, cy + 5, 4, 7 + walk_offset))   # Left leg
        pygame.draw.rect(surface, (45, 65, 110), (cx + 1, cy + 5, 4, 7 - walk_offset))   # Right leg
        pygame.draw.rect(surface, (40, 25, 15), (cx - 6, cy + 11 + walk_offset, 5, 3))   # Left boot
        pygame.draw.rect(surface, (40, 25, 15), (cx, cy + 11 - walk_offset, 5, 3))        # Right boot

        # Torso / Red Explorer Shirt (as in Image 1)
        pygame.draw.rect(surface, (200, 45, 55), (cx - 6, cy - 3, 12, 9), border_radius=2)
        # Belt & Buckle
        pygame.draw.rect(surface, (50, 30, 20), (cx - 6, cy + 4, 12, 2))
        pygame.draw.rect(surface, (255, 215, 60), (cx - 2, cy + 4, 4, 2))

        # Head / Face
        pygame.draw.circle(surface, (255, 215, 180), (cx, cy - 6), 6)

        # Facial eyes based on direction
        eye_ox = kapman.direction[0] * 2
        eye_oy = kapman.direction[1] * 2
        pygame.draw.circle(surface, (30, 30, 40), (cx - 2 + eye_ox, cy - 7 + eye_oy), 1)
        pygame.draw.circle(surface, (30, 30, 40), (cx + 2 + eye_ox, cy - 7 + eye_oy), 1)

        # Fedora Explorer Hat (Brown with darker crown band)
        # Brim
        pygame.draw.ellipse(surface, (125, 80, 40), (cx - 10, cy - 12, 20, 6))
        # Crown
        pygame.draw.rect(surface, (140, 90, 45), (cx - 6, cy - 17, 12, 7), border_radius=2)
        # Hatband
        pygame.draw.rect(surface, (55, 30, 15), (cx - 6, cy - 12, 12, 2))

    def _draw_classic_kapman(self, surface: pygame.Surface, cx: int, cy: int, r: int, kapman: Kapman):
        mouth_deg = kapman.mouth_angle
        rot = kapman.rotation_angle

        # Draw filled pie wedge arc
        pts = [(cx, cy)]
        start_angle = math.radians(rot + mouth_deg)
        end_angle = math.radians(rot + 360.0 - mouth_deg)
        steps = 24

        for step in range(steps + 1):
            theta = start_angle + (end_angle - start_angle) * (step / steps)
            px = cx + math.cos(theta) * r
            py = cy + math.sin(theta) * r
            pts.append((px, py))

        pygame.draw.polygon(surface, (255, 220, 30), pts)
        # Eye
        eye_angle = math.radians(rot + 75.0)
        ex = cx + math.cos(eye_angle) * (r * 0.55)
        ey = cy + math.sin(eye_angle) * (r * 0.55)
        pygame.draw.circle(surface, (20, 20, 30), (int(ex), int(ey)), 2)

    def draw_ghost(self, surface: pygame.Surface, ghost: Ghost, offset_y: int, fright_timer: float, anim_time: float):
        cx = int(ghost.x)
        cy = int(ghost.y + offset_y)
        r = int(TILE_SIZE * 0.65)

        if ghost.state in (GHOST_EATEN, GHOST_ENTERING):
            # Floating Eyes returning to tomb
            self._draw_ghost_eyes(surface, cx, cy, ghost.direction)
            return

        is_fright = (ghost.state == GHOST_FRIGHTENED)
        is_flashing = (is_fright and fright_timer <= FRIGHTENED_FLASH_TIME and int(fright_timer * 6.0) % 2 == 0)

        if self.theme == THEME_EGYPTIAN:
            self._draw_mummy(surface, cx, cy, ghost, is_fright, is_flashing, anim_time)
        else:
            self._draw_classic_ghost(surface, cx, cy, r, ghost, is_fright, is_flashing, anim_time)

    def _draw_mummy(self, surface: pygame.Surface, cx: int, cy: int, ghost: Ghost, is_fright: bool, is_flashing: bool, anim_time: float):
        """Draws the detailed animated Egyptian Mummy shown in Image 1."""
        body_col = (70, 110, 230) if is_fright else ((255, 255, 255) if is_flashing else (235, 225, 200))
        band_col = (110, 150, 255) if is_fright else ((210, 210, 230) if is_flashing else (160, 145, 120))
        sash_col = ghost.base_color if not is_fright else (40, 70, 180)

        # Animated foot shuffle
        shuffle = int(math.sin(anim_time * 8.0 + ghost.ghost_id) * 2)

        # Mummy Body Silhouette
        pygame.draw.ellipse(surface, body_col, (cx - 7, cy - 9, 14, 18))

        # Bandage Wrappings Lines
        for by in range(cy - 6, cy + 7, 3):
            pygame.draw.line(surface, band_col, (cx - 6, by), (cx + 6, by), 1)

        # Colored Hieroglyphic Sash (Akhenaten Red, Nefertiti Pink, Anubis Cyan, Horus Amber)
        pygame.draw.rect(surface, sash_col, (cx - 7, cy - 2, 14, 3))

        # Mummy Head & Wrappings
        pygame.draw.circle(surface, body_col, (cx, cy - 8), 6)
        pygame.draw.line(surface, band_col, (cx - 5, cy - 10), (cx + 5, cy - 7), 1)
        pygame.draw.line(surface, band_col, (cx - 5, cy - 6), (cx + 5, cy - 9), 1)

        # Glowing Eye Slit
        eye_y = cy - 8
        if is_fright:
            # Scared wobbly white eyes
            pygame.draw.circle(surface, (255, 255, 255), (cx - 3, eye_y), 2)
            pygame.draw.circle(surface, (255, 255, 255), (cx + 3, eye_y), 2)
            pygame.draw.circle(surface, (20, 20, 50), (cx - 3, eye_y), 1)
            pygame.draw.circle(surface, (20, 20, 50), (cx + 3, eye_y), 1)
        else:
            # Menacing glowing mummy eyes
            glow_col = (255, 230, 90) if ghost.ghost_id != GHOST_RED else (255, 70, 70)
            eye_ox = ghost.direction[0] * 2
            eye_oy = ghost.direction[1] * 2
            pygame.draw.circle(surface, glow_col, (cx - 3 + eye_ox, eye_y + eye_oy), 2)
            pygame.draw.circle(surface, glow_col, (cx + 3 + eye_ox, eye_y + eye_oy), 2)

        # Bandaged Legs
        pygame.draw.rect(surface, body_col, (cx - 5, cy + 7, 3, 5 + shuffle))
        pygame.draw.rect(surface, body_col, (cx + 2, cy + 7, 3, 5 - shuffle))

    def _draw_classic_ghost(self, surface: pygame.Surface, cx: int, cy: int, r: int, ghost: Ghost, is_fright: bool, is_flashing: bool, anim_time: float):
        color = (40, 80, 230) if is_fright else ((255, 255, 255) if is_flashing else ghost.base_color)

        # Dome head + skirt
        pygame.draw.circle(surface, color, (cx, cy - 2), r)
        skirt_rect = pygame.Rect(cx - r, cy - 2, r * 2, r)
        pygame.draw.rect(surface, color, skirt_rect)

        # Wavy bottom tentacles
        tentacle_w = (r * 2) // 3
        for i in range(3):
            tx = cx - r + i * tentacle_w + tentacle_w // 2
            ty = cy + r - 2 + int(math.sin(anim_time * 8.0 + i) * 2)
            pygame.draw.circle(surface, color, (tx, ty), tentacle_w // 2)

        # Eyes
        if is_fright:
            pygame.draw.circle(surface, (240, 240, 255), (cx - 4, cy - 3), 2)
            pygame.draw.circle(surface, (240, 240, 255), (cx + 4, cy - 3), 2)
        else:
            self._draw_ghost_eyes(surface, cx, cy, ghost.direction)

    def _draw_ghost_eyes(self, surface: pygame.Surface, cx: int, cy: int, direction: tuple[int, int]):
        eye_ox = direction[0] * 3
        eye_oy = direction[1] * 3
        # Sclera
        pygame.draw.ellipse(surface, (255, 255, 255), (cx - 7 + eye_ox, cy - 6 + eye_oy, 6, 8))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx + 1 + eye_ox, cy - 6 + eye_oy, 6, 8))
        # Pupils
        pygame.draw.circle(surface, (30, 60, 200), (cx - 4 + eye_ox, cy - 2 + eye_oy), 2)
        pygame.draw.circle(surface, (30, 60, 200), (cx + 4 + eye_ox, cy - 2 + eye_oy), 2)

    def draw_bonus_item(self, surface: pygame.Surface, item: BonusItem, offset_y: int):
        cx = int(item.x)
        cy = int(item.y + offset_y)

        # Glowing treasure pedestal
        pygame.draw.circle(surface, (180, 140, 40), (cx, cy), 11)
        pygame.draw.circle(surface, (255, 225, 75), (cx, cy), 11, width=1)

        if item.type == BONUS_SCARAB:
            # Golden Scarab Beetle
            pygame.draw.ellipse(surface, (50, 180, 120), (cx - 6, cy - 6, 12, 12))  # Emerald body
            pygame.draw.ellipse(surface, (255, 215, 50), (cx - 4, cy - 8, 8, 5))    # Golden head
            pygame.draw.line(surface, (255, 215, 50), (cx, cy - 6), (cx, cy + 5), 1)
        elif item.type == BONUS_ANKH:
            # Golden Ankh Key of Life
            pygame.draw.ellipse(surface, (255, 215, 50), (cx - 4, cy - 8, 8, 8), width=2)
            pygame.draw.line(surface, (255, 215, 50), (cx, cy), (cx, cy + 7), 2)
            pygame.draw.line(surface, (255, 215, 50), (cx - 5, cy + 2), (cx + 5, cy + 2), 2)
        elif item.type == BONUS_EYE:
            # Eye of Horus
            pygame.draw.ellipse(surface, (60, 150, 240), (cx - 7, cy - 4, 14, 8), width=2)
            pygame.draw.circle(surface, (20, 30, 60), (cx, cy), 2)
        else:
            # Royal Ruby Gem
            pygame.draw.polygon(surface, (245, 45, 70), [
                (cx, cy - 7), (cx + 7, cy - 2), (cx, cy + 7), (cx - 7, cy - 2)
            ])
