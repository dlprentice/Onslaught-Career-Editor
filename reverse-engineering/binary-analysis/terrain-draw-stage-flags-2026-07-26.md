# Terrain draw — texture-stage flags, and the falsification of both settings

> Verdict: `CDXLandscape__RenderTerrain` has exactly **one** unmodelled degree of
> freedom, `D3DStateCache__SetSlotMode4or5`, which selects `D3DTOP_MODULATE` or
> `D3DTOP_MODULATE2X` from a single global. **Both settings are falsified by
> measurement.** `MODULATE` bounds the draw's output at or below the macro texel;
> retail measures 1.40x it. `MODULATE2X` on stage 0 was built and captured and
> measures 1.855 / 1.753 / 1.502 against retail's 1.400 / 1.295 / 1.075 — a 33 to
> 40 percent overshoot. No gain was applied. The terrain draw is now exhausted as
> the source of retail's terrain brightness.

Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`,
2,506,752 bytes — the **capture target**: pristine plus the
`force_windowed` patch and nothing else.
*(Corrected 2026-07-28. This line previously read "`BEA.exe`, SHA-256
`e1436ef7…`, 2,506,752 bytes (local pristine safe copy)". `e1436ef7` is **not** pristine —
the pristine specimen is `BEA.exe.original.backup`, SHA-256 `74154bfa…`, in
the same directory; see
[`retail-specimen-baseline.md`](retail-specimen-baseline.md) and
[`retail-capture-provenance-2026-07-25.md`](retail-capture-provenance-2026-07-25.md),
which records that the two file names are inverted in that directory.
Re-measured 2026-07-28: the two builds differ at exactly **four** bytes,
file offsets `0x12a644`–`0x12a647` = VA `0x0052a644`–`0x0052a647`
(`a1 f0 2d 66 00` → `b8 01 00 00 00`). No address cited anywhere in this
note falls in that range — the nearest are `0x00513b61` below and `0x00540010`
above — and no disassembly quoted here decodes through it, so **every byte
claim below stands unchanged.** This is a specimen-label correction, not a
re-measurement.)*
Image base `0x00400000`;
`.text` VA `0x00401000`, file offset `0x1000`.

## 1. `CDXEngine__InitLandscapeTextureTables` @ `0x00542740` is a thunk

Two instructions: it forwards `ECX` to the base-init helper currently labelled
`0x00481400` and returns it. It sets no render state, creates no texture, and
touches no landscape colour. Eliminated outright.

## 2. `CDXLandscape__RenderTerrain` @ `0x00545590` — complete stage-argument census

The body's only texture-stage colour arguments are, by `D3DTSS` id:

| `D3DTSS` id | meaning | values used |
| --- | --- | --- |
| 1 | `COLOROP` | `4` (`MODULATE`) raw, or via `SetSlotMode4or5`, or `1` (`DISABLE`) |
| 2 | `COLORARG1` | `2` = `D3DTA_TEXTURE` only |
| 3 | `COLORARG2` | `0` = `D3DTA_DIFFUSE` (stage 0) or `1` = `D3DTA_CURRENT` (stages 1-3) |
| 4 | `ALPHAOP` | `1` (`DISABLE`) or `2` (`SELECTARG1`) |
| 5, 6 | `ALPHAARG1/2` | `2` = `TEXTURE`, `0` = `DIFFUSE`, `1` = `CURRENT` |
| 11 (`0x0b`) | `TEXCOORDINDEX` | `0..3` |
| 24 (`0x18`) | `TEXTURETRANSFORMFLAGS` | `0` or `2` |

Consequently, and against the specific candidates the previous pass named:

- **No `D3DRS_TEXTUREFACTOR`.** `RenderState_Set` is `SetRenderState` — confirmed
  by `CDXTrees__Render`'s `RenderState_Set(0x13,5)` / `(0x14,6)` / `(0x1b,0)` /
  `(0x0f,1)` = `SRCBLEND=SRCALPHA`, `DESTBLEND=INVSRCALPHA`,
  `ALPHABLENDENABLE=0`, `ZWRITEENABLE=1`. `RenderTerrain` never issues state
  `0x3c`.
- **No `D3DTA_TFACTOR`.** No `COLORARG` in the function takes the value `3`.
- **No `D3DTA_COMPLEMENT`.** No argument carries the `0x10` flag bit.
- **No second draw over the same geometry.** The sole caller
  `CDXLandscape__Render` @ `0x00545410` calls `RenderTerrain` exactly once, and
  the draws inside it are the base grid (`CEngine__DrawIndexedPrimitives(...,
  0x1081, ...)`, `0x1081` = 65x65 vertices) plus the disjoint LOD-tile loop.
- **No per-vertex colour.** The tile loop indexes vertices at stride `0x14` = 20
  bytes = position + one texture coordinate pair. Stage 0's `COLORARG2` is
  `D3DTA_DIFFUSE`, which with no `D3DFVF_DIFFUSE` and lighting suppressed is
  opaque white.
- The `vtable+0xb0` calls with `0x10`..`0x13` are `SetTransform(D3DTS_TEXTURE0..3,
  &DAT_00628258)` — texture matrices, not colour. Stage 0's scale is
  `0.001953125` = 1/512, stage 2's is `0.00390625` = 1/256 with the accumulated
  cloud scroll, stage 3's is the fixed rotation the reconstruction already
  models.

## 3. The one unmodelled degree of freedom

`D3DStateCache__SetSlotMode4or5` @ `0x00513af0`:

```
0x00513af0   a1 fc 54 85 00      MOV EAX, [0x008554fc]
```

It writes `(&DAT_008557f4)[slot*0x1e]` and calls device vtable `+0x10c` with
`(slot, 1, value)`. `D3DStateCache__SetStateRaw` @ `0x00513870` writes
`(&DAT_008557f0)[state_id + slot*0x1e]` through the same vtable slot, so
`0x008557f4` is `state_id == 1` and the helper is exactly

```
SetTextureStageState(slot, D3DTSS_COLOROP,
                     DAT_008554fc ? D3DTOP_MODULATE2X : D3DTOP_MODULATE)
