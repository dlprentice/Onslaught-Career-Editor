# Retail's terrain has no high-frequency term we are missing — and the frame is half a pixel out

> Verdict: **precise negative on the premise, plus one real defect found.**
> The claim that "retail's terrain carries roughly three times our relative
> per-pixel variation" is **not a missing spatial term**. Measured band for band,
> retail's terrain power spectrum and the reconstruction's agree to within 9 % at
> every spatial frequency from DC to Nyquist, including the near-Nyquist bands
> (**retail/ours 0.98 at 0.4–0.5 cycles/pixel**). The `sd/mean` gap is an artefact
> of a non-robust statistic over a heavy-tailed ratio: **9.5 % of terrain pixels
> carry 87.7 % of the variance**, and they are clustered on the terrain
> silhouette and the HUD boxes, not spread over the surface.
>
> What the search did find is unrelated to shading and larger than anything the
> dispersion number was pointing at: **the reconstruction's frame sits a uniform
> half pixel up and left of retail's**, `dy = +0.50, dx = +0.50`, identical in
> every block of the image. Correcting it by resampling alone — a strictly
> pessimistic stand-in for re-rendering — moves the **terrain mid-band from
> 72.85 % material / meanD 20.3 to 67.11 % / 17.1** and the **FULL FRAME from
> 52.20 % / 20.7 to 49.22 % / 19.0**.
>
> **No renderer source was changed by this work.** The offset is frame-global —
> it moves the sky too — so it does not belong in the terrain shader, and the
> fix is left to the owner of the camera/viewport path.

Tool: [`tools/terrain_spatial_structure_probe.py`](../../tools/terrain_spatial_structure_probe.py).
Frames: retail `hud-timeline-run1/level100-t025065ms.png`; reconstruction and the
`macro`/`mask` probes from the `ambient-light-after` / `al-probe-*` captures
recorded in
[the ambient-light implementation](terrain-ambient-light-applied-2026-07-26.md).

## 1. The spectrum: there is no missing high-frequency term

Averaged over every fully-terrain 48x48 window (36 of them at step 16), power of
`pixel / window mean - 1`, Hann-windowed, integer frame shift only:

| band (cycles/px) | <0.05 | 0.05–0.1 | 0.1–0.2 | 0.2–0.3 | 0.3–0.4 | 0.4–0.5 | \|fy\|>0.3 | \|fx\|>0.3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| retail | 804.4 | 81.03 | 24.80 | 5.909 | 2.170 | 0.830 | 6.661 | 0.0409 |
| reconstruction | 740.5 | 74.60 | 23.04 | 6.001 | 2.080 | 0.843 | 6.550 | 0.0479 |
| macro probe | 910.9 | 92.29 | 27.68 | 7.183 | 2.600 | 1.060 | 8.312 | 0.0577 |
| **retail / ours** | **1.09** | **1.09** | **1.08** | **0.98** | **1.04** | **0.98** | **1.02** | **0.85** |

**The reconstruction reproduces retail's terrain spatial power at every
frequency.** A missing detail-texture stage, a wrong mip or LOD bias, a
per-vertex term, or a macro cache we sample through a mip chain retail does not
have would all show as retail power exceeding ours in the right-hand bands. None
does. The two frames also agree on the strong anisotropy — near-Nyquist energy is
~160x larger along y than along x in both, which is the foreshortened terrain
surface, and the ratio there is 1.02.

Candidate 4 of the brief ("does Godot mip our macro?") is dead on the source as
well as the spectrum: `Level100TerrainAppearanceAsset.CreateRgb565Texture` builds
every landscape cache image with `useMipmaps: false`, which is retail's own
one-level `D3D_CreateTexture` contract.

### The trap this measurement sets

A bilinear half-pixel shift has frequency response `|cos(pi f)|`, which is **zero
at Nyquist**. Any comparison that sub-pixel-aligns one of the two frames before
taking a spectrum annihilates exactly the content the spectrum is about. Doing
that produced an apparent "retail carries 4.7x our near-Nyquist power, 6.6x along
y, uniform across all 34 clean windows" — a completely convincing false positive
that survived a minification-dependence check and only died when the resampling
was removed. The probe takes spectra on integer-shifted frames for this reason.

## 2. Where the dispersion actually lives

| | mean | sd | sd/mean | median | robustSD (IQR/1.349) | robust/median |
| --- | --- | --- | --- | --- | --- | --- |
| retail | 1.405 1.298 1.077 | 0.536 0.418 0.338 | 0.382 0.322 0.314 | 1.389 1.310 1.086 | 0.164 0.147 0.111 | **0.118 0.112 0.102** |
| reconstruction | 1.382 1.261 1.046 | 0.136 0.097 0.064 | 0.099 0.077 0.061 | 1.373 1.268 1.044 | 0.086 0.105 0.077 | **0.063 0.083 0.073** |

