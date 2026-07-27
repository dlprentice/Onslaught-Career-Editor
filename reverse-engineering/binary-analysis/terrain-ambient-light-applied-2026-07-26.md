# The terrain ambient-light term, implemented and measured

> Verdict: **implemented in the reconstruction's terrain shader and measured
> against retail.** The unfogged per-pixel terrain gain moves from
> **0.991 / 0.957 / 0.950** to **1.384 / 1.266 / 1.049** against retail's
> **1.400 / 1.295 / 1.075**, and the terrain mid-band region falls from
> **91.15 % material / meanD 35.4** to **72.85 % / 20.3**. **The specific
> prediction was missed**: the terrain mid-band was predicted near
> (167, 168, 187) and landed at **(157.3, 156.4, 172.9)** against retail's
> (163.4, 162.4, 179.6). The 2–4 % shortfall documented in
> [the derivation](terrain-ambient-light-material-2026-07-26.md) §7 survives the
> implementation intact and **was not tuned away**. Per-pixel gain dispersion is
> unchanged in relative terms, exactly as a constant multiplier requires.

## 1. What was implemented, and where

The mechanism is
[the ambient-light material derivation](terrain-ambient-light-material-2026-07-26.md);
it is not re-derived here. It is a **draw-time** term — retail produces it inside
`CDXLandscape::Render` at `0x005454ae`–`0x00545517`, not when the landscape cache
is built — so it is implemented in the fragment shader and **no cached or pinned
artefact was regenerated**. `Level100TerrainCompositor.RenderTile` is untouched,
and the pinned root map still reproduces byte for byte.

`Level100TerrainCompositor.TerrainVertexDiffuse(light0Rgb24, light1Rgb24)` returns

```
min( 0.8 x (light0 + light1) / 256 , 1 )    per channel
```

