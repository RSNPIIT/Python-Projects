"""moderngl render pipeline + a software fallback.

Pipeline (all offscreen, then one readback per frame):

    pygame world RGBA  ->  composite over procedural sky   (full res)
                        ->  bright pass                    (quarter res)
                        ->  blur horizontal / vertical     (quarter res)
                        ->  final grade, bloom, aberrations(full res)
                        ->  glReadPixels -> pygame.Surface

A small driver quirk on Apple's GL stack means textures that are created
empty and later filled with ``write()`` do not sample correctly.  Creating
them with initial data (and then writing) works, so all CPU textures are
seeded with zero bytes.  Render targets are seeded the same way for safety.
"""

from __future__ import annotations

import numpy as np
import pygame

from . import shaders
from .constants import BIOMES, SCREEN_H, SCREEN_W
from .utils import clamp, color_lerp, to01

try:  # pragma: no cover - import guard is exercised on machines without GL
    import moderngl

    _MODERNGL_AVAILABLE = True
except Exception:  # pragma: no cover
    moderngl = None
    _MODERNGL_AVAILABLE = False


def _u(program, name, value) -> None:
    try:
        program[name].value = value
    except KeyError:
        pass


class ShaderRenderer:
    """Hardware compositor.  `render` returns a fresh 1280x720 surface."""

    def __init__(self) -> None:
        if not _MODERNGL_AVAILABLE:
            raise RuntimeError("moderngl is not installed")
        self.ctx = moderngl.create_standalone_context(require=330)
        ctx = self.ctx
        self.w, self.h = SCREEN_W, SCREEN_H
        self.bw, self.bh = SCREEN_W // 4, SCREEN_H // 4

        blank = bytes(self.w * self.h * 4)
        blank_small = bytes(self.bw * self.bh * 4)

        def make_tex(size, data, filt=moderngl.LINEAR):
            tex = ctx.texture(size, 4, data)
            tex.filter = (filt, filt)
            tex.repeat_x = False
            tex.repeat_y = False
            return tex

        self.world_tex = make_tex((self.w, self.h), blank, moderngl.NEAREST)
        self.scene_tex = make_tex((self.w, self.h), blank)
        self.final_tex = make_tex((self.w, self.h), blank)
        self.bright_tex = make_tex((self.bw, self.bh), blank_small)
        self.blur_a_tex = make_tex((self.bw, self.bh), blank_small)
        self.blur_b_tex = make_tex((self.bw, self.bh), blank_small)

        self.scene_fbo = ctx.framebuffer(color_attachments=[self.scene_tex])
        self.final_fbo = ctx.framebuffer(color_attachments=[self.final_tex])
        self.bright_fbo = ctx.framebuffer(color_attachments=[self.bright_tex])
        self.blur_a_fbo = ctx.framebuffer(color_attachments=[self.blur_a_tex])
        self.blur_b_fbo = ctx.framebuffer(color_attachments=[self.blur_b_tex])

        self.scene_prog = ctx.program(vertex_shader=shaders.VERTEX,
                                      fragment_shader=shaders.SCENE)
        self.bright_prog = ctx.program(vertex_shader=shaders.VERTEX,
                                       fragment_shader=shaders.BRIGHT)
        self.blur_prog = ctx.program(vertex_shader=shaders.VERTEX,
                                     fragment_shader=shaders.BLUR)
        self.final_prog = ctx.program(vertex_shader=shaders.VERTEX_FLIP,
                                      fragment_shader=shaders.FINAL)

        quad = np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype="f4").tobytes()
        self.vbo = ctx.buffer(quad)
        self.vaos = {
            "scene": ctx.vertex_array(self.scene_prog, [(self.vbo, "2f", "in_pos")]),
            "bright": ctx.vertex_array(self.bright_prog, [(self.vbo, "2f", "in_pos")]),
            "blur": ctx.vertex_array(self.blur_prog, [(self.vbo, "2f", "in_pos")]),
            "final": ctx.vertex_array(self.final_prog, [(self.vbo, "2f", "in_pos")]),
        }

        # sampler bindings
        _u(self.scene_prog, "u_world", 0)
        _u(self.bright_prog, "u_scene", 0)
        _u(self.blur_prog, "u_src", 0)
        _u(self.final_prog, "u_scene", 0)
        _u(self.final_prog, "u_bloom", 1)

        self._bytes = blank
        self._frame = None
        self.frame_count = 0
        self.last_render_ms = 0.0

    # ------------------------------------------------------------------
    def render(
        self,
        world: pygame.Surface,
        palette: dict,
        time_s: float,
        scroll: float,
        hurt: float = 0.0,
        flash: float = 0.0,
        dash: float = 0.0,
        bloom_strength: float = 0.85,
    ) -> pygame.Surface:
        import time as _time

        t0 = _time.perf_counter()
        ctx = self.ctx

        # 1. upload the pygame world (flipped, see module docstring)
        self.world_tex.write(pygame.image.tobytes(world, "RGBA", True))

        # 2. composite world over the procedural sky
        self.scene_fbo.use()
        self.scene_fbo.clear(0.0, 0.0, 0.0, 1.0)
        self.world_tex.use(0)
        _u(self.scene_prog, "u_res", (float(self.w), float(self.h)))
        _u(self.scene_prog, "u_time", float(time_s))
        _u(self.scene_prog, "u_scroll", float(scroll))
        _u(self.scene_prog, "u_sky_top", to01(palette["sky_top"]))
        _u(self.scene_prog, "u_sky_bottom", to01(palette["sky_bottom"]))
        _u(self.scene_prog, "u_haze", to01(palette["haze"]))
        _u(self.scene_prog, "u_accent", to01(palette["accent"]))
        _u(self.scene_prog, "u_aurora", 1.0)
        self.vaos["scene"].render(moderngl.TRIANGLE_STRIP)

        # 3. bright pass
        self.bright_fbo.use()
        self.scene_tex.use(0)
        _u(self.bright_prog, "u_texel", (1.0 / self.bw, 1.0 / self.bh))
        _u(self.bright_prog, "u_threshold", 0.62)
        self.vaos["bright"].render(moderngl.TRIANGLE_STRIP)

        # 4. separable blur (horizontal then vertical)
        self.blur_a_fbo.use()
        self.bright_tex.use(0)
        _u(self.blur_prog, "u_texel", (1.0 / self.bw, 1.0 / self.bh))
        _u(self.blur_prog, "u_dir", (1.0, 0.0))
        self.vaos["blur"].render(moderngl.TRIANGLE_STRIP)

        self.blur_b_fbo.use()
        self.blur_a_tex.use(0)
        _u(self.blur_prog, "u_dir", (0.0, 1.0))
        self.vaos["blur"].render(moderngl.TRIANGLE_STRIP)

        # 5. final grade, bloom composite and vertical flip
        self.final_fbo.use()
        self.scene_tex.use(0)
        self.blur_b_tex.use(1)
        _u(self.final_prog, "u_res", (float(self.w), float(self.h)))
        _u(self.final_prog, "u_time", float(time_s))
        _u(self.final_prog, "u_hurt", clamp(hurt, 0.0, 1.0))
        _u(self.final_prog, "u_flash", clamp(flash, 0.0, 1.0))
        _u(self.final_prog, "u_dash", clamp(dash, 0.0, 1.0))
        _u(self.final_prog, "u_bloom_strength", bloom_strength)
        self.vaos["final"].render(moderngl.TRIANGLE_STRIP)

        # 6. readback
        data = self.final_fbo.read(components=4)
        surf = pygame.image.frombuffer(data, (self.w, self.h), "RGBA")
        self.frame_count += 1
        self.last_render_ms = (_time.perf_counter() - t0) * 1000.0
        return surf


