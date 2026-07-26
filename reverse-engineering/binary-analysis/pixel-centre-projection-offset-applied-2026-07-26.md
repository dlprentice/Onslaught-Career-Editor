# The half-pixel pixel-centre offset, corrected in the projection and measured

> Verdict: **applied and measured.** The frame-global half-pixel offset found in
> [the spatial-dispersion negative](terrain-spatial-dispersion-negative-2026-07-26.md)
> §3 is now corrected in the camera's projection rather than by resampling.
> Sub-pixel registration against retail's frame goes from **0.295 correlation at
> zero shift, peaking 0.604 at (+0.50, +0.50)** to **0.836 at zero shift with the
> peak collapsed onto the origin** — the residual offset is gone. Scored at zero
> shift on `level100-t025065ms`, **FULL FRAME 52.20 % material / meanD 20.7 ->
> 49.28 % / 19.5** and **terrain mid-band 72.85 % / 20.3 -> 65.12 % / 16.4**.
> As predicted, re-rendering beats the resampling estimate where the estimate's
> blur was doing the most damage: the terrain mid-band lands at 65.12 % against
> the resample's 67.11 %.
>
> **The 13 startup shots are byte-identical**, verified by capturing them with
> and without the change in the same session: 13 of 13 SHA-256 matches. The
> frontend does not share this camera, and shot 13 — taken after the Level 100
> world already exists — is unchanged too.

Changed file: `rebuild/OnslaughtRebuild.Godot/FirstFlightWorldView.cs` only.

## 1. What was applied

`BuildCamera` previously built a `Camera3D` in `Perspective` mode with
`Fov = 73.739795`. It now builds the identical frustum explicitly, so a
translation can be added to it:

- `Projection = Frustum`
- `Size = 2 * Near * 0.75` — Godot's frustum projection at the default
  `KEEP_HEIGHT` aspect treats `Size` as the **full vertical extent at the near
  plane** and derives the horizontal extent as `Size * aspect`. With
  `tan(vfov/2) = 0.75` from
  [the camera/hfov note](player-camera-attach-and-mesh-hfov-2026-07-26.md), this
  reproduces the previous perspective projection exactly when the offset is zero.
- `FrustumOffset = (-offset, +offset)` where `offset = Size / viewportHeight * 0.5`.

`Size / viewportHeight` is one pixel of vertical near-plane extent, and it is
also one pixel of **horizontal** extent, because the horizontal extent is
`Size * aspect` over `width = height * aspect`. That is why one scalar serves
both axes and why the correction is independent of the window size. It is
recomputed each frame from the live viewport rather than pinned to 640x480.

The signs are opposed because `FrustumOffset` moves the near-plane *window*, so
the image moves the other way, and because Godot's near-plane y is up while a
captured PNG's y is down. Both axes are therefore `+0.5` **in screen pixels**.

No shader, no terrain source, no `Level100StaticWorldAsset`, no HUD, no capture
script and no pinned artefact was touched.

### Control: the frustum rebuild changes nothing on its own

Switching `Perspective` to `Frustum` is a rewrite of the projection, so it was
verified separately from the offset it exists to carry. A third gameplay capture
was taken with `RetailPixelCentreOffsetPixels` forced to `0.0f`, and compared
against a capture of the unmodified `Perspective` camera taken in the same
session:

| pair | mean absolute per-channel difference over all 92 frames |
| --- | --- |
| two captures of the **unmodified** build (run-to-run noise) | 0.162 |
| **frustum at zero offset vs the original perspective camera** | **0.050** |
| half-pixel offset applied vs before | 5.909 |

The frustum rebuild differs from the perspective camera by **a third of the
capture's own run-to-run noise**, and scores `level100-t025065ms` at exactly
`FULL FRAME 94.84 / 52.20 / 20.7` and `terrain mid-band 99.79 / 72.85 / 20.3` —
digit for digit the pre-change numbers. The 5.909 figure is 36x the noise floor,
so everything measured below is the half pixel and nothing else.

(The capture is not bit-deterministic across runs: two runs of the identical
build produce 52 of 92 byte-identical PNGs. That is why the control is a
difference magnitude against a measured noise floor rather than a hash match.)

## 2. The measurement that says the offset is gone

`tools/terrain_spatial_structure_probe.py` §4, high-pass correlation over all
terrain pixels, reconstruction frame moved by fractional amounts, retail frame
`hud-timeline-run1/level100-t025065ms.png`:

| | correlation at (0, 0) | peak | peak location | control at peak |
| --- | --- | --- | --- | --- |
| before | 0.295 | 0.604 | dy +0.50, dx +0.50 | -0.036 |
| **after** | **0.836** | 0.841 | dy +0.00, dx +0.25 | **+0.831** |

The "after" peak at `dx = +0.25` is **not** a residual offset. Its control — the
same shift applied to the retail frame instead — is 0.8305 against the peak's
0.8411, i.e. the shift helps both frames equally, which is the signature of
blur, not of registration. Before the fix the same control was **-0.036**
against a peak of 0.604: a real offset. `dy` lands on exactly 0.00.

## 3. Per-region scores at zero shift

`py -3 tools/compare_capture.py --regions rebuild/tools/gameplay-regions-level100.json`
against `hud-timeline-run1/level100-t025065ms.png`. `compare_capture.py` applies
no shift, so these are honest zero-shift numbers on both sides.

