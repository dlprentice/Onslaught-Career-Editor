// SPDX-License-Identifier: GPL-3.0-or-later
shader_type spatial;
render_mode unshaded, cull_back;

uniform sampler2D base_texture : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D dot3_texture : filter_linear_mipmap, repeat_enable;
uniform sampler2D reflection_texture : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D overlay_texture : filter_linear_mipmap, repeat_enable;
uniform float has_dot3;
uniform float has_reflection;
uniform float has_overlay;
uniform float base_blend_texture_alpha;
uniform float alpha_reference;
// Stage-zero D3DTSS_COLOROP as a multiplier: 1.0 for D3DTOP_MODULATE
// (4), 2.0 for D3DTOP_MODULATE2X (5). Per draw, never a constant --
// see RetailStageZeroColorOperation for the runtime reads that fix it.
uniform float stage_zero_gain;
uniform vec2 dot3_offset;
uniform vec2 dot3_scale;
uniform float reflection_factor_alpha;
uniform vec2 overlay_offset;
uniform vec2 overlay_scale;
uniform float overlay_opacity;
// D3DRS_AMBIENT and the two anti-parallel D3DLIGHT9 records, per draw
// and never a level constant -- see RetailMeshLightRig for the device
// reads at SetLight (0x005512e1) that fix them. sun_color is light 0's
// Diffuse, anti_sun_color is light 1's, and sunlight_direction is light
// 0's Direction mapped into Godot; light 1's Direction is its exact
// negation on both measured rigs, which is why one vector serves both.
// On the 442 CRTTree draws light 0 is the sun scaled by the shipped 0.1
// at 0x005d85c0 and the axis is vertical, so the names describe the
// static-world rig and the slots, not the tree rig's physical roles.
uniform vec3 ambient_color;
uniform vec3 sun_color;
uniform vec3 anti_sun_color;
uniform vec3 sunlight_direction;
uniform vec3 fog_color;
uniform float fog_density;
uniform float maximum_horizontal_distance_squared;
varying vec3 vertex_light_color;
varying vec3 model_light_direction;
varying vec2 reflection_uv;
varying float horizontal_distance_squared;

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
    // MultiMesh instance position is available through MODEL_MATRIX
    // here, so carry its camera distance into the fragment stage.
    vec2 horizontal_offset =
        MODEL_MATRIX[3].xz - CAMERA_POSITION_WORLD.xz;
    horizontal_distance_squared = dot(
        horizontal_offset,
        horizontal_offset);
    vec3 world_normal = normalize(mat3(MODEL_MATRIX) * NORMAL);
    float sun = max(dot(world_normal, -sunlight_direction), 0.0);
    float anti_sun = max(dot(world_normal, sunlight_direction), 0.0);
    vertex_light_color = ambient_color + (sun_color * sun) +
        (anti_sun_color * anti_sun);
    // Retail leaves D3DRS_LIGHTING on for the FVF 0x152 mesh draw and
    // sets D3DRS_DIFFUSEMATERIALSOURCE and D3DRS_AMBIENTMATERIALSOURCE
    // to D3DMCS_COLOR1 (D3DStateCache__UseDefaultRenderState,
    // 0x004EB1E0), leaving D3DRS_COLORVERTEX at its TRUE default. The
    // per-vertex DIFFUSE dword is therefore the diffuse and ambient
    // material reflectance for every term of the lighting equation, and
    // the lit result is stage-zero COLORARG2 = D3DTA_DIFFUSE.
    vertex_light_color *= COLOR.rgb;
    model_light_direction = normalize(
        transpose(mat3(MODEL_MATRIX)) * sunlight_direction);

    // D3DTSS_TCI_CAMERASPACEREFLECTIONVECTOR generates
    // 2(N.E)N-E per vertex. Steam then applies [.5,0;0,-.5]
    // and the (.5,.5) offset before interpolating the coordinates.
    vec3 view_position = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
    vec3 view_normal = normalize(MODELVIEW_NORMAL_MATRIX * NORMAL);
    vec3 eye = normalize(-view_position);
    vec3 reflection_vector =
        (2.0 * dot(view_normal, eye) * view_normal) - eye;
    reflection_uv = vec2(
        (reflection_vector.x * 0.5) + 0.5,
        (reflection_vector.y * -0.5) + 0.5);
}

