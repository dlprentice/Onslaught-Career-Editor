# The player camera, the cockpit attach, and what `HFOV` means

Date: 2026-07-26. Every address below is in the pristine Steam specimen
(`SHA-256 74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750`),
read read-only from the live maintainer Ghidra database and from the image bytes
via `tools/pe_read_va.py`. Nothing was renamed or written.

This answers a specific question: does retail place the player camera from the
authored `Camera01` node in `m_cockpit2.msh.aya`, and what is that node's
`HFOV = 180.0`?

## Summary of verdicts

| Question | Verdict |
| --- | --- |
| Does retail attach the camera to a mesh camera node? | **No.** The camera is the Battle Engine's own origin and orientation. |
| Where is the cockpit mesh placed? | At the Battle Engine origin — **the same point as the camera** — plus a shake offset. |
| Is `HFOV` loaded on PC? | **Yes**, into a per-hierarchy-frame float array at `CMeshPart+0xcc`. |
| Is it consumed? | **Only** by the in-mesh movie/cutscene camera. Nothing in the cockpit or gameplay path reads it. |
| What does `180.0` mean? | `zoom = fov/90/2`, and `tan(hfov/2) = zoom`. `180.0 -> zoom 1.0`, which is exactly the default gameplay projection. |
| Are `CPOS`/`CORI` live? | Read from the file, then **overwritten** at load by `CMeshPart::CacheFrameData`. Functionally dead. |

## 1. The projection

`CDXEngine__SetProjectionMatrix` (`0x00550b10`) builds

```
proj[0][0] = near_z / viewport_w
proj[1][1] = near_z / viewport_h
proj[2][2] = far_z / (far_z - near_z)
proj[3][2] = -(near_z * far_z) / (far_z - near_z)
```

`CDXEngine__Render` (`0x0053e2e0`) makes exactly two calls to it — the sky pass
and the world pass — and **no third call for the cockpit**, so the cockpit is
drawn under the world projection. Disassembly of the world call at `0x0053e670`:

```
0053e638  MOV  EDX, [EBP + 0x430]        ; mNearZ
0053e63e  MOV  [ESP + 0x24], EDX
0053e644  CALL dword ptr [EAX + 0x18]    ; camera vtable slot 6 = GetAspectRatio
0053e647  FMUL float ptr [ESP + 0x38]    ; * zoom
0053e64c  FMUL float ptr [EBP + 0x430]   ; * mNearZ   -> viewport_h
0053e655  FLD  float ptr [ESP + 0x28]    ; mNearZ
0053e659  FMUL float ptr [ESP + 0x3c]    ; * zoom     -> viewport_w
0053e665  PUSH 0x442f0000                ; far = 700.0
0053e670  CALL 0x00550b10
```

So `viewport_w = near*zoom`, `viewport_h = near*zoom*aspect`, therefore

```
tan(hfov/2) = zoom
tan(vfov/2) = zoom * aspect
```

`CCamera__GetAspectRatio` (`0x0041b070`) returns `_DAT_005d85ec` in multiplayer
and `_DAT_005d8bc4` otherwise. Image bytes:

| VA | file offset | bytes | value |
| --- | --- | --- | ---: |
| `0x005d8bc4` | `0x001d8bc4` | `00 00 40 3f` | **0.75** (single player) |
| `0x005d85ec` | `0x001d85ec` | `00 00 00 3f` | 0.5 (multiplayer) |

`zoom` is `CCamera::GetZoom`, vtable slot 4. `CThingCamera`'s implementation
(vtable `0x005DBB88` slot 4 -> `0x00418eb0`) reads `[EAX + 0x2c8]` — the Battle
Engine's `mZoom`. Its initial value and its two bounds are all immediates:

| Site | Instruction | Value |
| --- | --- | --- |
| `CBattleEngine__Init` `0x0040555d/63/69` | `mZoom = mDesiredZoom = mOldZoom = EDI` | `0x3f800000` = **1.0** |
| `CBattleEngine__ZoomOut` `0x00409eab` | `mDesiredZoom = 0x3f800000` | **1.0** (`MAX_ZOOM_OUT`) |
| `CBattleEngine__AutoZoomOut` `0x00409e80` | same | 1.0 |
| `CBattleEngine__Morph` `0x0040a5fd` | same | 1.0 |
| `CBattleEngine__AugmentWeapon` `0x0040dee7` | same | 1.0 |
| `CBattleEngine__ZoomIn` `0x00409edb` | `mDesiredZoom = 0x3ecccccd` | **0.4** (`MAX_ZOOM_IN`) |

**Unzoomed gameplay is therefore `zoom = 1.0`, `aspect = 0.75`:**