- `0.8` is `0x3f4ccccd` at `0x0083d28c + 0x10`, the ambient reflectance of the
  terrain-only `D3DMATERIAL9` whose Diffuse is black and Emissive zero. *(Note
  added 2026-07-27: the **material's** ambient is the operative one even though
  `D3DRS_AMBIENTMATERIALSOURCE` is `D3DMCS_COLOR1`, because the terrain stream
  carries no vertex colour and D3D9 falls back to the material. An implicit-white
  fallback would predict `(1.750, 1.656, 1.383)` against the measured
  `(1.457, 1.389, 1.147)`. See the material note's §5 correction block.)*
- `1/256` is `_DAT_005db060` = `0x3b800000`.
- the `min` is Direct3D's own clamp on a lit vertex colour. For Level 100 the
  result is (0.700, 0.663, 0.553) and it does not fire.
- the two arguments are the HFLD fields `CHFD+0x107C` and `CHFD+0x1080`, the two
  and only two lights `CEngine::SetupLights` @ `0x0044a2d0` enables. They are
  **read from the shipped height field at load** —
  `Level100HeightFieldAsset.SunColorRgb24` / `.AntiSunColorRgb24`, which
  `OnslaughtRebuild.Core` parses at exactly those offsets. No colour, sum or
  factor is written down as a literal anywhere in the renderer; another level's
  lights are other bytes and produce another term.

The shader receives that triple as `uniform vec3 terrain_vertex_diffuse` and
consumes it at stage 0 together with the stage op, in one expression:

```glsl
vec3 stage_color = min(macro_color * terrain_vertex_diffuse * 2.0, vec3(1.0));
```

The `2.0` is `D3DTOP_MODULATE2X` (`0x005454ae`; the `MODULATE` alternative at
`0x0054568a` is reachable only when `LANDSCAPE_LIGHTING` is zero, and its
registered default is 1). The `min` is the fixed-function stage saturation, the
same clamp the two later 2x stages in this shader already carried. **The
doubling and the lighting term are deliberately one expression**: an earlier
experiment applied the stage-0 2x alone and overshot to 1.855, because without
the terrain material — which kills the diffuse channel and responds at 0.8 —
there is nothing for the 2x to be doubling.

Files: `rebuild/OnslaughtRebuild.Godot/Level100TerrainCompositor.cs` (the
byte-derived term, Godot-free so the client tests link it),
`rebuild/OnslaughtRebuild.Godot/Level100TerrainAppearanceAsset.cs` (the uniform
and the stage-0 composition),
`rebuild/OnslaughtRebuild.Client.Tests/Level100TerrainAmbientLightTests.cs`
(three tests pinning the coefficients to shipped bytes and the composition to
one expression).

## 2. The transfer function, before and after

Method: `tools/terrain_transfer_probe.py`, which pairs every terrain pixel of
retail's own frame with the reconstruction's macro-cache value at the same
screen pixel (`ONSLAUGHT_TERRAIN_PROBE=macro`), masks the terrain surface and
recovers fog analytically from `ONSLAUGHT_TERRAIN_PROBE=mask`. It fits nothing.

Frame `level100-t025065ms`, 71,426 usable paired terrain pixels, shift `-1,0`.

```
CHAIN GAIN = unfogged pixel / macro          R        G        B
  retail                                  1.400    1.295    1.075
  reconstruction BEFORE                   0.991    0.957    0.950
  reconstruction AFTER                    1.384    1.266    1.049
  after / retail                          0.989    0.978    0.976
```

The predicted stage-0 factor is (1.400, 1.325, 1.106) and the reconstruction's
pre-existing stage-1..3 chain measures (0.991, 0.957, 0.950), whose product is
(1.387, 1.268, 1.051) — the measured after-value to three places. The
implementation therefore does exactly and only what the derivation says, and the
remaining **1.1 % / 2.2 % / 2.4 %** is the residual, not a defect in the wiring.

Means over the same pixels, as shown on screen: retail (155.9, 154.3, 178.9),
reconstruction (119.3, 121.7, 163.7) before and (156.9, 153.2, 177.9) after.

## 3. The frame, region by region

`py -3 tools/compare_capture.py --regions rebuild/tools/gameplay-regions-level100.json`
against `hud-timeline-run1/level100-t025065ms.png`:

| region | before material% / meanD | after material% / meanD | retail RGB | after RGB |
| --- | --- | --- | --- | --- |
| FULL FRAME | 63.81 / 26.5 | **52.20 / 20.7** | (133.2, 124.4, 135.0) | (134.9, 127.6, 137.2) |
| terrain mid-band | 91.15 / 35.4 | **72.85 / 20.3** | (163.4, 162.4, 179.6) | (157.3, 156.4, 172.9) |
| horizon ridge | 63.16 / 17.5 | 51.41 / 15.3 | (126.3, 121.6, 144.7) | (118.5, 116.1, 139.5) |
| threat circle | 67.16 / 27.0 | 59.15 / 20.2 | (169.6, 157.8, 164.5) | (167.7, 163.1, 166.6) |
| scanner (lower left) | 95.94 / 38.1 | 62.76 / 27.9 | (141.1, 145.3, 165.0) | (160.0, 165.6, 185.4) |
| message panel | 97.07 / 37.3 | 57.86 / 26.3 | (107.1, 112.9, 126.9) | (115.4, 120.4, 132.6) |
| sky | 18.54 / 6.5 | 18.54 / 6.5 | (171.9, 135.8, 105.5) | (168.1, 130.5, 102.3) |
| cockpit frame (left) | 80.36 / 34.9 | 80.27 / 35.5 | (40.5, 45.7, 67.1) | (60.0, 67.4, 101.1) |

The sky is byte-identical and the cockpit frames are unmoved, which is the
control: this term reaches the terrain draw and nothing else. The lower-HUD
regions move because terrain is visible through and around them; the scanner and
message panel now overshoot retail slightly, where before they undershot.

**The prediction was (167, 168, 187) for the terrain mid-band and the measured
result is (157.3, 156.4, 172.9)** — 5.8 % / 6.9 % / 7.6 % below the prediction,
and 3.7 % / 3.7 % / 3.7 % below retail. Two things account for the region mean
sitting under the clean per-pixel gain of §2: the region contains fogged pixels
whose gain is diluted toward the fog colour, and **6.3 % of terrain pixels
saturate at least one channel at stage 0** (`macro x factor > 255`; 3.7 % / 3.0 %
/ 2.8 % per channel), which is real fixed-function behaviour that retail also
performs and which no multiplier recovers.

## 4. Dispersion: unchanged, as a constant multiplier requires

`tools/terrain_gain_dispersion_probe.py`, same pixels:

```
PER-PIXEL GAIN            mean                    sd                  sd/mean
  retail             1.405 1.298 1.078      0.527 0.411 0.334     0.375 0.317 0.310
  reconstruction BEFORE  0.991 0.957 0.949  0.097 0.074 0.060     0.098 0.077 0.063
  reconstruction AFTER   1.382 1.262 1.046  0.138 0.097 0.064     0.100 0.077 0.061
```

A flat factor multiplies mean and sd together and leaves `sd/mean` fixed, and
that is precisely what happened: 0.098/0.077/0.063 → 0.100/0.077/0.061 against
retail's 0.375/0.317/0.310. **This was expected and is not evidence for or
against the factor.** Retail's terrain carries roughly three times the relative
per-pixel variation the reconstruction's does — a separate, unexplained defect in
the spatial structure of the terrain, untouched by this work and not addressed by
it.

## 5. The residual, stated and not closed

`tools/terrain_macro_inversion_probe.py` is unchanged by this work by
construction — it divides retail's frame by the reconstruction's *chain* probe,
which excludes stage 0 — and still reports implied/ours = **1.457 / 1.389 /
1.147** against the derivation's 1.400 / 1.325 / 1.106.

The implemented term therefore lands **1.1 % / 2.2 % / 2.4 % low** on the clean
per-pixel measure and 3.7 % low on the terrain region mean. That gap is the
residual the derivation recorded in advance (§7 there: uniformly 3.6–4.6 % low,
roughly achromatic in light-colour units, `(9.1, 10.2, 6.5)` out of 256) and it
is attributed there to a probable **third light**: a second light-setup path at
`0x00450428`–`0x00450b3f` enables `0x009c68a0`, `0x009c68a1` **and**
`0x009c68a2`, and which path is live for Level 100 gameplay is not decided by
static reading. It needs the runtime light state at the terrain draw.

**SUPERSEDED 2026-07-26 — that third-light attribution is FALSIFIED.** See
[`terrain-third-light-2026-07-26.md`](terrain-third-light-2026-07-26.md).
`SetupLights` provably dominates every terrain draw (single caller each, same
function, no intervening branch target), and it enables exactly two lights
unconditionally. The three-light path belongs to `.?AVCFEPBEConfig@@` slot 5, a
front-end page. It is falsified twice over independently of liveness: its rig
gives R = B against a measured `(1.457, 1.389, 1.147)`, and its third light is
12–24x too large and achromatic.

Two further findings from that work bear directly on this document. First, the
residual is **degenerate**: retail-total / predicted-stage-0 is
`(1.0000, 0.9774, 0.9720)` against our stage-1..3 chain `(0.9910, 0.9570,
0.9500)`, so the identical residual reads equally well as "stages 1–3 are
0.9/2.1/2.3 % dark, stage-0 exact in R". A flat gain measurement cannot separate
the two readings. Second, and larger: over ten paired frames spanning
t0+23.1 s to t0+34.1 s, **retail's terrain chain gain is flat to sd
0.0018/0.0032/0.0028 while the reconstruction's falls monotonically at
−0.12/−0.22/−0.22 %/s**, with our own macro-probe input unchanged. The residual
quoted above is therefore a single-frame slice of a moving quantity. The
constant part stays open and unattributed; the drift is tracked separately in
[`terrain-chain-temporal-drift-2026-07-26.md`](terrain-chain-temporal-drift-2026-07-26.md).

**No gain, offset or tint was added to close it.** Every coefficient in the
implementation is a shipped byte or a Direct3D operation, and the shader contains
no numeric literal that came from a measurement.

## Reproduce

```powershell
./rebuild/tools/Capture-Frontend.ps1 -Plan gameplay `
  -RetailOffsetManifest ./local-lab/retail-reference-pristine/level100-gameplay/manifest.json `
  -OutputDirectory ./local-lab/godot-captures/ambient-light-after

foreach ($m in 'macro','mask') {
  $env:ONSLAUGHT_TERRAIN_PROBE = $m
  ./rebuild/tools/Capture-Frontend.ps1 -Plan gameplay `
    -RetailOffsetManifest ./local-lab/retail-reference-pristine/level100-gameplay/manifest.json `
    -OutputDirectory "./local-lab/godot-captures/al-probe-$m"
}
Remove-Item Env:ONSLAUGHT_TERRAIN_PROBE

$retail = 'local-lab/retail-reference-pristine/level100-gameplay/hud-timeline-run1/level100-t025065ms.png'
py -3 tools/compare_capture.py --reference $retail `
  --candidate local-lab/godot-captures/ambient-light-after/level100-t025065ms.png `
  --regions rebuild/tools/gameplay-regions-level100.json
py -3 tools/terrain_transfer_probe.py --retail $retail `
  --rebuild      local-lab/godot-captures/ambient-light-after/level100-t025065ms.png `
  --macro-probe  local-lab/godot-captures/al-probe-macro/level100-t025065ms.png `
  --mask-probe   local-lab/godot-captures/al-probe-mask/level100-t025065ms.png --shift -1,0
py -3 tools/terrain_gain_dispersion_probe.py --retail $retail `
  --rebuild      local-lab/godot-captures/ambient-light-after/level100-t025065ms.png `
  --macro-probe  local-lab/godot-captures/al-probe-macro/level100-t025065ms.png `
  --mask-probe   local-lab/godot-captures/al-probe-mask/level100-t025065ms.png
py -3 tools/terrain_ambient_light_factor_probe.py
```

Captures are stamped `capturePurpose: probe` because the working tree was dirty
when they were taken; that is correct and deliberate, and no automated gate
scores them.

## Gates

`test:rebuild-core` 94/94. `test:rebuild-client` **135**/135 (132 unchanged plus
the three new tests above; **no pinned artefact was regenerated** — the terrain
compositor test still reproduces the pinned root map byte for byte).
`test:rebuild-godot-smoke` PASS with `stateHash`
`c3ae5a39fbbc4a47f1309c2d7ec5a2c874f8f41f364d38263e60b6965f450b47` unchanged.
All 13 startup-plan shots SHA-256 identical to the pre-change capture.
`prepare:rebuild-assets` 319 exact files.
