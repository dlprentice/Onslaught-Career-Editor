// SPDX-License-Identifier: GPL-3.0-or-later
shader_type spatial;
render_mode unshaded;

// Steam owns macro UVs as repeated absolute landscape X/Y in each
// 20-byte vertex. Each logical level is an independent one-level
// 512x512 cache with a progressively smaller virtual world span.
uniform sampler2D macro_map_0 : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D macro_map_1 : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D macro_map_2 : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D macro_map_3 : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D macro_map_4 : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D detail_map : filter_linear_mipmap, repeat_enable;
uniform sampler2D cloud_shadow_map : filter_linear_mipmap, repeat_enable;
uniform vec3 fog_color;
uniform float fog_density;
// The constant lit vertex colour of retail's terrain draw:
// 0.8 x (CHFD+0x107C + CHFD+0x1080) / 256, computed at load from the
// shipped HFLD by Level100TerrainCompositor.TerrainVertexDiffuse. The
// terrain vertex carries no normal, so this is one colour for the whole
// surface with no positional term.
uniform vec3 terrain_vertex_diffuse;
uniform vec2 terrain_cloud_scroll;

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

vec3 sample_macro_map(int level, vec2 retail_world_uv) {
    if (level == 4) {
        return texture(macro_map_4, retail_world_uv / 32.0).rgb;
    }
    if (level == 3) {
        return texture(macro_map_3, retail_world_uv / 64.0).rgb;
    }
    if (level == 2) {
        return texture(macro_map_2, retail_world_uv / 128.0).rgb;
    }
    if (level == 1) {
        return texture(macro_map_1, retail_world_uv / 256.0).rgb;
    }
    return texture(macro_map_0, retail_world_uv / 512.0).rgb;
}

