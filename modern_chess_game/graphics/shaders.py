"""Modern Chess Game - GLSL Shaders for ModernGL (OpenGL 3.3 Core)"""

# 1. Textured Quad / Piece Shader with Soft Drop Shadow & Alpha Blending
TEXTURED_QUAD_VS = """
#version 330 core
layout (location = 0) in vec2 in_pos;
layout (location = 1) in vec2 in_uv;

uniform vec2 u_resolution;
uniform vec2 u_position;
uniform vec2 u_size;

out vec2 v_uv;

void main() {
    // Transform pixel coordinates to NDC [-1, 1]
    vec2 pixel_pos = u_position + in_pos * u_size;
    vec2 ndc = (pixel_pos / u_resolution) * 2.0 - 1.0;
    ndc.y = -ndc.y; // Flip Y for top-left origin
    gl_Position = vec4(ndc, 0.0, 1.0);
    v_uv = in_uv;
}
"""

TEXTURED_QUAD_FS = """
#version 330 core
in vec2 v_uv;
out vec4 frag_color;

uniform sampler2D u_texture;
uniform vec4 u_tint;
uniform float u_opacity;
uniform bool u_is_shadow;

void main() {
    vec4 tex = texture(u_texture, v_uv);
    if (u_is_shadow) {
        // Render soft black drop shadow based on texture alpha
        frag_color = vec4(0.0, 0.0, 0.0, tex.a * 0.35 * u_opacity);
    } else {
        frag_color = vec4(tex.rgb * u_tint.rgb, tex.a * u_tint.a * u_opacity);
    }
}
"""

# 2. Solid Color & Rounded Rectangle Shader for Board and UI
RECT_VS = """
#version 330 core
layout (location = 0) in vec2 in_pos;

uniform vec2 u_resolution;
uniform vec2 u_position;
uniform vec2 u_size;

out vec2 v_local_pos;

void main() {
    vec2 pixel_pos = u_position + in_pos * u_size;
    vec2 ndc = (pixel_pos / u_resolution) * 2.0 - 1.0;
    ndc.y = -ndc.y;
    gl_Position = vec4(ndc, 0.0, 1.0);
    v_local_pos = in_pos * u_size;
}
"""

RECT_FS = """
#version 330 core
in vec2 v_local_pos;
out vec4 frag_color;

uniform vec2 u_size;
uniform vec4 u_color;
uniform float u_radius;
uniform vec4 u_border_color;
uniform float u_border_width;

// Signed distance field for rounded box
float rounded_box_sdf(vec2 center_pos, vec2 half_size, float radius) {
    vec2 d = abs(center_pos) - half_size + vec2(radius);
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0)) - radius;
}

void main() {
    vec2 half_size = u_size * 0.5;
    vec2 center_pos = v_local_pos - half_size;
    float dist = rounded_box_sdf(center_pos, half_size, u_radius);

    // Antialiased edge
    float alpha = 1.0 - smoothstep(-0.8, 0.8, dist);

    if (u_border_width > 0.0) {
        float border_dist = dist + u_border_width;
        float border_factor = smoothstep(-0.8, 0.8, border_dist);
        vec4 col = mix(u_color, u_border_color, border_factor);
        frag_color = vec4(col.rgb, col.a * alpha);
    } else {
        frag_color = vec4(u_color.rgb, u_color.a * alpha);
    }
}
"""

# 3. Move Indicators & Glow Rings Shader (SDF based circles and donuts)
CIRCLE_VS = """
#version 330 core
layout (location = 0) in vec2 in_pos;

uniform vec2 u_resolution;
uniform vec2 u_position;
uniform vec2 u_size;

out vec2 v_uv;

void main() {
    vec2 pixel_pos = u_position + in_pos * u_size;
    vec2 ndc = (pixel_pos / u_resolution) * 2.0 - 1.0;
    ndc.y = -ndc.y;
    gl_Position = vec4(ndc, 0.0, 1.0);
    v_uv = in_pos; // [0, 1] range
}
"""

CIRCLE_FS = """
#version 330 core
in vec2 v_uv;
out vec4 frag_color;

uniform vec4 u_color;
uniform float u_inner_radius; // 0.0 for filled circle, >0 for ring
uniform float u_outer_radius; // typically 0.5
uniform float u_glow;         // soft radial glow factor

void main() {
    vec2 center = vec2(0.5, 0.5);
    float dist = length(v_uv - center);

    if (u_glow > 0.0) {
        // Soft radial glow for King in check
        float intensity = 1.0 - smoothstep(0.0, u_outer_radius, dist);
        intensity = pow(intensity, 1.5) * u_glow;
        frag_color = vec4(u_color.rgb, u_color.a * intensity);
    } else {
        // Crisp antialiased circle or ring
        float edge1 = smoothstep(u_inner_radius - 0.02, u_inner_radius + 0.01, dist);
        float edge2 = 1.0 - smoothstep(u_outer_radius - 0.015, u_outer_radius + 0.015, dist);
        float alpha = edge1 * edge2 * u_color.a;
        frag_color = vec4(u_color.rgb, alpha);
    }
}
"""
