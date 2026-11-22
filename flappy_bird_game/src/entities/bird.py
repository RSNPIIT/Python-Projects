"""
bird.py - KFlapper Player Entity.
Implements authentic arcade flight dynamics, velocity-driven rotation,
triple-frame wing flap animation, procedural HD skin rendering, and collision circles.
"""

import math
import pygame
from ..config import (
    BIRD_X, BIRD_RADIUS, GRAVITY, FLAP_STRENGTH, MAX_FALL_SPEED,
    TILT_UP_SPEED, TILT_DOWN_SPEED, MAX_UPWARD_ANGLE, MAX_DOWNWARD_ANGLE,
    FALL_ROTATION_DELAY, SKINS
)


class Bird:
    """The titular flapping hero entity."""

    def __init__(self, start_x: float = BIRD_X, start_y: float = 340.0, skin_key: str = "KFlapper"):
        self.x = start_x
        self.y = start_y
        self.vy = 0.0
        self.angle = 0.0
        self.fall_timer = 0.0
        self.alive = True
        self.collided = False

        self.skin_key = skin_key
        self.skin_config = SKINS.get(skin_key, SKINS["KFlapper"])

        # Animation states: 0: Down, 1: Mid, 2: Up, 3: Mid
        self.wing_frame = 1
        self.anim_timer = 0.0
        self.anim_speed = 14.0  # Frames per second

        # Pre-render frames for current skin
        self.frames = []
        self._build_skin_frames()

    def set_skin(self, skin_key: str):
        if skin_key in SKINS:
            self.skin_key = skin_key
            self.skin_config = SKINS[skin_key]
            self._build_skin_frames()

    def _build_skin_frames(self):
        """Generates 3 crisp procedural HD animation frames for the selected skin."""
        self.frames = []
        cfg = self.skin_config
        w, h = 64, 56
        cx, cy = 30, 28

        # 3 wing positions: 0 = down, 1 = mid, 2 = up
        wing_offsets = [(cx - 10, cy + 6, 20, 14),   # Down
                        (cx - 12, cy - 2, 22, 14),   # Mid
                        (cx - 10, cy - 12, 20, 16)]  # Up

        for frame_idx in range(3):
            surf = pygame.Surface((w, h), pygame.SRCALPHA)

            # 1. Beak (Upper & Lower Mandible)
            beak_col = cfg["beak_color"]
            beak_shadow = (max(0, beak_col[0] - 50), max(0, beak_col[1] - 40), max(0, beak_col[2] - 30))
            # Lower beak
            pygame.draw.polygon(surf, beak_shadow, [(cx + 12, cy + 3), (cx + 26, cy + 8), (cx + 12, cy + 12)])
            # Upper beak
            pygame.draw.polygon(surf, beak_col, [(cx + 10, cy - 4), (cx + 28, cy + 4), (cx + 10, cy + 6)])
            pygame.draw.polygon(surf, (20, 20, 25), [(cx + 10, cy - 4), (cx + 28, cy + 4), (cx + 10, cy + 6)], 2)

            # 2. Crest (Optional Phoenix / Cyber plume)
            if cfg.get("crest"):
                plume_col = cfg["wing_color"]
                pygame.draw.polygon(surf, plume_col, [(cx - 6, cy - 18), (cx - 18, cy - 28), (cx - 2, cy - 18)])
                pygame.draw.polygon(surf, (20, 20, 25), [(cx - 6, cy - 18), (cx - 18, cy - 28), (cx - 2, cy - 18)], 2)

            # 3. Main Chubby Body
            body_col = cfg["body_color"]
            body_outline = (30, 25, 20)
            # Body drop shadow / base
            pygame.draw.ellipse(surf, body_outline, (cx - 22, cy - 19, 44, 38))
            pygame.draw.ellipse(surf, body_col, (cx - 20, cy - 17, 40, 34))

            # 4. Cream Belly
            belly_col = cfg["belly_color"]
            pygame.draw.ellipse(surf, belly_col, (cx - 10, cy - 4, 26, 20))

            # 5. Eye (Large Cartoon Sclera, Pupil & Glint)
            sclera_col = cfg["eye_sclera"]
            pupil_col = cfg["eye_pupil"]
            eye_cx, eye_cy = cx + 8, cy - 8
            # Sclera
            pygame.draw.circle(surf, body_outline, (eye_cx, eye_cy), 9)
            pygame.draw.circle(surf, sclera_col, (eye_cx, eye_cy), 8)
            # Pupil
            pygame.draw.circle(surf, pupil_col, (eye_cx + 2, eye_cy - 1), 4)
            # Specular Glint
            pygame.draw.circle(surf, (255, 255, 255), (eye_cx + 1, eye_cy - 3), 2)

            # 6. Wing with Animated Position
            wx, wy, ww, wh = wing_offsets[frame_idx]
            wing_col = cfg["wing_color"]
            wing_outline = (25, 20, 15)
            # Wing outline
            pygame.draw.ellipse(surf, wing_outline, (wx - 2, wy - 2, ww + 4, wh + 4))
            # Wing fill
            pygame.draw.ellipse(surf, wing_col, (wx, wy, ww, wh))
            # Wing feather split line
            pygame.draw.arc(surf, wing_outline, (wx + 2, wy + 2, ww - 4, wh - 4), math.pi * 0.2, math.pi * 1.2, 2)

            self.frames.append(surf)

    def flap(self):
        """Executes an upward flap impulse."""
        if not self.alive:
            return
        self.vy = FLAP_STRENGTH
        self.fall_timer = 0.0
        # Instant snap upward
        self.angle = MAX_UPWARD_ANGLE

    def update(self, dt: float, ground_y: float):
        """Simulates gravity, velocity caps, ground collision, and smooth tilt interpolation."""
        # 1. Physics: Gravity & Vertical Motion
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        self.y += self.vy

        # 2. Rotation / Attitude Dynamics
        if self.vy < 0:
            # Ascending: quickly point beak up
            self.angle = min(MAX_UPWARD_ANGLE, self.angle + TILT_UP_SPEED * dt)
            self.fall_timer = 0.0
        else:
            # Descending: delay slightly, then smoothly pitch down toward -90 deg
            self.fall_timer += dt
            if self.fall_timer > FALL_ROTATION_DELAY:
                self.angle = max(MAX_DOWNWARD_ANGLE, self.angle - TILT_DOWN_SPEED * dt)

        # 3. Wing Flapping Animation
        if self.alive:
            self.anim_timer += dt * self.anim_speed
            # Cycle 0, 1, 2, 1
            seq = [0, 1, 2, 1]
            self.wing_frame = seq[int(self.anim_timer) % len(seq)]
        else:
            # Dead/crashing: lock wing to down
            self.wing_frame = 0

        # 4. Ground Collision Check
        if self.y >= ground_y - BIRD_RADIUS:
            self.y = ground_y - BIRD_RADIUS
            self.vy = 0
            self.alive = False
            self.collided = True

        # Ceiling clamp
        if self.y < BIRD_RADIUS:
            self.y = BIRD_RADIUS
            self.vy = 0

    def draw(self, surface: pygame.Surface):
        """Renders rotated bird sprite at sub-pixel coordinates."""
        frame = self.frames[self.wing_frame]

        # Rotate around center
        rotated_surf = pygame.transform.rotate(frame, self.angle)
        rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_surf, rect)

    def get_hitbox_circle(self) -> tuple:
        """Returns (center_x, center_y, radius) for tight collision detection."""
        return self.x, self.y, BIRD_RADIUS

    def reset(self, start_x: float = BIRD_X, start_y: float = 340.0):
        self.x = start_x
        self.y = start_y
        self.vy = 0.0
        self.angle = 0.0
        self.fall_timer = 0.0
        self.alive = True
        self.collided = False
        self.wing_frame = 1
        self.anim_timer = 0.0