Retail's tails are enormous — `p01 = -0.04 / 0.04 / 0.24`, `p99 = 3.03 / 2.30 /
1.83` — while ours span 1.17–2.02. Replacing `sd` with the same quantity
estimated from the interquartile range takes the ratio from **3.9x / 4.2x / 5.1x
down to 1.9x / 1.3x / 1.4x**, and in green the two distributions are already
within 35 %.

Localisation of retail's red-channel gain variance:

- `|z| > 4` outliers are **9.54 % of pixels and 87.7 % of the variance**.
- Their density falls monotonically with distance from the terrain silhouette:
  **16.1 %** at 1 px from an edge, 12.6 % at 2 px, 10.9 % at 3–4 px, 9.1 % at
  5–8 px, 4.3 % at 9–12 px, **1.4 % beyond 12 px**.
- 29.3 % of terrain pixels fall inside the HUD/cockpit region boxes but 35.7 % of
  the outliers do.

A shading term missing from a surface produces variance *on* the surface. This
variance is on the surface's **boundary**, where the mask (built from *our*
render) and retail's content need not describe the same object, and where a
sub-pixel offset does the most damage. In the clean interior — outside the HUD
boxes and more than 12 px from any silhouette, 8,980 pixels — retail's gain
`sd/mean` is 0.085 / 0.089 / 0.090 against ours 0.053 / 0.060 / 0.051, and
robustly 0.066 / 0.070 / 0.073 against 0.054 / 0.067 / 0.049.

**The "three times" figure should not be used again.** It is one non-robust
statistic on a ratio whose denominator is a small measured number, dominated by
boundary pixels.

## 3. The real defect: a uniform half-pixel offset

High-pass (pixel minus its 3x3 mean) correlation between the two frames over all
terrain pixels, as the reconstruction's frame is moved by fractional amounts:

```
        dx -1.00  -0.50  +0.00  +0.50  +1.00
  dy+0.00   0.231  0.283  0.295  0.318  0.295
  dy+0.25   0.331  0.417  0.429  0.471  0.429
  dy+0.50   0.409  0.530  0.540  0.604  0.539     <- peak
  dy+0.75   0.338  0.436  0.457  0.501  0.455
  dy+1.00   0.242  0.311  0.336  0.361  0.333
```

Peak **0.604 at `dy = +0.50, dx = +0.50`**, against 0.295 unshifted.

**Control, because the peak sits at the most-blurring shift available and a blur
can flatter a correlation:** applying the *same* `+0.50, +0.50` to the **retail**
frame instead drives the correlation to **-0.036**, and applying `-0.50, -0.50`
to retail raises it to **+0.582**. Blurring both equally and then sweeping the
net offset still peaks at `+0.5` (0.584) over 0 (0.495). The offset is real and
its sign is fixed: **our image must move down and right**.

It is also **uniform**. Estimated independently in 64x128 blocks over the whole
terrain, every block that has enough pixels returns `(+0.50, +0.50)` at 0.25-px
resolution — 14 of 15, the exception being a 0.22-correlation corner block. A
projection or field-of-view error would vary across the frame; a constant offset
in both axes at exactly half a pixel is the Direct3D 9 pixel-centre convention,
against which a modern rasteriser places the same geometry half a pixel up and
left.

The current comparison shift of `-1,0` is therefore **half a pixel too far in x
and half a pixel short in y**.

### What correcting it is worth

Resampling our existing frame by `+0.5, +0.5` and re-scoring. This **understates**
the prize: bilinear resampling blurs the frame it corrects, where re-rendering
with the offset would not.

| region | current | resampled +0.5,+0.5 |
| --- | --- | --- |
| FULL FRAME | 52.20 % / 20.7 | **49.22 % / 19.0** |
| terrain mid-band | 72.85 % / 20.3 | **67.11 % / 17.1** |
| horizon ridge | 51.41 % / 15.3 | 48.30 % / 12.9 |
| threat circle | 59.15 % / 20.2 | 57.02 % / 17.8 |
| message panel | 57.86 % / 26.3 | 56.07 % / 20.7 |
| sky | 18.54 % / 6.5 | 19.02 % / 6.3 |
| cockpit frame (left) | 80.27 % / 35.5 | 80.01 % / 34.6 |

The sky moving at all is the cross-check that this is not a terrain effect: the
sky is already the closest region in the frame and its `changed%` still falls
from 84.13 to 76.93. **The fix belongs in the camera/viewport path, not in the
terrain shader**, and it is not applied here.

## 4. Also eliminated on the way

- **Retail's back buffer is not 16-bit.** The retail frame carries 253 / 251 / 247
  distinct values per channel with no `RGB565` step, so neither quantisation nor
  dithering contributes high-frequency energy. (Consistent with the earlier sky
  finding that 21.73 % of retail's sky pixels are exact shipped texels.)
- **Minification is not the mechanism.** From the `uv`/`uvfine` probes, a screen
  pixel spans 0.008–0.36 world units over almost the whole terrain, so the detail
  texture (1 texel per world unit) is **magnified 3–120x**, not minified. Mip
  selection and LOD bias cannot flatten a magnified texture, and the shipped
  detail DDS does carry a 10-level chain, so retail has the same option we do.
  The macro cache selects level 4 for 61,951 of 80,252 terrain pixels and level 0
  for none.
- **The capture is not downscaled.** `FrontendCaptureRig` renders and reads back
  at native 640x480 with content scaling disabled; there is no resample between
  the renderer and the PNG.

## Reproduce

```powershell
$retail = 'local-lab/retail-reference-pristine/level100-gameplay/hud-timeline-run1/level100-t025065ms.png'
py -3 tools/terrain_spatial_structure_probe.py --retail $retail `
  --rebuild     local-lab/godot-captures/ambient-light-after/level100-t025065ms.png `
  --macro-probe local-lab/godot-captures/al-probe-macro/level100-t025065ms.png `
  --mask-probe  local-lab/godot-captures/al-probe-mask/level100-t025065ms.png `
  --regions rebuild/tools/gameplay-regions-level100.json --shift 0,0
```

## Gates

**No product source was modified**: this work adds one analysis script under
`tools/` and this document. `Level100TerrainAppearanceAsset.cs`,
`Level100TerrainCompositor.cs`, every shader string, and every pinned artefact are
byte-unchanged, so the terrain gain stays at 1.384 / 1.266 / 1.049 and the
`stateHash`, the 13 startup shots and the 319 prepared assets are untouched by
construction.