```
hfov = 2*atan(1.00)   = 90.000000 degrees
vfov = 2*atan(0.75)   = 73.739795 degrees
```

at any resolution — the 0.75 is a fixed constant, not a viewport ratio, so at
640x480 it happens to be square-pixel correct.

### Correction to a previously circulated number

The figure "retail horizontal FOV = 73.71 degrees" originates in
`local-lab/ADVERSARIAL-GODOT-VIABILITY-2026-07-25.md:217`, where it is *derived
from the reconstruction's own* `Fov = 58.7155f` by widening 58.7155 vertical to
4:3. It was never a retail measurement. `tan(58.7155/2) = 0.5625 = 0.75 * 0.75`,
i.e. the reconstruction applied the 0.75 aspect factor to the horizontal axis as
well. Retail's vertical FOV is `2*atan(0.75)`, not `2*atan(0.75*0.75)`.

## 2. The camera-attach convention

`CThingCamera::GetPos` is `0x00418cd0` (`CThingCamera` vtable `0x005DBB88`
slot 0). Disassembled:

```
00418cd0  MOV EAX, [ECX + 0x4]           ; mForThing
00418cda  LEA ECX, [EAX + 0x1c]          ; thing->mPos
00418cf2  MOV CL, byte ptr [EAX + 0x34]  ; thing type flags
00418cf5  TEST CL, 0x8                   ; THING_TYPE_BATTLE_ENGINE
00418cf8  JNZ 0x00418d29                 ; -> return mPos verbatim
          ... else: pos.Y += bbox.Y * 1.5   (0x005d8bd8 = 1.5)
          ...       pos.Z -= bbox.Z
```

matching `Camera.cpp:41-56` in the pinned reference source exactly. For the
Battle Engine the camera position is `mPos` with **no offset of any kind**, and
`CThingCamera::GetOrientation` returns the thing's orientation unchanged.

The cockpit is not the camera's parent; it is a render thing whose transform is
supplied through the second base class of `CCockpit` (vtable `0x005d8838`,
installed at `CCockpit+8`):

- **slot 0, `0x00425430` — position.** `[ESI+0x108]` is `mBattleEngine`
  (`CCockpit+0x110`, stored by `CCockpit__ctor` at `0x004244b0`).

  ```
  new = cockpitShake(+0x0c..0x14) + battleEngine->mPos(+0x1c..0x24)
  old = cockpitOldShake(+0x1c..0x24) + battleEngine->GetOldPos()   ; vtable +0x78
  out = old + (new - old) * DAT_008a9e44                            ; frame render fraction
  ```

- **slot 1, `0x004254f0` — orientation.** Composes the cockpit's own 3x4 shake
  matrix (`CCockpit+0x2c`, seeded to identity in the constructor and updated by
  `0x00424ca0` / `0x004250f0`) onto `battleEngine+0x3c`, the same orientation
  the camera returns, and interpolates the same way.

**So with no shake the cockpit mesh origin is exactly the camera position and
its orientation is exactly the camera orientation. The retail attach offset is
zero.** `Camera01`'s `CPOS (0.006004, -0.002597, 0)` is authoring slop about the
mesh origin, consistent with — but not the source of — that convention.

`CCockpit::Render` is `0x0053bb50` (currently misnamed
`CDXEngine__RenderOptionalFullscreenEffectPass` in the database; its caller is
`CDXEngine__Render+0x98a` at `0x0053ec6a`, with `ECX = battleEngine+0x528` =
`mCockpit`). It gates on `mShouldRender` (`CCockpit+0x12c`, set to 1 in the
constructor), computes a fade byte into `DAT_0063012c`, and dispatches the
render thing's slot-2 virtual. It sets no matrices.

## 3. `HFOV` is loaded, and what it means

There is **no `HFOV` string and no `HFOV` 4CC immediate anywhere in the image** —
but the mesh chunk reader is positional, not tag-driven. `CMeshPart__LoadFromStream`
(`0x004b27a0`) calls `CChunkReader__GetNext` and reads immediately, comparing the
returned tag in only two places, against the literals `'HORI'` at `0x00630038`
and `'CORI'` at `0x0063000c` (both present in the image as plain ASCII). The
keyframe block is:

| Order | Guard | Read | Field | Debug allocation name |
| --- | --- | --- | --- | --- |
| 1 | tag == `HORI` | `0x30 * [0xbc]` | `+0x10c` | — |
| 2 | `[0xc8] != 0` | `0x10 * [0xbc]` | `+0xc8` | — |
| 3 | `[0xcc] != 0` | `0x04 * [0xbc]` | `+0xcc` | **`Meshes/%s/Part %d/FOV data`** (`0x00630080`, referenced at `0x004b2936`) |