void fragment() {
    if (maximum_horizontal_distance_squared >= 0.0 &&
        horizontal_distance_squared > maximum_horizontal_distance_squared) {
        discard;
    }
    // Steam's high static-world renderer applies a -1 mip bias to
    // hardware stage zero.
    vec4 texture_color = texture(base_texture, UV, -1.0);
    if (base_blend_texture_alpha < 0.5 && texture_color.a < alpha_reference) {
        discard;
    }
    // Stage zero is COLORARG1 = D3DTA_TEXTURE, COLORARG2 =
    // D3DTA_DIFFUSE, and COLOROP is whichever of MODULATE /
    // MODULATE2X the draw is under. Read out of the running safe copy
    // from the texture-stage-state shadow at 0x008557f4 (the setter at
    // 0x00513820 indexes it as (type + stage*0n30)*4 + 0x008557f0):
    // 5 = MODULATE2X on the 134 mode-0 static-world draws and the 442
    // CRTTree mesh draws of one frame, 4 = MODULATE on all seven
    // cockpit batches (16 reads inside the cockpit window, zero
    // transitions while inside it) and on the 19 mode-4 static-world
    // draws of that same frame. So the gain is per draw.
    vec3 retail_color = min(
        texture_color.rgb * vertex_light_color * stage_zero_gain,
        vec3(1.0));
    if (base_blend_texture_alpha > 0.5) {
        retail_color = mix(retail_color, texture_color.rgb, texture_color.a);
    }

    if (has_dot3 > 0.5) {
        vec3 dot3_sample = texture(
            dot3_texture,
            (UV * dot3_scale) + dot3_offset).rgb;
        vec3 encoded_light = round(clamp(
            (model_light_direction * 127.0) + vec3(128.0),
            vec3(0.0),
            vec3(255.0))) / 255.0;
        float dot3_value = clamp(
            4.0 * dot(dot3_sample - vec3(0.5), encoded_light - vec3(0.5)),
            0.0,
            1.0);
        retail_color = vec3(dot3_value);
    }

    if (has_reflection > 0.5) {
        // The reflection layer is another stage-zero world draw, and
        // it is a MODE-0 one: [0x00704e48], the RenderMeshCore mode
        // global, was read at every one of 4,393 mesh renders across
        // three launches and is 0 on 4,314 and 4 on 79 -- never 2,
        // never 6, never 8, and the mode-2/mode-6 draw calls at
        // 0x0054a423 / 0x0054a466 never fired at all. D3DRS_LIGHTING
        // ([0x00855764], the render-state shadow at 0x00855540 indexed
        // state*4) is 1 across all 576 world and tree draws, so the
        // layer is lit, which is what this branch already assumed. It
        // inherits stage zero's colour operation and sampler state;
        // stage one only scales its alpha with texture factor.
        vec4 reflection_color = texture(
            reflection_texture,
            reflection_uv,
            -1.0);
        vec3 reflection_stage_color = min(
            reflection_color.rgb * vertex_light_color * stage_zero_gain,
            vec3(1.0));
        float reflection_alpha = clamp(
            reflection_color.a * reflection_factor_alpha,
            0.0,
            1.0);
        retail_color = mix(
            retail_color,
            reflection_stage_color,
            reflection_alpha);
    }

    if (has_overlay > 0.5) {
        vec4 overlay_color = texture(
            overlay_texture,
            (UV * overlay_scale) + overlay_offset);
        float overlay_alpha = clamp(
            overlay_color.a * overlay_opacity,
            0.0,
            1.0);
        retail_color = mix(retail_color, overlay_color.rgb, overlay_alpha);
    }

    retail_color = apply_retail_fog(retail_color, max(-VERTEX.z, 0.0));
    ALBEDO = retail_output(retail_color);
}
