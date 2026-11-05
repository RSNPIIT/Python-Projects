"""Grid map, raycasting, and 3D-ish billboard rendering."""

from __future__ import annotations

import math
from dataclasses import dataclass

import raylib as rl

from .config import (
    BLACK,
    CLEAR,
    COLUMN_W,
    FOV,
    PROJ_PLANE,
    WHITE,
    WORLD_H,
    WORLD_W,
    angle_difference,
    clamp,
    lerp,
    mix_color,
    shade,
    smoothstep,
)
from .levels import MAP_H, MAP_W, WALL_CHARS, LevelDef, Theme


# ---------------------------------------------------------------------------
# Collision and map queries
# ---------------------------------------------------------------------------
def is_wall_char(char: str) -> bool:
    return char in WALL_CHARS


@dataclass
class RayHit:
    distance: float
    map_x: int
    map_y: int
    side: int
    wall_x: float
    wall_type: int


def cast_ray(walls: list[list[bool]], px: float, py: float, angle: float, max_distance: float = 40.0) -> RayHit:
    dir_x = math.cos(angle)
    dir_y = math.sin(angle)
    map_x = int(px)
    map_y = int(py)
    if map_y < 0 or map_y >= len(walls) or map_x < 0 or map_x >= len(walls[0]):
        return RayHit(max_distance, map_x, map_y, 0, 0.0, 1)

    delta_x = abs(1.0 / dir_x) if abs(dir_x) > 1e-9 else 1e30
    delta_y = abs(1.0 / dir_y) if abs(dir_y) > 1e-9 else 1e30

    if dir_x < 0:
        step_x = -1
        side_x = (px - map_x) * delta_x
    else:
        step_x = 1
        side_x = (map_x + 1.0 - px) * delta_x
    if dir_y < 0:
        step_y = -1
        side_y = (py - map_y) * delta_y
    else:
        step_y = 1
        side_y = (map_y + 1.0 - py) * delta_y

    side = 0
    wall_type = 1
    steps = 0
    distance = max_distance
    while steps < 256:
        steps += 1
        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            side = 0
            distance = side_x - delta_x
        else:
            side_y += delta_y
            map_y += step_y
            side = 1
            distance = side_y - delta_y
        if distance > max_distance:
            distance = max_distance
            wall_type = 1
            break
        if 0 <= map_y < len(walls) and 0 <= map_x < len(walls[0]) and walls[map_y][map_x]:
            wall_type = 1
            break
    else:
        distance = max_distance

    if side == 0:
        wall_x = py + distance * dir_y
    else:
        wall_x = px + distance * dir_x
    wall_x -= math.floor(wall_x)
    return RayHit(max(0.0001, distance), map_x, map_y, side, wall_x, wall_type)