| region | changed% before -> after | material% before -> after | meanD before -> after |
| --- | --- | --- | --- |
| **FULL FRAME** | 94.84 -> **85.16** | 52.20 -> **49.28** | 20.7 -> **19.5** |
| sky | 84.13 -> **61.61** | 18.54 -> 19.17 | 6.5 -> 6.4 |
| horizon ridge | 97.29 -> **86.54** | 51.41 -> **47.00** | 15.3 -> **13.6** |
| **terrain mid-band** | 99.79 -> 98.43 | 72.85 -> **65.12** | 20.3 -> **16.4** |
| cockpit frame (left) | 99.91 -> 98.91 | 80.27 -> 79.64 | 35.5 -> 35.0 |
| cockpit frame (right) | 100.00 -> 100.00 | 94.01 -> 93.57 | 45.5 -> 45.5 |
| threat circle | 95.33 -> **83.55** | 59.15 -> **57.57** | 20.2 -> **18.2** |
| scanner (lower left) | 97.19 -> 97.01 | 62.76 -> **57.59** | 27.9 -> 27.2 |
| portrait/compass | 99.81 -> 99.80 | 90.53 -> 90.89 | 62.0 -> 61.9 |
| message panel | 99.72 -> 99.59 | 57.86 -> 57.37 | 26.3 -> 26.2 |

Averaged over **all 98 retail reference frames** of `opening-pan-run1` and
`hud-timeline-run1` paired to their 92 captured offsets, not one frame:

| region | changed% | material% | meanD |
| --- | --- | --- | --- |
| FULL FRAME | 96.17 -> **89.09** | 59.13 -> **57.80** | 23.06 -> **22.35** |
| sky | 88.14 -> **71.61** | 26.14 -> 26.42 | 8.41 -> 8.30 |
| horizon ridge | 98.07 -> **90.38** | 56.17 -> **52.81** | 18.02 -> **16.82** |
| terrain mid-band | 99.81 -> 98.81 | 75.68 -> **70.89** | 26.26 -> **23.58** |
| threat circle | 96.63 -> **88.29** | 63.10 -> **60.37** | 24.58 -> **22.95** |

The `changed%` column is where a sub-pixel offset shows most plainly: it is the
fraction of pixels that differ *at all*, and a half-pixel misregistration makes
essentially every textured pixel differ. Full-frame `changed%` falls 96.17 to
89.09 and the sky's falls 88.14 to 71.61. The sky moving is the cross-check that
the correction is frame-global rather than a terrain effect.

The regions that barely move — the portrait/compass, the message panel, the
cockpit frame — are the ones whose remaining error is colour, not position.

## 4. Gates

| gate | result |
| --- | --- |
| `test:rebuild-core` | **94 / 94 PASS** |
| `test:rebuild-client` | **135 / 135 PASS** |
| `test:rebuild-godot-smoke` | **PASS**, `stateHash` `c3ae5a39fbbc4a47f1309c2d7ec5a2c874f8f41f364d38263e60b6965f450b47`, tick 3228 — unchanged |
| 13 startup shots | **13 / 13 SHA-256 identical** |

The startup check is a controlled A/B in one session, not a comparison against a
stored capture: the working-tree change was stashed, `-Plan startup` captured to
`halfpixel-startup-before`, the change restored, and `-Plan startup` captured to
`halfpixel-startup-after`. Every one of the 13 PNGs hashes the same.

### The terrain gain

`tools/terrain_transfer_probe.py` on the same frame, at zero shift:

```
CHAIN GAIN = unfogged pixel / macro          R        G        B
  retail                                  1.401    1.296    1.074
  reconstruction BEFORE                   1.384    1.266    1.049
  reconstruction AFTER                    1.384    1.266    1.047
```

R and G are unchanged to three places; B moves 0.002. **That residual is a
measurement artefact, not a shading change.** The probe pairs the rendered frame
against the `al-probe-macro` / `al-probe-mask` captures, and those probe frames
were rendered with the *old* projection, so after the fix they sit half a pixel
away from the frame they are being paired with. Re-measuring the gain exactly
would need the two probe captures retaken with the corrected projection, which
requires the terrain-shader probe builds. No shader was modified, so no shading
term changed.

## Reproduce

```powershell
$retail = 'local-lab/retail-reference-pristine/level100-gameplay/hud-timeline-run1/level100-t025065ms.png'
pwsh -NoLogo -NoProfile -File ./rebuild/tools/Capture-Frontend.ps1 -Offline -Plan gameplay `
  -RetailOffsetManifest local-lab/retail-reference-pristine/level100-gameplay/manifest.json `
  -OutputDirectory local-lab/godot-captures/halfpixel-after
py -3 tools/compare_capture.py --reference $retail `
  --candidate local-lab/godot-captures/halfpixel-after/level100-t025065ms.png `
  --regions rebuild/tools/gameplay-regions-level100.json
py -3 tools/terrain_spatial_structure_probe.py --retail $retail `
  --rebuild     local-lab/godot-captures/halfpixel-after/level100-t025065ms.png `
  --macro-probe local-lab/godot-captures/al-probe-macro/level100-t025065ms.png `
  --mask-probe  local-lab/godot-captures/al-probe-mask/level100-t025065ms.png `
  --regions rebuild/tools/gameplay-regions-level100.json --shift 0,0
```

Captures are stamped `capturePurpose: probe` because the working tree was dirty
when they were taken. That is correct: no automated gate may score them as the
shipping build until the change is committed.
