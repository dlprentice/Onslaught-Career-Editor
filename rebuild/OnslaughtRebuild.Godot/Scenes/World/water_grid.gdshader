// SPDX-License-Identifier: GPL-3.0-or-later
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_always, cull_disabled;

uniform sampler2D caustic_texture : filter_linear_mipmap, repeat_enable;
uniform sampler2D reflection_texture : filter_linear_mipmap, repeat_enable;
uniform vec3 water_color;
uniform vec2 retail_origin;
uniform float caustic_phase;
uniform vec3 fog_color;
uniform float fog_density;
varying vec3 water_world_position;

vec3 retail_output(vec3 color) {
    if (OUTPUT_IS_SRGB) {
        return color;
    }
    vec3 low = color / 12.92;
    vec3 high = pow((color + vec3(0.055)) / 1.055, vec3(2.4));
    return mix(low, high, step(vec3(0.04045), color));
}

vec3 apply_retail_fog(vec3 color, float view_depth) {
    float visibility = clamp(exp(-fog_density * view_depth), 0.0, 1.0);
    return mix(fog_color, color, visibility);
}

void vertex() {
    water_world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
    vec2 retail_xy = vec2(
        water_world_position.x + retail_origin.x,
        retail_origin.y - water_world_position.z);

    vec2 caustic_a = vec2(
        (retail_xy.x * 0.1) + (retail_xy.y * 0.03),
        (retail_xy.x * 0.03) - (retail_xy.y * 0.1));
    caustic_a += vec2(sin(caustic_phase), cos(caustic_phase)) * 0.1;

    float second_phase = caustic_phase + 3.14159265359;
    vec2 caustic_b = vec2(
        (retail_xy.x * 0.03) + (retail_xy.y * 0.1),
        (retail_xy.x * 0.1) - (retail_xy.y * 0.03));
    caustic_b += vec2(sin(second_phase), cos(second_phase)) * 0.1;

    // The active Steam path uses the camera/world translation with a
    // 1/256 texture transform. The animated 1/2-scale transform belongs
    // to the optional advanced path, which Level 100 does not enable.
    vec2 reflection_uv = retail_xy / 256.0;
    vec3 caustic_0 = texture(caustic_texture, caustic_a).rgb;
    vec3 caustic_1 = texture(caustic_texture, caustic_b).rgb;
    vec3 reflected = texture(reflection_texture, reflection_uv).rgb;

    // Steam disables texture stage 3 before switching to the one-UV
    // grid vertex format. The animated waves stage remains active only
    // for the authored shoreline passes.
    vec3 base_water = min((water_color * caustic_0 * caustic_1) + reflected, vec3(1.0));
    vec3 retail_color = min(COLOR.rgb * base_water, vec3(1.0));
    retail_color = apply_retail_fog(retail_color, max(-VERTEX.z, 0.0));
    ALBEDO = retail_output(retail_color);
    ALPHA = COLOR.a;
}
