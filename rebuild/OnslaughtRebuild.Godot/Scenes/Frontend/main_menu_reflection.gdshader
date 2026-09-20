// SPDX-License-Identifier: GPL-3.0-or-later
shader_type canvas_item;
render_mode blend_add, unshaded;

uniform sampler2D reflection : filter_linear, repeat_enable;
uniform float scroll;
uniform float gain;

void fragment() {
    // Fragment centres, so x is the pixel's integer column + 0.5.
    float x = 64.0 + (UV.x * 512.0);
    float y = 2.0 + (UV.y * 256.0);

    // D3DCMP_ALWAYS z-stamp of the alpha-tested logo body (ALPHAREF 8).
    float mask = step(8.0 / 255.0, texture(TEXTURE, UV).a);
    // The sheen quad's own edges: its left edge is 65 - scroll and its
    // bottom is y = 248. Everything between is covered by it or by its
    // +512 twin, which is what the mod() below expresses.
    mask *= step(65.0 - scroll, x);
    mask *= step(y, 248.0);

    float u = mod(x - 65.0 + scroll, 512.0) / 512.0;
    float v = (y + 8.0) / 256.0;
    COLOR = vec4(texture(reflection, vec2(u, v)).rgb * gain, mask);
}