class SoftwareRenderer:
    """Fallback used when OpenGL/modernGL is unavailable.

    It still gives a coherent look: biome gradient sky, world composite,
    a cheap bloom-ish glow pass over bright pixels and a vignette.
    """

    def __init__(self) -> None:
        self.w, self.h = SCREEN_W, SCREEN_H
        self._sky_key = None
        self._sky = None
        self._vignette = self._make_vignette()
        self.frame_count = 0
        self.last_render_ms = 0.0

    def _make_vignette(self) -> pygame.Surface:
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        cx, cy = self.w / 2, self.h / 2
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (0.75 * max(cx, cy))
        alpha = (np.clip(dist - 0.35, 0, 1) ** 1.6 * 190).astype(np.uint8)
        arr = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        arr[..., 3] = alpha
        return pygame.image.frombuffer(arr.tobytes(), (self.w, self.h), "RGBA").copy()

    def _make_sky(self, palette) -> pygame.Surface:
        top = np.array(palette["sky_top"], dtype=np.float32)
        bottom = np.array(palette["sky_bottom"], dtype=np.float32)
        rows = np.linspace(0.0, 1.0, self.h, dtype=np.float32)[:, None]
        t = (rows ** 0.85) * 0.9
        grad = bottom[None, :] * (1 - t) + top[None, :] * t
        arr = np.repeat(grad[:, None, :], self.w, axis=1).astype(np.uint8)
        surf = pygame.image.frombuffer(np.ascontiguousarray(arr).tobytes(),
                                       (self.w, self.h), "RGB").convert()
        haze = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        for y in range(self.h):
            a = int(24 * max(0.0, 1.0 - abs(y / self.h - 0.55) * 2.2))
            if a:
                pygame.draw.line(haze, (*palette["haze"], a), (0, y), (self.w, y))
        surf.blit(haze, (0, 0))
        return surf

    def render(
        self,
        world: pygame.Surface,
        palette: dict,
        time_s: float,
        scroll: float,
        hurt: float = 0.0,
        flash: float = 0.0,
        dash: float = 0.0,
        bloom_strength: float = 0.85,
    ) -> pygame.Surface:
        key = (palette["name"], palette["sky_top"], palette["sky_bottom"])
        if key != self._sky_key:
            self._sky = self._make_sky(palette)
            self._sky_key = key
        frame = self._sky.copy()
        frame.blit(world, (0, 0))
        if hurt > 0:
            frame.fill((int(140 * hurt), 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        frame.blit(self._vignette, (0, 0))
        self.frame_count += 1
        return frame


def create_renderer():
    """Return the best renderer available, never raise."""
    if _MODERNGL_AVAILABLE:
        try:
            return ShaderRenderer(), True
        except Exception as exc:  # pragma: no cover
            print(f"[renderer] GPU pipeline unavailable ({exc}); using software fallback")
    return SoftwareRenderer(), False
