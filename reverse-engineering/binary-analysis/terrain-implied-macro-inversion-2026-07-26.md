# Retail's implied macro cache, derived from its own pixels — and why the macro cache is not the bug

> **Verdict: a precise negative, and a hard one.** Retail's terrain renders
> brighter than the *maximum value the reconstruction's macro compositor can
> produce from the shipped material data at all*. Over 1,875 paired pixels whose
> attributed shade index is ≥ 28 — where the reconstruction's own macro measures
> **0.95 / 0.95 / 1.01 of its per-texel ceiling**, i.e. it is already saturated —
> retail's implied macro measures **1.38 / 1.37 / 1.22 of that same ceiling**.
>
> The ceiling is the value a texel takes when the lighting gradient is at its
> three `min()` saturations. Nothing inside the compositor can exceed it: not a
> blend-weight normalisation, not a palette index, not a material ordering, not a
> missing material, not a different shade plane, not a different gradient. All of
> them are bounded above by the texel's own material blend.
>
> **No gain, offset or tint was applied. No fix landed, deliberately.** The
> pinned root map was NOT regenerated and did not need to be — the compositor's
> behaviour is unchanged.

Frames: `local-lab/retail-reference-pristine/level100-gameplay/hud-timeline-run1/`
at `t020080ms`, `t025065ms`, `t030071ms`. Probe captures:
`local-lab/godot-captures/inv-probe-{mask,chain,macro,uv,uvfine}`, all taken in one
sitting at retail's realised level offsets, all stamped `capturePurpose: probe`.

---

## 1. Why this measurement was needed

`c745a9a2` showed the compositor's only retail-side check to be circular:
`level100-root-terrain.rgb565.bin` is this project's own Python transcription of
the blit, gated against a hash of its own output, and
`Level100TerrainCompositorTests` then asserts C# equals that Python. So the
standing measurement — `retail / macro = 1.400, 1.295, 1.075` — was a ratio
against an **unvalidated denominator**, and nobody had ever compared the
reconstruction's macro cache to retail's.

Eight agents had eliminated every named external mechanism (texture stage chain,
shade interpolation, the shade plane as a bake, fog, stage-0 DIFFUSE, the
MODULATE2X flag, frame-global gamma/format/presentation, the per-node coloured
terrain light). The forced conclusion was that the macro cache itself differs.
This measurement tests that directly.

## 2. Method — inverting retail's chain against measured terms

Retail's terrain pixel is

```
retail_pixel = fog( min(min(macro * detail1, 1) * cloud * 2, 1) * detail2 * 2 )
```

Every term except `macro` is *measured*, per pixel, by capturing the
reconstruction's terrain shader with its fragment tail replaced. The tails live
in `Level100TerrainAppearanceAsset.s_probeTails`, selected by the
`ONSLAUGHT_TERRAIN_PROBE` environment variable; unset, the shipping fragment is
unchanged.

| probe | fragment tail | recovers |
| --- | --- | --- |
| `mask` | `vec3(1, exp(-density*depth), 0)` | terrain coverage + per-pixel fog visibility |
| `chain` | `0.25 * detail1 * cloud * 2 * detail2 * 2` | the whole post-macro chain, both `min()` removed |
| `macro` | `macro_color` | our macro cache as sampled on screen |
| `uv` | `vec3(fract(UV/512), level/8)` | root-map texel coordinate at 2-unit resolution |
| `uvfine` | `vec3(fract(UV/2), 0)` | the same coordinate at 1/128-unit resolution |

Then per paired pixel `implied_retail_macro = unfog(retail_pixel) / chain`, and
`uv`+`uvfine` attribute the pixel to a root-map texel and hence to its authored
material set, mixer weights and shade index.

Tool: `tools/terrain_macro_inversion_probe.py`. It divides only by terms it has
measured and bins the result; it fits nothing.

### 2.1 The inversion is validated end to end

Two independent checks, both required before any conclusion:

**The chain probe reproduces the reconstruction's own terrain.** Over 77,576
unclamped terrain pixels of the production capture
`local-lab/godot-captures/20260726-063703-gameplay`:

| | R | G | B |
| --- | ---: | ---: | ---: |
| chain probe mean | 0.9615 | 0.9369 | 0.9383 |
| reconstruction, unfogged | 109.36 | 112.00 | 155.16 |
| macro probe × chain probe | 108.06 | 110.69 | 153.70 |
| ratio actual / predicted | **1.029** | **1.021** | **1.012** |

So `unfog(pixel) / chain` recovers a macro cache to within **1–3 %**. That is the
error bar on everything below, against a difference of 40 %.

**The world decode, material blend and shade attribution reproduce our macro.**
Recomputing `unlit_material_blend × gradient[shade]` from the `LTH1` hierarchy
bytes at each decoded texel, over 18,246 pixels with a sub-half-texel footprint:

```
ours / predicted   mean 1.039 1.052 1.078   median 1.006 1.005 1.023
                   p25  0.889 0.895 0.945   p75   1.139 1.135 1.151
```

