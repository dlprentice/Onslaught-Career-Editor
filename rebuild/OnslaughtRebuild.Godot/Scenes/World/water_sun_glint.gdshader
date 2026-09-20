// SPDX-License-Identifier: GPL-3.0-or-later
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_opaque, cull_disabled;

uniform sampler2D sun_reflection_texture : filter_linear_mipmap, repeat_enable;
uniform sampler2D sun_blob_texture : filter_linear_mipmap, repeat_enable;
uniform float glint_phase;
uniform float projection_depth_bias;
uniform vec2 retail_origin;
varying vec2 sun_reflection_coordinates;

vec3 retail_output(vec3 color) {
    if (OUTPUT_IS_SRGB) {
        return color;
    }
    vec3 low = color / 12.92;
    vec3 high = pow((color + vec3(0.055)) / 1.055, vec3(2.4));
    return mix(low, high, step(vec3(0.04045), color));
}

void vertex() {
    vec3 world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    sun_reflection_coordinates = vec2(
        world_position.x + retail_origin.x,
        retail_origin.y - world_position.z);
    POSITION = PROJECTION_MATRIX * MODELVIEW_MATRIX * vec4(VERTEX, 1.0);
    POSITION.z += projection_depth_bias * POSITION.w;
}

void fragment() {
    vec2 reflection_a_uv = vec2(
        (sun_reflection_coordinates.x * 0.1) + (sun_reflection_coordinates.y * 0.03),
        (sun_reflection_coordinates.x * 0.03) - (sun_reflection_coordinates.y * 0.1));
    reflection_a_uv += vec2(sin(glint_phase), cos(glint_phase)) * 0.1;

    float second_phase = glint_phase + 3.14159265359;
    vec2 reflection_b_uv = vec2(
        (sun_reflection_coordinates.x * 0.03) + (sun_reflection_coordinates.y * 0.1),
        (sun_reflection_coordinates.x * 0.1) - (sun_reflection_coordinates.y * 0.03));
    reflection_b_uv += vec2(sin(second_phase), cos(second_phase)) * 0.1;

    vec4 reflection_a = texture(sun_reflection_texture, reflection_a_uv);
    vec4 reflection_b = texture(sun_reflection_texture, reflection_b_uv);
    vec4 blob = texture(sun_blob_texture, UV);

    // Retail stages 0..2 use SELECTARG1, ADD, ADD for alpha, then
    // D3DCMP_GREATEREQUAL against alpha ref 0xC0. The colour path selects
    // the retained Level-100 texture-factor value #E8E8FF.
    float glint_alpha = min(reflection_a.a + reflection_b.a + blob.a, 1.0);
    if (glint_alpha < (192.0 / 255.0)) {
        discard;
    }
    ALBEDO = retail_output(vec3(232.0 / 255.0, 232.0 / 255.0, 1.0));
    ALPHA = 1.0;
}