```

`RenderTerrain` applies it to stage 0 (in the two- and one-texture blocks) and to
stages 2 and 3; `CDXLandscape__Render` applies it to stages 0 and 1 before
calling in. In the four-texture block stage 0 is instead set raw to `4` when the
flag is zero, so the flag is the only thing that can lift any stage above 1x.

Two independent corroborations of the semantics:

- `CDXFont__DrawTextScaled` @ `0x00540010`, at `0x0054034c` and `0x005403ac`,
  takes the `DAT_008554fc == 0` branch to **double the vertex colour in
  software** — `(argb >> 0xf) & 0x1fe`, `(argb >> 7) & 0x1fe`, `(argb & 0xff) * 2`,
  each clamped to `0xff` — and skips that doubling entirely when the flag is set.
  The flag means "the hardware will do the 2x for me".
- `CDXTrees__Render` @ `0x0055aa10`, at `0x0055ab4f`, uses `SELECTARG1` on the
  zero branch and `TEXTUREFACTOR = 0xFFFFFFFF` + `COLORARG2 = D3DTA_TFACTOR` +
  `SetSlotMode4or5` on the non-zero branch. That is the only `TFACTOR` use in the
  landscape/tree render path, and it is not on terrain.

### The flag has no absolute writer

`0x008554fc` lies in the **uninitialised tail of `.data`** (`pe_read_va.py`
refuses it). An exhaustive whole-file scan for the little-endian operand
`fc 54 85 00` returns exactly six occurrences, and every one is a read:

| VA | bytes | function |
| --- | --- | --- |
| `0x00513af1` | `a1 fc 54 85 00` | `D3DStateCache__SetSlotMode4or5` |
| `0x00513b61` | `a1 fc 54 85 00` | `D3DStateCache__ForceSlotMode4or5` |
| `0x0054034e` | `8b 15 fc 54 85 00` | `CDXFont__DrawTextScaled` |
| `0x005403ae` | `8b 15 fc 54 85 00` | `CDXFont__DrawTextScaled` |
| `0x00545650` | `39 2d fc 54 85 00` | `CDXLandscape__RenderTerrain` |
| `0x0055ab50` | `a1 fc 54 85 00` | `CDXTrees__Render` |

This does **not** prove the flag is zero — the `CMixerMap` precedent
([shade plane note](terrain-shade-plane-origin-2026-07-26.md)) is a global whose
member had no absolute writer either, because it was reached through a base
pointer. Section 4 settles the value by output instead.

## 4. Both settings are falsified against retail output

Measurement frame: retail `level100-t025065ms.png`
(`hud-timeline-run1`), reconstruction at the same deterministic offset, paired
per pixel at the aligned `dx = -1`, fog removed analytically, 71,426 usable
terrain pixels. Retail's transfer function against the macro cache:

```
retail / macro       1.400   1.295   1.075
```

**`MODULATE` everywhere is impossible.** On that setting every stage is a product
of values each in `[0,1]` — four texture samples and an opaque-white `DIFFUSE` —
so the draw's output can never exceed the stage-0 macro texel. Retail measures
**1.40x** it. The flag cannot be zero.

**`MODULATE2X` on stage 0 overshoots.** The flag being non-zero forces stage 0 to
`MODULATE2X`, which the reconstruction did not model (it already modelled stages
2 and 3 as 2x). Built and captured with `min(macro * 2, 1)` at stage 0:

```
retail / macro                 1.400   1.295   1.075
reconstruction, stage-0 2x     1.855   1.753   1.502     (+33% / +35% / +40%)
reconstruction, as shipped     1.047   1.017   0.978     (-25% / -21% /  -9%)
```

Per macro-luminance bin the overshoot is flat and unambiguous — `b/m` runs
1.96, 1.93, 1.91, 1.91 across the bins where retail runs 1.38, 1.38, 1.34, 1.35.
The change was reverted; no gain was applied.

## 5. What this leaves

Retail's measured terrain gain sits almost exactly at the geometric midpoint of
the reconstruction's two admissible stage-0 settings
(`sqrt(1.047 * 1.855) = 1.39` against 1.400). That is an observation, not a
mechanism, and nothing here licenses inserting a factor to land it.

With the compositor, the shade plane, fog, the `TEXTURE` stage chain, the
offline PS2 cache generator, and now the terrain draw's full stage-argument
census and its single flag all eliminated, the 1.36x is not produced anywhere
inside `CDXLandscape::RenderTerrain`. The remaining surface is the frame-global
one the terrain draw does not own — device gamma/brightness, the back-buffer
format and its `RGB565` quantisation, or the presentation path — which would
show up as a whole-frame effect and must be measured against a non-terrain
surface of known colour before it is believed.
