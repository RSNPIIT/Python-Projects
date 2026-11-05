"""GLSL sources for the procedural sky, bloom chain and post processing.

The world itself is drawn by pygame into an RGBA surface.  That surface is
uploaded as a texture and composited over a fully procedural sky, then the
result goes through a bright-pass / separable-blur bloom chain and a final
grade with chromatic aberration, vignette and film grain.

The final pass flips the geometry on the Y axis.  This cancels the vertical
flip introduced by reading a framebuffer back into a top-down pygame surface.
"""

from __future__ import annotations

VERTEX = """#version 330
in vec2 in_pos;
out vec2 uv;
void main() {
    uv = in_pos * 0.5 + 0.5;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
"""

# Same as VERTEX but flips the output vertically for the final readback.
VERTEX_FLIP = """#version 330
in vec2 in_pos;
out vec2 uv;
void main() {
    uv = in_pos * 0.5 + 0.5;
    gl_Position = vec4(in_pos.x, -in_pos.y, 0.0, 1.0);
}
"""

COMMON_NOISE = """
float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float vnoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash21(i);
    float b = hash21(i + vec2(1.0, 0.0));
    float c = hash21(i + vec2(0.0, 1.0));
    float d = hash21(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    for (int i = 0; i < 5; i++) {
        v += a * vnoise(p);
        p = p * 2.03 + vec2(17.1, 9.2);
        a *= 0.5;
    }
    return v;
}
"""

SCENE = """#version 330
in vec2 uv;
out vec4 frag;

uniform sampler2D u_world;
uniform vec2 u_res;
uniform float u_time;
uniform float u_scroll;
uniform vec3 u_sky_top;
uniform vec3 u_sky_bottom;
uniform vec3 u_haze;
uniform vec3 u_accent;
uniform float u_aurora;

""" + COMMON_NOISE + """

void main() {
    vec2 p = uv;
    vec3 sky = mix(u_sky_bottom, u_sky_top, smoothstep(0.0, 1.0, p.y));

    // low haze hugging the horizon
    sky += u_haze * 0.22 * exp(-abs(p.y - 0.30) * 5.5);

    // aurora ribbons
    vec2 q = vec2(p.x * 2.7 + u_scroll * 0.00020, p.y * 1.45 - u_time * 0.010);
    float drift = fbm(q * 0.7 + vec2(u_time * 0.012, 0.0));
    float flow = fbm(q * 1.5 + vec2(drift * 0.9, 0.0));
    float ribbon = smoothstep(0.48, 0.76, flow)
                 * smoothstep(0.02, 0.38, p.y)
                 * (1.0 - smoothstep(0.66, 1.0, p.y));
    vec3 aurora_col = mix(u_accent, u_haze * 1.8 + u_accent * 0.30, 0.35);
    sky += aurora_col * ribbon * 0.30 * u_aurora;

    // fine stars, brighter overhead
    vec2 sp = p * vec2(u_res.x / u_res.y, 1.0) * 115.0;
    vec2 cell = floor(sp);
    vec2 fp = fract(sp) - 0.5;
    float h = hash21(cell);
    float star = smoothstep(0.13, 0.0, length(fp)) * smoothstep(0.982, 0.999, h);
    star *= 0.55 + 0.45 * sin(u_time * 2.1 + h * 57.0);
    sky += vec3(0.82, 0.90, 1.0) * star * (0.30 + 0.70 * p.y) * 0.95;

    // distant nebula wisps
    float wisp = fbm(p * vec2(3.0, 2.1) + vec2(u_scroll * 0.00035, -u_time * 0.007));
    sky += u_haze * smoothstep(0.46, 0.92, wisp) * 0.11;

    // faint vignette in the sky keeps the edges moody
    sky *= mix(1.0, 0.72, smoothstep(0.55, 1.05, distance(p, vec2(0.5, 0.55))));

    // dithering to kill banding in the dark gradients
    sky += (hash21(p * u_res + fract(u_time) * 17.0) - 0.5) / 255.0;

    // pygame stores straight (non-premultiplied) alpha, so a plain mix keeps
    // antialiased glyphs and soft glows clean.
    vec4 world = texture(u_world, p);
    vec3 color = mix(sky, world.rgb, world.a);
    frag = vec4(color, 1.0);
}
"""