Median 1.00 per channel. The spread is sub-texel filtering — 78 % of these pixels
sample macro level 4, whose cache carries the mixer weights at 16× the root
map's resolution — not attribution failure.

## 3. The distribution: implied vs ours

28,196 usable paired pixels at `t025065ms` (81,698 terrain pixels; the reduction
is dominated by the 2-unit/1-unit world-decode ambiguity, which is dropped rather
than guessed).

```
                       mean                sd                  p05 / p50 / p95
our macro (probe)      107.8 113.0 158.1   44.4 45.5 49.7      24/111/170  33/114/175   76/159/222
retail IMPLIED macro   152.9 154.8 179.2   67.2 67.2 61.9      29/161/250  38/162/256   73/185/266
implied / ours         1.457 1.389 1.147   0.483 0.381 0.275   0.91/1.44/2.08  0.89/1.38/1.91  0.73/1.14/1.54
implied - ours         45.0  41.9  21.1    34.6 34.3 34.1
```

Reproduced across three retail frames:

| frame | implied / ours (mean) |
| --- | --- |
| `t020080ms` | 1.423  1.327  1.096 |
| `t025065ms` | 1.457  1.389  1.147 |
| `t030071ms` | 1.470  1.413  1.168 |

### 3.1 It is a flat per-channel gain, not a structure

**By our macro's luminance** (octiles, `t025065ms`):

| macro luminance | n | ratio R | G | B |
| --- | ---: | ---: | ---: | ---: |
| 17.8–59.5 | 3525 | 1.62 | 1.50 | 1.15 |
| 59.5–80.0 | 3524 | 1.42 | 1.39 | 1.16 |
| 80.0–97.9 | 3525 | 1.45 | 1.41 | 1.17 |
| 97.9–118.1 | 3524 | 1.42 | 1.39 | 1.14 |
| 118.1–142.7 | 3524 | 1.42 | 1.38 | 1.14 |
| 142.7–157.3 | 3525 | 1.41 | 1.35 | 1.12 |
| 157.3–166.9 | 3506 | 1.41 | 1.34 | 1.11 |
| 166.9–226.5 | 3543 | 1.38 | 1.34 | 1.12 |

A two-point fit across the range gives `implied ≈ 1.32·ours + 9.7` (R),
`1.30·ours + 7.6` (G), `1.09·ours + 5.9` (B) — a gain with a small additive term,
which is why only the darkest octile departs.

**By macro level** — 1.50/1.39/1.12 (level 2), 1.49/1.43/1.18 (level 3),
1.40/1.36/1.13 (level 4). **By screen-space texel footprint** — 1.41/1.37/1.13
(<1 texel), 1.47/1.44/1.19 (1–2), 1.44/1.39/1.15 (2–3).

**By material set** (sorted tile material ids), which is the test that would have
named a blend bug:

| materials | n | ours | implied | ratio | mean shade |
| --- | ---: | --- | --- | --- | ---: |
| `[1,3,4,5]` | 23675 | 114.5 119.0 159.0 | 161.5 162.9 180.5 | 1.41 1.37 1.13 | 21.5 |
| `[1,3]` | 3359 | 49.2 58.1 138.3 | 78.1 84.8 158.3 | 1.59 1.46 1.14 | 9.3 |
| `[1,2,3,4,5]` | 888 | 141.8 147.7 196.1 | 185.7 182.2 201.4 | 1.31 1.23 1.03 | 20.9 |
| `[1,3,4]` | 263 | 146.0 152.0 198.1 | 225.5 236.4 257.8 | 1.55 1.55 1.30 | 21.5 |

The spread tracks each set's mean shade, not its material membership. **No
material is short while others match.** A missing or mis-ordered material would
show as one row at ~1.0 and another at ~2.0; nothing like that appears.

**By screen band** (distance proxy) the ratio falls from 1.62/1.49/1.16 at
`y 120–179` to 1.26/1.22/0.99 at `y 420–479` — but so does macro darkness, and
the trend is the same additive term seen in the luminance table, not a distance
effect independent of it.

**Spatially** the paired pixels fall in two 64-unit world blocks — the visible
island — at 1.35 (block 256,192) and 1.49 / 1.20 (blocks 256,256 and 192,256) in
green. Coverage is too narrow for a spatial verdict; this is recorded as
insufficient, not as flat.

### 3.2 The map: implied/ours by 64-unit world block, green channel

```
        x=192  x=256
y=192      .    1.35   (19,566 px)
y=256    1.20   1.49   (705 px / 7,910 px)
```

## 4. The hard result: retail exceeds the compositor's ceiling

The blit's final step is

```
R5 = (red   * lightR & 0xF8000000) >> 16
G6 = (green * lightG & 0x07E00000) >> 16
B5 = (blue  * lightB & 0x001F0000) >> 16
```

and the gradient's three `min()` saturations cap `lightR/G/B` at
`0xF80000 / 0x7E000 / 0x1F00`. Substituting the caps, a texel whose material
blend is `unlit` can never render above `unlit × (247, 251, 247)/255`. That is
the **per-texel ceiling**: the value the texel takes at a fully saturated
lighting gradient, and the most its material data allows under *any* shade index,
mixer weight, palette entry, material id or material ordering.