void fragment() {
    vec2 retail_world_uv = UV;
    int macro_level = int(clamp(floor(UV2.x + 0.5), 0.0, 4.0));
    vec3 macro_color = sample_macro_map(macro_level, retail_world_uv);
    vec3 detail_primary = texture(detail_map, retail_world_uv).rgb;
    // Retail's stage-3 texture matrix is
    // [k*cos(t), k*sin(t); -k*sin(t), k*cos(t)] with offset (0.3, 0.3),
    // k = *(float *)0x005d858c = 0.25 and t = *(float *)0x005d87e0 = 0.0.
    // Both live in .rdata (0x005d8000..0x00622000) in a .reloc-free image,
    // so the angle is fixed at zero for the life of the process and the
    // matrix is a pure uniform quarter-scale aligned with stage 1.
    vec2 detail_secondary_uv = (retail_world_uv * 0.25) + vec2(0.3);
    vec3 detail_secondary = texture(detail_map, detail_secondary_uv).rgb;
    // Stage 2's texture matrix is written at 0x0054591a-0x00545967:
    // _11 (0x628258) = _22 (0x62826c) = 0x3b800000 = 1/256, _12/_21
    // zero, and the translation row _31 (0x628278) = *(float
    // *)0x008c0294, _32 (0x62827c) = *(float *)0x008c0298. Those two
    // globals are the cloud scroll accumulators, advanced at the head
    // of CDXLandscape__RenderTerrain (0x005455d2-0x0054563a) by
    //   u += dt * *(float *)0x005d8580 (0x3a83126f = 0.001)
    //   v += dt * *(float *)0x005e50e4 (0x3a03126f = 0.0005)
    // each followed by a single `if (x >= 1.0) x -= 1.0` against
    // *(float *)0x005d8568 (0x3f800000 = 1.0), which for a monotonic
    // accumulator is fract().
    //
    // BOTH HALVES OF THE PARAGRAPH BELOW WERE WRONG, and it is retained
    // only because it is the reasoning that led here. The rate was NOT
    // retail's -- see the remarks on CloudScrollRateU -- and the origin
    // is now correct and confirmed at runtime. Read the CORRECTED and
    // CONFIRMED notes that follow as the current statement.
    //
    // Superseded: "KNOWN DIVERGENCE - the rate is retail's, the origin
    // is not. A whole-file operand scan finds exactly five references to
    // each of 0x008c0294 and 0x008c0298, all five inside RenderTerrain,
    // and both addresses lie in the uninitialised tail of .data.
    // Retail's scroll offset is therefore 0.001 x (total frame time
    // accumulated across terrain draws since process start), with no
    // per-level reset and no advance while the front end is up."
    //
    // The operand-scan half of that is sound and still holds; the
    // inference from it is what failed. Five references with no
    // initialiser establishes that nothing RESETS the accumulator in the
    // image -- it does not establish the zero, because the zero is set
    // by whatever runs before the first terrain draw, which the file
    // cannot show. The measured zero is the level's first frame.
    //
    // The scroll is what produces 96 percent of the reconstruction's
    // measured terrain drift:
    // reverse-engineering/binary-analysis/terrain-chain-temporal-drift-2026-07-26.md
    // (itself partially superseded on the rate; its origin finding
    // stands).
    // CORRECTED 2026-07-26. The origin is now retail's: Update() takes
    // the frame delta and advances a per-terrain-draw accumulator with
    // the same two rates and the same fract() wrap, so the phase counts
    // time spent drawing terrain rather than time since engine launch.
    // TIME is deliberately no longer referenced here -- it carried the
    // front end's 8.167 s (490 frames at --fixed-fps 60) plus, in
    // ordinary play, however long the player spent in menus.
    //
    // CONFIRMED 2026-07-26 by reading the live accumulators: their zero
    // is the level's first frame, not process start. Back-extrapolating
    // u from three samples puts u = 0 at process uptime 26.15 s against
    // a level start of about 26.3 s. So resetting the phase at level
    // entry, as this asset does, is retail's behaviour.
    //
    // The rate, however, was NOT what the .rdata constants suggested —
    // see the remarks on CloudScrollRateU.
    //
    // This is necessary but is NOT known to be sufficient. Solving for
    // the single phase that both matches retail's measured stage-1..3
    // ratio 1.0091/1.0213/1.0232 and stays inside retail's measured
    // temporal flatness admits only phi in [5.0, 13.5] s (plus a
    // one-second sliver near 361.5 s) -- 1.1 percent of the 1000 s
    // cycle. The bare level clock, 25.065 s, is excluded too: it
    // predicts a -0.11/-0.16/-0.15 percent-per-second drift retail does
    // not show. Retail's true phase needs one runtime read of
    // 0x008c0294/0x008c0298 and is not settled here.
    vec3 cloud_shadow = texture(
        cloud_shadow_map,
        (retail_world_uv / 256.0) + terrain_cloud_scroll).rgb;
    // Stage 0 is COLORARG1 = D3DTA_TEXTURE, COLORARG2 = D3DTA_DIFFUSE
    // (0x00545699, 0x005456a8) with COLOROP = D3DTOP_MODULATE2X
    // (0x005454ae; the MODULATE alternative at 0x0054568a is taken only
    // when LANDSCAPE_LIGHTING is zero, and its default is 1). So the
    // macro texel is multiplied by the lit vertex colour and doubled.
    // The 2.0 is the stage op and terrain_vertex_diffuse is the lighting
    // term; neither is meaningful without the other, and applying the
    // doubling alone overshoots.
    // Fixed-function stages saturate, hence the min() - the same clamp
    // the two later 2x stages below already carry.
    vec3 stage_color = min(
        macro_color * terrain_vertex_diffuse * 2.0,
        vec3(1.0));
    stage_color *= detail_primary;
    stage_color = min(stage_color * cloud_shadow * 2.0, vec3(1.0));
    vec3 retail_color = min(stage_color * detail_secondary * 2.0, vec3(1.0));
    retail_color = apply_retail_fog(retail_color, max(-VERTEX.z, 0.0));
    ALBEDO = retail_output(retail_color);
    // PROBE_HOOK
}