class GameMap:
    """Parsed, queryable version of a mission's ASCII floorplan."""

    def __init__(self, level: LevelDef) -> None:
        self.level = level
        self.rows = level.rows
        self.wall_chars = [list(row) for row in self.rows]
        self.walls: list[list[bool]] = [
            [is_wall_char(char) for char in row] for row in self.rows
        ]
        self.hazards: set[tuple[int, int]] = set()
        for y, row in enumerate(self.rows):
            for x, char in enumerate(row):
                if char == "!":
                    self.hazards.add((x, y))
        self.floor_cells = [
            (x, y)
            for y in range(MAP_H)
            for x in range(MAP_W)
            if not self.walls[y][x]
        ]
        self.flow: list[list[float]] | None = None
        self.flow_origin: tuple[int, int] | None = None
        self._skyline = self._make_skyline()

    def wall_at(self, x: int, y: int) -> bool:
        if y < 0 or y >= len(self.walls) or x < 0 or x >= len(self.walls[0]):
            return True
        return self.walls[y][x]

    def wall_for_position(self, x: float, y: float) -> bool:
        return self.wall_at(int(x), int(y))

    def wall_type_at(self, x: int, y: int) -> int:
        if y < 0 or y >= len(self.wall_chars) or x < 0 or x >= len(self.wall_chars[0]):
            return 1
        return WALL_CHARS.get(self.wall_chars[y][x], 1)

    def hazard_at(self, x: float, y: float) -> bool:
        return (int(x), int(y)) in self.hazards

    def circle_collides(self, x: float, y: float, radius: float) -> bool:
        if self.wall_at(int(x), int(y)):
            return True
        samples = 8
        for index in range(samples):
            angle = index * math.tau / samples
            sx = x + math.cos(angle) * radius
            sy = y + math.sin(angle) * radius
            if self.wall_at(int(sx), int(sy)):
                return True
        # A few extra diagonal samples make wide dash movements feel solid.
        for ox, oy in ((-radius, -radius), (radius, -radius), (-radius, radius), (radius, radius)):
            if self.wall_at(int(x + ox), int(y + oy)):
                return True
        return False

    def try_move(self, x: float, y: float, dx: float, dy: float, radius: float) -> tuple[float, float]:
        # Move in small substeps so high-speed dashes do not tunnel through walls.
        distance = math.hypot(dx, dy)
        steps = max(1, int(distance / 0.12))
        step_x = dx / steps
        step_y = dy / steps
        nx, ny = x, y
        for _ in range(steps):
            if not self.circle_collides(nx + step_x, ny, radius):
                nx += step_x
            if not self.circle_collides(nx, ny + step_y, radius):
                ny += step_y
        return nx, ny

    def has_line_of_sight(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        dx = x2 - x1
        dy = y2 - y1
        distance = math.hypot(dx, dy)
        if distance < 0.001:
            return True
        hit = cast_ray(self.walls, x1, y1, math.atan2(dy, dx), distance + 0.1)
        return hit.distance >= distance - 0.03

    def clear_line(self, x1: float, y1: float, x2: float, y2: float) -> tuple[float, float] | None:
        """Return wall hit point between two positions, if any."""
        dx = x2 - x1
        dy = y2 - y1
        distance = math.hypot(dx, dy)
        if distance < 0.001:
            return None
        angle = math.atan2(dy, dx)
        hit = cast_ray(self.walls, x1, y1, angle, distance)
        if hit.distance < distance:
            return (x1 + math.cos(angle) * hit.distance, y1 + math.sin(angle) * hit.distance)
        return None

    # ------------------------------------------------------------------
    # Enemy navigation
    # ------------------------------------------------------------------
    def build_flow_field(self, target_x: float, target_y: float) -> list[list[float]]:
        tx, ty = int(target_x), int(target_y)
        if self.wall_at(tx, ty):
            tx = int(clamp(tx, 1, MAP_W - 2))
            ty = int(clamp(ty, 1, MAP_H - 2))
        infinity = 1e9
        flow = [[infinity for _ in range(MAP_W)] for _ in range(MAP_H)]
        if self.wall_at(tx, ty):
            return flow
        flow[ty][tx] = 0.0
        queue = [(tx, ty)]
        head = 0
        while head < len(queue):
            x, y = queue[head]
            head += 1
            current = flow[y][x]
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < MAP_W and 0 <= ny < MAP_H):
                    continue
                if self.walls[ny][nx] or flow[ny][nx] <= current + 1.0:
                    continue
                flow[ny][nx] = current + 1.0
                queue.append((nx, ny))
        self.flow = flow
        self.flow_origin = (tx, ty)
        return flow

    def flow_direction(self, x: float, y: float) -> tuple[float, float]:
        if self.flow is None:
            return 0.0, 0.0
        cx, cy = int(x), int(y)
        if not (0 <= cx < MAP_W and 0 <= cy < MAP_H):
            return 0.0, 0.0
        best = self.flow[cy][cx]
        best_x, best_y = cx, cy
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = cx + dx, cy + dy
            if not (0 <= nx < MAP_W and 0 <= ny < MAP_H) or self.walls[ny][nx]:
                continue
            # Do not cut diagonal corners.
            if dx and dy and (self.walls[cy][nx] or self.walls[ny][cx]):
                continue
            value = self.flow[ny][nx]
            if value < best:
                best = value
                best_x, best_y = nx, ny
        if (best_x, best_y) == (cx, cy):
            return 0.0, 0.0
        tx = best_x + 0.5
        ty = best_y + 0.5
        length = math.hypot(tx - x, ty - y)
        if length < 1e-5:
            return 0.0, 0.0
        return (tx - x) / length, (ty - y) / length

    # ------------------------------------------------------------------
    # Skyline decoration
    # ------------------------------------------------------------------
    def _make_skyline(self) -> list[tuple[float, float, float, list[tuple[float, float, float, float]]]]:
        if not self.level.theme.outdoor:
            return []
        rng = 481516
        buildings = []
        x = -520.0
        index = 0
        while x < 1500.0:
            rng = (rng * 1103515245 + 12345 + index * 97) & 0x7FFFFFFF
            width = 32 + (rng % 70)
            rng = (rng * 1103515245 + 12345 + index * 131) & 0x7FFFFFFF
            height = 35 + (rng % 150)
            windows = []
            cols = max(1, int(width // 13))
            rows = max(1, int(height // 17))
            for row in range(rows):
                for col in range(cols):
                    rng = (rng * 1103515245 + 12345 + row * 17 + col * 41 + index) & 0x7FFFFFFF
                    if rng % 10 < 3:
                        windows.append(
                            (
                                x + 5 + col * 13,
                                height - 12 - row * 17,
                                3.0,
                                5.0,
                            )
                        )
            buildings.append((x, width, float(height), windows))
            x += width + 6 + (rng % 20)
            index += 1
        return buildings

    def draw_skyline(self, renderer: "Renderer", horizon: float, angle: float) -> None:
        if not self._skyline:
            return
        theme = self.level.theme
        offset = (angle * 155.0) % 2020.0
        base = mix_color(theme.sky_low, BLACK, 0.40, 255)
        far = mix_color(theme.sky_low, BLACK, 0.56, 255)
        for index, (bx, width, height, windows) in enumerate(self._skyline):
            screen_x = bx - offset
            while screen_x < -420:
                screen_x += 2020
            while screen_x > WORLD_W + 200:
                screen_x -= 2020
            if screen_x > WORLD_W + 10 or screen_x + width < -10:
                continue
            color = base if index % 3 else far
            top = horizon - height
            rl.DrawRectangleRec((screen_x, top, width, height), color)
            # Antenna beacon and silhouette detail.
            if width > 52:
                rl.DrawRectangle(int(screen_x + width * 0.5), int(top - 14), 1, 14, color)
                if index % 4 == 0:
                    rl.DrawCircle(int(screen_x + width * 0.5), int(top - 16), 1.2, theme.accent)
            for wx, wy, ww, wh in windows:
                wx_screen = screen_x + wx
                if -4 < wx_screen < WORLD_W:
                    window_color = mix_color(theme.accent_2, theme.accent, ((int(wx) + int(wy)) % 7) / 7.0, 255)
                    window_color = shade(window_color, 0.55, 255)
                    rl.DrawRectangleRec((wx_screen, horizon - wy, ww, wh), window_color)

    def draw_indoor_ceiling(self, horizon: float, time_value: float) -> None:
        theme = self.level.theme
        # Hanging light strips create depth in the upper half of the view.
        for index in range(7):
            y = int(horizon - 18 - index * index * 5.2)
            if y < -4:
                continue
            alpha_value = max(10, 54 - index * 6)
            w = int(120 + index * 90)
            x = WORLD_W // 2 - w // 2
            rl.DrawRectangle(x, y, w, 1, (*theme.accent[:3], alpha_value))
            if index < 3:
                pulse = 0.6 + 0.4 * math.sin(time_value * 1.7 + index)
                rl.DrawCircle(WORLD_W // 2, y, 2 + pulse, (*theme.accent[:3], 80))


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------
class Renderer:
    def __init__(self, textures) -> None:
        self.textures = textures
        self.z_buffer = [1e9] * WORLD_W
        self.horizon = WORLD_H // 2

    def render(
        self,
        player,
        game_map: GameMap,
        time_value: float,
        shake: float = 0.0,
    ) -> None:
        theme = game_map.level.theme
        look_offset = player.look
        horizon = int(WORLD_H * 0.5 + look_offset + math.sin(time_value * 27.0) * shake * 18.0)
        self.horizon = horizon
        self._draw_background(player, game_map, horizon, time_value)
        self._draw_floor_grid(horizon, theme, player)
        self._draw_walls(player, game_map, horizon, time_value)

    # ------------------------------------------------------------------
    def _draw_background(self, player, game_map: GameMap, horizon: int, time_value: float) -> None:
        theme = game_map.level.theme
        # Ceiling / sky.
        if horizon > 0:
            top = max(0, horizon)
            rl.DrawRectangleGradientV(0, 0, WORLD_W, top, theme.sky_high, theme.sky_low)
        # Ground.
        if horizon < WORLD_H:
            floor_top = max(0, horizon)
            height = WORLD_H - floor_top
            if height > 0:
                rl.DrawRectangleGradientV(0, floor_top, WORLD_W, height, theme.floor_far, theme.floor_near)

        # A pair of planets/moons behind the city makes outdoor sectors feel huge.
        if theme.outdoor:
            moon_x = int(WORLD_W * 0.73 - player.angle * 55.0) % (WORLD_W + 240) - 120
            moon_y = horizon - 115
            if -60 < moon_x < WORLD_W + 60 and moon_y > -70:
                rl.BeginBlendMode(rl.BLEND_ADDITIVE)
                rl.DrawCircleGradient((moon_x, moon_y), 62, (*theme.accent_2[:3], 26), CLEAR)
                rl.EndBlendMode()
                rl.DrawCircle(moon_x, moon_y, 31, (18, 25, 46, 255))
                rl.DrawCircle(moon_x - 8, moon_y - 6, 17, (30, 42, 66, 255))
                rl.DrawCircle(moon_x + 14, moon_y + 9, 4, (25, 33, 50, 255))
            game_map.draw_skyline(self, horizon, player.angle)
        else:
            game_map.draw_indoor_ceiling(horizon, time_value)

        # Horizon haze.
        if -20 < horizon < WORLD_H + 20:
            hz = max(0, horizon - 22)
            rl.BeginBlendMode(rl.BLEND_ADDITIVE)
            rl.DrawRectangleGradientV(0, hz, WORLD_W, 44, CLEAR, (*theme.accent[:3], 22))
            rl.DrawRectangleGradientV(0, max(0, horizon - 2), WORLD_W, 4, (*theme.accent[:3], 48), CLEAR)
            rl.EndBlendMode()

    def _draw_walls(self, player, game_map: GameMap, horizon: int, time_value: float) -> None:
        theme = game_map.level.theme
        wall_textures = self.textures.walls_for(theme)
        walls = game_map.walls
        px, py = player.x, player.y
        angle = player.angle
        for screen_x in range(0, WORLD_W, COLUMN_W):
            ray_angle = angle - FOV * 0.5 + (screen_x + COLUMN_W * 0.5) / WORLD_W * FOV
            hit = cast_ray(walls, px, py, ray_angle, 42.0)
            depth = max(0.0001, hit.distance)
            line_height = WORLD_H / depth
            top = horizon - line_height * 0.5
            bottom = top + line_height
            self.z_buffer[screen_x] = depth
            if screen_x + 1 < WORLD_W:
                self.z_buffer[screen_x + 1] = depth
            if bottom < 0 or top > WORLD_H:
                continue

            wall_type = game_map.wall_type_at(hit.map_x, hit.map_y)
            texture = wall_textures.get(wall_type, wall_textures[1])
            tex_width = texture.width
            tex_height = texture.height
            wall_x = hit.wall_x
            if hit.side == 0 and math.cos(ray_angle) > 0:
                wall_x = 1.0 - wall_x
            if hit.side == 1 and math.sin(ray_angle) < 0:
                wall_x = 1.0 - wall_x
            tex_x = int(wall_x * (tex_width - 1)) % tex_width
            tex_x = max(0, min(tex_width - 1, tex_x))

            brightness = clamp(1.38 - depth * 0.040, 0.30, 1.0)
            if hit.side == 1:
                brightness *= 0.78
            fog_amount = smoothstep(2.0, 30.0, depth) * 0.55
            fog = theme.fog
            tint = (
                int((255 * (1.0 - fog_amount) + fog[0] * fog_amount) * brightness),
                int((255 * (1.0 - fog_amount) + fog[1] * fog_amount) * brightness),
                int((255 * (1.0 - fog_amount) + fog[2] * fog_amount) * brightness),
                255,
            )
            src = (tex_x, 0.0, 1.0, float(tex_height))
            dest = (screen_x, top, COLUMN_W, line_height)
            rl.DrawTexturePro(texture, src, dest, (0.0, 0.0), 0.0, tint)

            # Occasional wall highlight gives the flat raycast strips extra life.
            if depth < 8.0 and (hit.map_x * 7 + hit.map_y * 11) % 13 == 0 and screen_x % 12 == 0:
                rl.DrawRectangle(screen_x, int(top), 1, int(line_height), (*theme.accent[:3], 24))

    def _draw_floor_grid(self, horizon: int, theme: Theme, player) -> None:
        if horizon >= WORLD_H:
            return
        # Perspective floor lines.  They are intentionally subtle; the walls and
        # sprites carry most of the depth information.
        start_y = max(horizon + 3, 0)
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        for distance in range(2, 17):
            y = int(horizon + (WORLD_H * 0.5) / distance)
            if y <= horizon or y >= WORLD_H:
                continue
            alpha_value = int(clamp(45 - distance * 1.9, 5, 45))
            rl.DrawRectangle(0, y, WORLD_W, 1, (*theme.accent[:3], alpha_value))
        # Faux perspective rays anchor the floor to the vanishing point.
        for index in range(-9, 10):
            if index == 0:
                continue
            x = WORLD_W // 2 + index * 78
            rl.DrawLineEx((WORLD_W // 2, horizon + 1), (x, WORLD_H), 1.0, (*theme.accent[:3], 13))
        # Reflected floor glow just under the horizon.
        rl.DrawRectangleGradientV(0, max(0, horizon), WORLD_W, 46, (*theme.accent[:3], 12), CLEAR)
        # A soft glow at the vanishing point.
        rl.DrawCircleGradient((WORLD_W // 2, horizon), 52, (*theme.accent[:3], 18), CLEAR)
        rl.EndBlendMode()

    # ------------------------------------------------------------------
    # Billboards
    # ------------------------------------------------------------------
    def project(self, player, x: float, y: float, z: float = 0.0):
        dx = x - player.x
        dy = y - player.y
        cos_a = math.cos(player.angle)
        sin_a = math.sin(player.angle)
        depth = dx * cos_a + dy * sin_a
        if depth <= 0.08:
            return None
        lateral = -dx * sin_a + dy * cos_a
        screen_x = WORLD_W * 0.5 + (lateral / depth) * PROJ_PLANE
        line_height = WORLD_H / depth
        floor_y = self.horizon + line_height * 0.5
        screen_y = floor_y - z * line_height
        return screen_x, screen_y, depth, line_height

    def sprite_visible(self, screen_x: float, depth: float, margin: float = 0.0) -> bool:
        ix = int(screen_x)
        if ix < 0 or ix >= WORLD_W:
            return False
        return self.z_buffer[ix] + margin > depth

    def draw_sprite(
        self,
        texture,
        player,
        x: float,
        y: float,
        world_height: float,
        floor_offset: float = 0.0,
        tint=WHITE,
        alpha_value: int = 255,
        hurt_flash: float = 0.0,
    ) -> None:
        projection = self.project(player, x, y, 0.0)
        if projection is None:
            return
        screen_x, floor_y, depth, line_height = projection
        if screen_x < -300 or screen_x > WORLD_W + 300:
            return
        height_px = line_height * world_height
        width_px = height_px * texture.width / texture.height
        top = floor_y - height_px - floor_offset * line_height
        left = screen_x - width_px * 0.5
        right = screen_x + width_px * 0.5
        if right < 1 or left > WORLD_W - 1 or height_px < 1:
            return

        brightness = clamp(1.08 - depth * 0.035, 0.34, 1.0)
        color = tint
        r = int(clamp(color[0] * brightness, 0, 255))
        g = int(clamp(color[1] * brightness, 0, 255))
        b = int(clamp(color[2] * brightness, 0, 255))
        if hurt_flash > 0:
            flash = clamp(hurt_flash, 0.0, 1.0)
            r = int(lerp(r, 255, flash))
            g = int(lerp(g, 244, flash))
            b = int(lerp(b, 220, flash))
        draw_color = (r, g, b, alpha_value)

        x0 = max(0, int(math.floor(left)))
        x1 = min(WORLD_W, int(math.ceil(right)))
        run_start = None
        for ix in range(x0, x1 + 1):
            visible = ix < x1 and self.z_buffer[ix] + 0.025 > depth
            if visible and run_start is None:
                run_start = ix
            elif not visible and run_start is not None:
                self._draw_sprite_run(texture, run_start, ix, left, right, width_px, top, height_px, draw_color)
                run_start = None
        if run_start is not None:
            self._draw_sprite_run(texture, run_start, x1, left, right, width_px, top, height_px, draw_color)

    def _draw_sprite_run(
        self,
        texture,
        start: int,
        end: int,
        left: float,
        right: float,
        width_px: float,
        top: float,
        height_px: float,
        color,
    ) -> None:
        if end <= start:
            return
        uv_start = clamp((start - left) / max(width_px, 1e-6), 0.0, 1.0)
        uv_end = clamp((end - left) / max(width_px, 1e-6), 0.0, 1.0)
        src_x = uv_start * texture.width
        src_w = max(0.5, (uv_end - uv_start) * texture.width)
        src = (src_x, 0.0, src_w, float(texture.height))
        dest = (float(start), top, float(end - start), height_px)
        rl.DrawTexturePro(texture, src, dest, (0.0, 0.0), 0.0, color)

    def draw_shadow(self, player, x: float, y: float, radius: float = 0.28) -> None:
        projection = self.project(player, x, y, 0.0)
        if projection is None:
            return
        screen_x, floor_y, depth, line_height = projection
        if not self.sprite_visible(screen_x, depth, 0.2):
            return
        rx = radius * line_height
        ry = max(1.0, rx * 0.24)
        rl.DrawEllipseV((screen_x, floor_y), rx, ry, (0, 0, 0, 105))

    def draw_particle(self, player, x: float, y: float, z: float, size: float, color) -> None:
        projection = self.project(player, x, y, z)
        if projection is None:
            return
        screen_x, screen_y, depth, line_height = projection
        if not self.sprite_visible(screen_x, depth, 0.1):
            return
        radius = max(0.6, size * line_height * 0.08)
        rl.DrawCircleV((screen_x, screen_y), radius, color)
        if radius > 2:
            rl.DrawCircleV((screen_x + 1, screen_y - 1), radius * 0.45, (255, 245, 220, color[3] // 2))

    def draw_glow_point(self, player, x: float, y: float, z: float, radius: float, color) -> None:
        projection = self.project(player, x, y, z)
        if projection is None:
            return
        screen_x, screen_y, depth, line_height = projection
        if not self.sprite_visible(screen_x, depth, 0.1):
            return
        r = max(2.0, radius * line_height * 0.08)
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        rl.DrawCircleGradient((screen_x, screen_y), r, color, CLEAR)
        rl.EndBlendMode()

    def draw_portal(self, player, x: float, y: float, time_value: float, active: bool, color) -> None:
        projection = self.project(player, x, y, 0.0)
        if projection is None:
            return
        screen_x, floor_y, depth, line_height = projection
        if not self.sprite_visible(screen_x, depth, 0.25):
            return
        base = max(6.0, line_height * 0.17)
        pulse = 0.5 + 0.5 * math.sin(time_value * 3.2)
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        if active:
            rl.DrawCircleGradient((screen_x, floor_y - line_height * 0.42), base * 3.8, (*color[:3], 38), CLEAR)
            # Energy column.
            rl.DrawRectangleGradientV(
                int(screen_x - base),
                int(floor_y - line_height * 1.35),
                max(1, int(base * 2)),
                max(1, int(line_height * 1.35)),
                (*color[:3], 55),
                (*color[:3], 6),
            )
        else:
            rl.DrawCircleGradient((screen_x, floor_y - line_height * 0.2), base * 2.6, (110, 110, 120, 15), CLEAR)
        for index in range(3):
            ring_pulse = (time_value * 0.85 + index * 0.33) % 1.0
            alpha_value = int((1.0 - ring_pulse) * (100 if active else 32))
            radius_x = base * (1.5 + ring_pulse * 2.4 + pulse * 0.2)
            radius_y = radius_x * 0.32
            center_y = floor_y - line_height * (0.12 + ring_pulse * 0.7)
            rl.DrawEllipseLines(
                int(screen_x),
                int(center_y),
                int(radius_x),
                int(radius_y),
                (*color[:3], alpha_value),
            )
        if active:
            for index in range(7):
                angle = time_value * 1.5 + index * math.tau / 7
                px = screen_x + math.cos(angle) * base * 2.1
                py = floor_y - line_height * 0.55 + math.sin(angle) * base * 0.75
                rl.DrawCircleV((px, py), max(1.0, base * 0.13), (*color[:3], 150))
        rl.EndBlendMode()

    def draw_muzzle_light(self, player, x: float, y: float, color) -> None:
        projection = self.project(player, x, y, 0.5)
        if projection is None:
            return
        screen_x, screen_y, depth, line_height = projection
        if not self.sprite_visible(screen_x, depth):
            return
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        rl.DrawCircleGradient((screen_x, screen_y), max(12.0, line_height * 0.5), (*color[:3], 40), CLEAR)
        rl.EndBlendMode()