Selecting on attributed shade — the reconstruction's own gradient saturates at
shade 29 for R/G and 14 for B — at `t025065ms`:

| cut | n | ours | ceiling | implied | ours/ceiling | implied/ceiling |
| --- | ---: | --- | --- | --- | --- | --- |
| shade ≥ 24 | 5924 | 127.5 130.7 155.0 | 146.1 146.6 149.8 | 189.9 192.6 189.2 | 0.87 0.89 1.03 | **1.30 1.31 1.26** |
| shade ≥ 26 | 3636 | 132.5 134.8 152.1 | 147.5 148.1 150.7 | 196.7 198.9 187.3 | 0.90 0.91 1.01 | **1.33 1.34 1.24** |
| shade ≥ 28 | 1875 | 134.9 136.0 145.5 | 142.3 142.5 144.5 | 196.1 195.6 176.5 | **0.95 0.95 1.01** | **1.38 1.37 1.22** |

`ours/ceiling → 0.95, 0.95, 1.01` is the calibration: at shade ≥ 28 the
reconstruction's macro is measured to be at its own ceiling, which independently
confirms both the ceiling arithmetic and the attribution. Retail's implied macro
at the *same pixels* is 22–38 % above it. `t030071ms` gives 1.39 / 1.38 / 1.23 on
the same cut (n = 1,874).

Over all usable pixels, `implied / ceiling` has median **1.04 / 1.03 / 1.15**, and
**56 % / 55 % / 74 %** of pixels exceed the ceiling. Restricting to the 15,559
pixels whose retail pixel is under 200 — where no retail-side `min()` can have
fired and clamping cannot be compressing the estimate — still leaves
**43 % / 45 % / 59 %** above it.

Independently of any attribution: **4.7 % / 5.5 % / 10.0 %** of implied macro
values exceed 252, with maxima of **303 / 325 / 314**. No RGB565 cache holds those.

### What this rules out

Every hypothesis the task listed for the macro is closed by the ceiling:

- a mixer-weight normalisation error — bounded by the ceiling;
- a wrong palette index — bounded by the ceiling;
- a material ordering error — bounded by the ceiling;
- a missing material layer — bounded by the ceiling, and refuted again by the
  per-material table showing no material short and none matching;
- a wrong shade index or a second gradient doubling — bounded by the ceiling, and
  refuted directly: the deficit is **undiminished where our gradient is already
  saturated**. A lighting-index error must vanish at saturation. It does not.

That last point closes `6c905b09`'s reading. "Retail's terrain renders as if the
lighting index were at the gradient's saturation point" is measurably too weak:
retail renders as if it were **1.38× past** the saturation point, which the
gradient cannot reach.

The chain is closed from the other side by the same arithmetic. To supply
1.4× the reconstruction's chain mean of 0.909 needs 1.27, and the shipped detail
texture bounds every arrangement of the stages: `d1·cloud·2 = 0.939`,
`d1·2·cloud·2 = 1.879`, `d1·cloud·2·d2·2 = 0.909`; and with `E[d1] = 0.4836`,
`sd 0.0738`, even perfectly correlated samples give `E[d1·d2] = 0.2393` against
`0.2339` independent — 1.02×, not 1.49×. Every one of those is grey, and the
required factor is not.

## 5. What survives

The missing term is **multiplicative, coloured, terrain-specific, and applied
outside both the macro cache and the shipped texture stages**:

```
retail_terrain = reconstruction_terrain x (1.44, 1.38, 1.13)   [+ a small offset ~ (10, 8, 6)]
```

flat across macro value, macro level, texel footprint, material set and shade,
including where the reconstruction's compositor is already at its arithmetic
maximum.

One observation, recorded and **not acted on**: normalised to blue, the measured
factor is `(1.25, 1.21, 1.00)`, and the HFLD's `sun + ambient` — `(202, 192, 164)`,
already computed by `CHeightField__Load` — normalises to `(1.23, 1.17, 1.00)`.
That is a 1–4 % chromaticity agreement with no magnitude and no mechanism behind
it. It is a lead for a byte-level search, not a finding, and it is emphatically
not licence to multiply anything by anything.

**Nothing was scaled, offset or tinted to close the gap, and no fix landed** —
the pattern rules the fix out of every file this task owned.

## Reproduce

```powershell
foreach ($m in 'mask','chain','macro','uv','uvfine') {
  $env:ONSLAUGHT_TERRAIN_PROBE = $m
  ./rebuild/tools/Capture-Frontend.ps1 -Plan gameplay `
    -RetailOffsetManifest ./local-lab/retail-reference-pristine/level100-gameplay/manifest.json `
    -OutputDirectory "./local-lab/godot-captures/inv-probe-$m"
}
Remove-Item Env:ONSLAUGHT_TERRAIN_PROBE

py -3 tools/terrain_macro_inversion_probe.py `
  --retail local-lab/retail-reference-pristine/level100-gameplay/hud-timeline-run1/level100-t025065ms.png `
  --probe-dir-prefix local-lab/godot-captures/inv-probe
```