`[0xbc]` is the hierarchy-frame count. The order `HORI, HPOS, HFOV` is exactly
the chunk order in `m_cockpit2.msh.aya`. The old-style path in `CMesh__Load`
does the same thing explicitly:

```
004a66a1  CMP dword ptr [EBX + 0x8c], 0x4     ; part type 4 == "[camera]"  (0x0062fbb0)
004a66a8  JNZ ...
004a66b1  PUSH 0x4 ; read 4 bytes
004a66bb  MOV EDX, [EBX + 0xcc]               ; FOV array
004a66cf  FSTP float ptr [EDX + EAX*0x4]      ; FOV[frame] = value
```

So on PC the `HFOV` chunk becomes `CMeshPart+0xcc`, one float per hierarchy
frame, on camera-type parts.

### Its only consumer

Sweeping every instruction in the image for a non-stack `[reg + 0xcc]` reference
inside mesh code gives exactly one *reader* outside load/init/clone/free:

```
004dc09b  CALL 0x004b0fb0                 ; compose the camera part's pose for a frame
004dc0a0  MOV EAX, [EDI + 0xc4]           ; VHFM  (virtual -> hierarchy frame map, 1 byte/frame)
004dc0a6  MOV EDX, [EDI + 0xcc]           ; FOV array
004dc0af  MOV CL, byte ptr [EAX + ESI*1]  ; h = VHFM[virtualFrame]
004dc0b5  MOV EAX, [EDX + ECX*0x4]        ; fov = FOV[h]
004dc0bc  MOV [ECX], EAX                  ; *out_fov
```

inside `CRTCutscene__BuildCurrentFrameOutputs` — the `GetMovieCameraPosition`
virtual. Its caller is `CMovieCamera__GetZoom` (`0x0041a630`):

```
zoom = fov * _DAT_005d9338 * _DAT_005d85ec
     = fov * 0.011111111 * 0.5
     = (fov / 90) / 2
```

(`0x005d9338` = `61 0b 36 3c` = `0.0111111114`; `0x005d85ec` = `0.5`), matching
`Camera.cpp:650` in the reference source.

### Therefore `HFOV = 180.0` means "no zoom change"

`tan(hfov_rendered/2) = zoom = fov/180`. With `fov = 180.0`, `zoom = 1.0` — bit
for bit the Battle Engine's default. `m_cockpit2.msh.aya` part 8 `Camera01` has
`hFrames = 1`, a single `HFOV` float of `180.0`, and a `VHFM` of 51 zeros, so
every virtual frame maps to it. The authored value is not a horizontal field of
view in degrees; it is the parameter of an engine mapping whose fixed point at
180 is the default projection.

**It is also dead for this mesh.** The consumer is the cutscene render-thing
path; the cockpit is a `CCockpit` render thing drawn under the world projection,
and `CBattleEngine::mZoom` is what reaches `SetProjectionMatrix`.

## 4. `CPOS` / `CORI` are loaded and then overwritten

`CMeshPart__LoadFromStream` reads the file's `CPOS` into `+0x104`
(`0x10 * [0x118]`, allocation name `Meshes/%s/Part %d/Position cache`) and,
guarded by a `'CORI'` tag compare, the file's `CORI` into `+0x108`
(`0x30 * [0x118]`, `.../Orientation cache`).

`CMesh__Load` then calls `CMeshPart__CacheFrameData` (`0x004b1a40`) at
`0x004a96dc`. That function **reallocates both arrays** and refills them from
`CMCMech__BuildInterpolatedPoseAndAnchor` for every cached frame — the composed
hierarchy pose. It also short-circuits them away entirely when the local
transform is identity (`+0x120`) or the local position is zero (`+0x11c`).

So the shipped `CPOS`/`CORI` bytes are consumed by nothing: they are recomputed
before first use. `tools/cmsh_cpos_cori_verify.py` already established that they
equal the composed `HORI`/`HPOS` chain, which is why the substitution is
invisible.

## 5. Measured against retail

Both values above were applied to the reconstruction — `Fov 58.7155 -> 73.739795`
and the cockpit root offset `(0, -0.01, -0.06) -> (0, 0, 0)` — and the gameplay
plan was recaptured at 640x480 against retail's realised level offsets
(`local-lab/retail-reference-pristine/level100-gameplay/manifest.json`), then
compared with `tools/compare_capture.py` and
`rebuild/tools/gameplay-regions-level100.json`.

At retail offset `t0+25065 ms`, `material% / meanD`:

| Region | baseline | offset only | FOV only | **both** |
| --- | --- | --- | --- | --- |
| FULL FRAME | 88.62 / 45.5 | 88.15 / 48.1 | 72.27 / 40.8 | **63.81 / 26.5** |
| sky | 72.03 / 32.9 | 71.28 / 29.5 | 55.77 / 49.6 | **18.54 / 6.5** |
| horizon ridge | 89.65 / 34.3 | 89.65 / 34.3 | 63.11 / 17.4 | **63.16 / 17.5** |
| terrain mid-band | 93.98 / 47.1 | 93.98 / 47.1 | 91.20 / 35.6 | **91.15 / 35.4** |
| cockpit frame (left) | 96.52 / 65.0 | 97.04 / 67.2 | 93.96 / 50.7 | **80.36 / 34.9** |
| cockpit frame (right) | 96.03 / 50.6 | 90.73 / 36.1 | 95.00 / 42.9 | **94.73 / 45.9** |
| threat circle | 89.45 / 40.6 | 89.45 / 40.6 | 67.16 / 27.0 | **67.16 / 27.0** |

Whole-frame cockpit-dark mask agreement against retail
(`tools/cockpit_edge_profile.py`, intersection over union):

| | baseline | offset only | FOV only | **both** |
| --- | ---: | ---: | ---: | ---: |
| dark pixels (retail 72,642) | 58,595 | 42,765 | 123,635 | **78,268** |
| IoU | 0.3235 | 0.2420 | 0.4579 | **0.5763** |

Neither change is sufficient alone, and each alone is worse than the pair on at
least one axis: at the old narrow FOV the `-0.06` forward offset partly
compensated for the missing width, and at the correct FOV that same offset makes
the cockpit swallow the sky (123,635 dark pixels against retail's 72,642). This
is what a compensating pair of fitted constants looks like from the outside.

The same improvement holds across the timeline rather than at one offset —
FULL FRAME `material% / meanD`, baseline -> both:

| offset | baseline | both |
| --- | --- | --- |
| t0+16060 ms | 88.36 / 42.1 | 62.89 / 22.5 |
| t0+20080 ms | 88.65 / 43.4 | 63.76 / 27.2 |
| t0+30071 ms | 88.63 / 45.1 | 64.02 / 25.9 |
| t0+42062 ms | 89.05 / 46.9 | 65.07 / 28.4 |

The sky region is the cleanest single read: `72.03% / 32.9` -> `18.54% / 6.5` at
every sampled offset. That is a field-of-view result, not a shading one.

The opening pan improves by the same margin, which is expected:
`CPanCamera::GetZoom` also returns 1.0 (`Camera.h:126`), so the pan runs on the
same projection. FULL FRAME `material% / meanD` against
`opening-pan-run1`, baseline -> both: t0+2 ms `94.05 / 48.0` -> `70.24 / 25.0`;
t0+256 ms `94.08 / 48.4` -> `81.29 / 29.0`; t0+499 ms `94.68 / 49.5` ->
`84.53 / 31.3`; t0+749 ms `95.63 / 50.2` -> `86.33 / 32.8`.

### One gate flips, and it is a proxy

`Level100WaterEnvelopeTests.CapturedWaterStaysInsideTheRetailEnvelope` fails on
the corrected capture: pooled `B > G > R` fraction falls to 75.1% in
`open-sea-right` and 67.2% in `mid-sea` against its 86-95% band. In the **same
three rectangles at the same four offsets**, direct agreement with retail
improves substantially — at t0+499 ms, `material% / meanD`:

| box | baseline | both |
| --- | --- | --- |
| open-sea-right | 72.47 / 19.6 | **50.71 / 14.4** |
| caustic-band | 77.83 / 24.4 | **66.25 / 18.7** |
| mid-sea | 85.41 / 23.6 | **26.14 / 6.1** |

So the water in those boxes moved closer to retail's pixels while a smaller
fraction of them satisfy a strict channel ordering. Retail's own `mid-sea` reads
`(90.3, 92.2, 110.0)` there — green is 1.9 above red, so the ordering flips on
noise. Retail's own `open-sea-right` fraction is 65.6% at t0+749 ms, below the
gate's own floor; the 88.1% figure it pins is the four-offset pool.

This note does not change that test — the water lane owns it. It records that
the hue-ordering statistic and direct retail agreement now disagree in sign, and
that the second is the one measured against retail pixels.

## What this does not establish

The shake law in `0x00424ca0` / `0x004250f0`, the fade computation in
`0x0053bb50`, the cockpit lighting model, and any runtime value of `mZoom`
during a specific captured frame are static reads only. No process was launched
for this note.