BRIGHT = """#version 330
in vec2 uv;
out vec4 frag;

uniform sampler2D u_scene;
uniform vec2 u_texel;
uniform float u_threshold;

void main() {
    // Small 4-tap box downsample keeps thin glows alive.
    vec2 o = u_texel * 0.5;
    vec3 c = texture(u_scene, uv + vec2(-o.x, -o.y)).rgb;
    c += texture(u_scene, uv + vec2( o.x, -o.y)).rgb;
    c += texture(u_scene, uv + vec2(-o.x,  o.y)).rgb;
    c += texture(u_scene, uv + vec2( o.x,  o.y)).rgb;
    c *= 0.25;
    float luma = dot(c, vec3(0.2126, 0.7152, 0.0722));
    float k = smoothstep(u_threshold, u_threshold + 0.30, luma);
    frag = vec4(c * k, 1.0);
}
"""

BLUR = """#version 330
in vec2 uv;
out vec4 frag;

uniform sampler2D u_src;
uniform vec2 u_texel;
uniform vec2 u_dir;

void main() {
    vec2 o = u_texel * u_dir;
    vec3 c = texture(u_src, uv).rgb * 0.227027;
    c += texture(u_src, uv + o * 1.3846).rgb * 0.3162162;
    c += texture(u_src, uv - o * 1.3846).rgb * 0.3162162;
    c += texture(u_src, uv + o * 3.2308).rgb * 0.0702703;
    c += texture(u_src, uv - o * 3.2308).rgb * 0.0702703;
    frag = vec4(c, 1.0);
}
"""

FINAL = """#version 330
in vec2 uv;
out vec4 frag;

uniform sampler2D u_scene;
uniform sampler2D u_bloom;
uniform vec2 u_res;
uniform float u_time;
uniform float u_hurt;
uniform float u_flash;
uniform float u_dash;
uniform float u_bloom_strength;

""" + COMMON_NOISE + """

void main() {
    vec2 p = uv;
    vec2 d = p - 0.5;
    float r2 = dot(d, d);

    // radial warp on damage
    vec2 sp = p + d * (u_hurt * 0.045) * (0.35 + r2);

    // chromatic aberration, stronger while hurt / dashing
    float ca = 0.0010 + u_hurt * 0.0045 + u_dash * 0.0022;
    vec3 col;
    col.r = texture(u_scene, sp + d * ca).r;
    col.g = texture(u_scene, sp).g;
    col.b = texture(u_scene, sp - d * ca).b;

    vec3 bloom = texture(u_bloom, sp).rgb;
    col += bloom * u_bloom_strength;

    // dash speed smear
    if (u_dash > 0.002) {
        vec2 dir = normalize(d + vec2(1e-5));
        vec3 smear = vec3(0.0);
        for (int i = 1; i <= 4; i++) {
            smear += texture(u_scene, p - dir * (float(i) * 0.007 * u_dash)).rgb;
        }
        col += smear * 0.045 * u_dash;
    }

    // filmic-ish curve and split tone
    col = pow(max(col, vec3(0.0)), vec3(0.94));
    float luma = dot(col, vec3(0.299, 0.587, 0.114));
    vec3 cool = col * vec3(0.92, 0.98, 1.07);
    vec3 warm = col * vec3(1.07, 1.00, 0.93);
    col = mix(cool, warm, smoothstep(0.18, 0.82, luma));

    // vignette
    float vig = smoothstep(0.98, 0.22, length(d) * 1.12);
    col *= mix(1.0, vig, 0.62);

    // film grain + subtle scanline
    float grain = hash21(p * u_res + fract(u_time) * 91.7);
    col += (grain - 0.5) * 0.032;
    col *= 1.0 - 0.022 * (0.5 + 0.5 * sin(p.y * u_res.y * 3.14159));

    // damage flash and pickup flash
    col = mix(col, vec3(1.0, 0.12, 0.18), u_hurt * 0.20);
    col += u_flash * vec3(1.0, 0.95, 0.82) * 0.35;

    frag = vec4(col, 1.0);
}
"""
