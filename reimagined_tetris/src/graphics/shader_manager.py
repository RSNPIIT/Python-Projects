"""
shader_manager.py - ModernGL Post-Processing Pipeline & Fallback Renderer.
Features: Dynamic Bloom, Chromatic Aberration Shockwaves, CRT Scanlines & Vignette.
"""

import array
import pygame


class ShaderManager:
    def __init__(self, width, height, use_opengl=True):
        self.width = width
        self.height = height
        self.use_opengl = use_opengl
        self.ctx = None
        self.program = None
        self.vbo = None
        self.vao = None
        self.texture = None

        # Shader toggles & uniforms
        self.enable_bloom = True
        self.enable_scanlines = True
        self.chromatic_intensity = 0.0
        self.shockwave_intensity = 0.0

        if self.use_opengl:
            self._init_opengl()

    def _init_opengl(self):
        try:
            import moderngl
            self.ctx = moderngl.create_context(require=330)

            vert_shader = """
            #version 330 core
            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 uv;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                uv = in_uv;
            }
            """

            frag_shader = """
            #version 330 core
            in vec2 uv;
            out vec4 fragColor;
            uniform sampler2D tex;
            uniform float time;
            uniform float shockwave;
            uniform float chromatic;
            uniform int enable_scanlines;
            uniform int enable_bloom;

            void main() {
                vec2 st = uv;

                // Shockwave distortion
                if (shockwave > 0.001) {
                    vec2 center = vec2(0.5, 0.5);
                    vec2 dir = st - center;
                    float dist = length(dir);
                    float wave = sin(dist * 25.0 - time * 12.0) * shockwave * 0.012;
                    st += normalize(dir) * wave;
                }

                // Chromatic aberration on impact
                vec2 offset = vec2(chromatic * 0.006, 0.0);
                float r = texture(tex, st + offset).r;
                float g = texture(tex, st).g;
                float b = texture(tex, st - offset).b;
                float a = texture(tex, st).a;
                vec4 col = vec4(r, g, b, a);

                // Bloom glow approximation for neon elements
                if (enable_bloom == 1) {
                    vec4 glow = vec4(0.0);
                    float blur = 0.0022;
                    glow += texture(tex, st + vec2(-blur, -blur)) * 0.20;
                    glow += texture(tex, st + vec2(blur, -blur)) * 0.20;
                    glow += texture(tex, st + vec2(-blur, blur)) * 0.20;
                    glow += texture(tex, st + vec2(blur, blur)) * 0.20;
                    glow += texture(tex, st + vec2(0.0, -blur * 1.5)) * 0.10;
                    glow += texture(tex, st + vec2(0.0, blur * 1.5)) * 0.10;
                    col += max(glow - 0.22, 0.0) * 1.4;
                }

                // CRT Scanlines
                if (enable_scanlines == 1) {
                    float sl = sin(st.y * 700.0) * 0.035;
                    col.rgb -= sl;
                }

                // Soft cinematic vignette
                float dist = distance(st, vec2(0.5));
                col.rgb *= smoothstep(0.88, 0.35, dist);

                fragColor = col;
            }
            """

            self.program = self.ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)

            # Fullscreen Quad: (x, y, u, v)
            quad_data = array.array('f', [
                -1.0, -1.0,  0.0, 0.0,
                 1.0, -1.0,  1.0, 0.0,
                -1.0,  1.0,  0.0, 1.0,
                 1.0,  1.0,  1.0, 1.0,
            ])
            self.vbo = self.ctx.buffer(quad_data)
            self.vao = self.ctx.vertex_array(
                self.program,
                [(self.vbo, '2f 2f', 'in_vert', 'in_uv')],
            )
            self.texture = self.ctx.texture((self.width, self.height), 4)
            self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            self.use_opengl = True
        except Exception as e:
            print(f"[ShaderManager] ModernGL initialization note: {e}. Falling back to software renderer.")
            self.use_opengl = False

    def trigger_impact(self, shockwave=0.4, chromatic=0.6):
        self.shockwave_intensity = max(self.shockwave_intensity, shockwave)
        self.chromatic_intensity = max(self.chromatic_intensity, chromatic)

    def update(self, dt):
        if self.shockwave_intensity > 0:
            self.shockwave_intensity = max(0.0, self.shockwave_intensity - dt * 2.8)
        if self.chromatic_intensity > 0:
            self.chromatic_intensity = max(0.0, self.chromatic_intensity - dt * 3.2)

    def render(self, surface, time_sec=0.0):
        if not self.use_opengl or self.ctx is None:
            # Software fallback
            pygame.display.flip()
            return

        # Upload surface to OpenGL texture
        raw_bytes = pygame.image.tobytes(surface, 'RGBA', True)
        self.texture.write(raw_bytes)
        self.texture.use(location=0)

        self.program['tex'].value = 0
        self.program['time'].value = float(time_sec)
        self.program['shockwave'].value = float(self.shockwave_intensity)
        self.program['chromatic'].value = float(self.chromatic_intensity)
        self.program['enable_scanlines'].value = 1 if self.enable_scanlines else 0
        self.program['enable_bloom'].value = 1 if self.enable_bloom else 0

        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.vao.render(mode=5)  # TRIANGLE_STRIP
        pygame.display.flip()
