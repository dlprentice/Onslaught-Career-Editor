# The cockpit lighting law — located, decoded, and already implemented

> Verdict: **retail's cockpit lighting law is
> `COLOR1 x ( D3DRS_AMBIENT + SUM_i max(0, N.L_i) x light_i.Diffuse )`, and the
> reconstruction's `RetailFixedFunctionMaterial` vertex shader already computes
> exactly that.** No renderer change is warranted by this note. Two premises the
> search was built on are **falsified on bytes**: material `[0]`'s zero ambient
> does **not** zero the cockpit's ambient response (both material sources are
> `D3DMCS_COLOR1`, not `D3DMCS_MATERIAL`), and the cockpit's day-cycle
> invariance is **not a constraint at all** — retail's entire light state is
> level-constant, with no writer anywhere in the image. What remains open is not
> the law but the **space the cockpit's normals are in**.

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
note falls in that range — the nearest are `0x00513bc0` below and `0x0053bb50`
above — and no disassembly quoted here decodes through it, so **every byte
claim below stands unchanged.** This is a specimen-label correction, not a
re-measurement.)*
Image base `0x00400000`. All
disassembly is `capstone` linear decode of that file through
`tools/disasm_va.py`; all reference counts are whole-file little-endian operand
scans through `tools/operand_scan.py` and direct `rel32` scans through
`tools/call_xref_scan.py`. The Ghidra database was not opened or mutated.
`BEA.exe` was not launched.

## 1. Where the cockpit is actually drawn

The gameplay frame function ends at `0x0053ecb4` (`RET 4`). Its terminal
sequence is the cockpit:

```
0053eb7a  MOV  EAX, [0x0089d670]                  ; 4-dword translation
0053eb84  SUB  ESP,0x10; ECX=0xc; ESI=0x0089d640  ; 12-dword 3x4 rotation
0053eb93  REP MOVSD
0053ebb1  MOV  ECX, 0x009c65c0
0053ebb6  CALL 0x00550ca0                         ; CDXEngine::SetWorldMatrix
0053ebbb  MOV  EAX, [0x00888a50]
0053ebc0  PUSH 0x0083d248                         ; material[0]
0053ebc6  MOV  EDX, [EAX]
0053ebc8  CALL dword [EDX+0xc4]                   ; IDirect3DDevice9::SetMaterial
...
0053ec4c  MOV  ECX, 0x0089c9a0
0053ec51  CALL 0x0044a650                         ; blend/z-write setup, below
0053ec64  MOV  ECX, [ESI+0x528]
0053ec6a  CALL 0x0053bb50                         ; the cockpit draw wrapper
```

`0x0053bb50` has exactly **one** caller in the image (`call_xref_scan.py`:
`CALL at 0x0053ec6a`, total 1). It is the wrapper the task named
`CCockpit::Render`; its body is:

```
0053bb7c  PUSH 1; PUSH 0x8f; ECX=0x00855bb0; CALL 0x00513bc0  ; NORMALIZENORMALS := 1
0053bb97  ECX=[this+0x110]; CALL [vt+0x16c]                   ; a float
0053bbc3  ... 0x0063012c := 0x5d8c70 - f*0x5d8c74             ; global vertex-alpha scale
0053bbe1  ECX=[this+0x8c]; PUSH edi; CALL [vt+0x8]            ; the mesh render
0053bbed  0x0063012c := 0xff
0053bbf8  PUSH 0; PUSH 0x8f; CALL 0x00513bc0                  ; NORMALIZENORMALS := 0
```

`0x0063012c` is the same global `CMeshRenderer::RenderMeshCore` reads at
`0x005497fc` to scale the per-vertex alpha, which independently ties this
wrapper to the stride-36 mesh path.

`0x0044a650`, called at `0x0053ec51` immediately before the draw, is four
cached render-state writes:

```
0044a650  PUSH 1; PUSH 0x1b   ; D3DRS_ALPHABLENDENABLE := 1
0044a65e  PUSH 5; PUSH 0x13   ; D3DRS_SRCBLEND  := D3DBLEND_SRCALPHA
0044a66c  PUSH 6; PUSH 0x14   ; D3DRS_DESTBLEND := D3DBLEND_INVSRCALPHA
0044a67a  PUSH 0; PUSH 0x0e   ; D3DRS_ZWRITEENABLE := 0
```

(`0x00513bc0` takes `(state, value)` — first push is the value; the
`D3DRS_FOGCOLOR` write at `0x0053e5d2` with state `0x22` = 34 fixes the
convention.)

## 2. Material `[0]` contributes nothing — the material sources are `COLOR1`

`SetMaterial(0x0083d248)` at `0x0053ebc8` confirms the cockpit uses element 0 of
the two-material array decoded in
[the terrain material note](terrain-ambient-light-material-2026-07-26.md):
Diffuse `(1,1,1,1)`, Ambient `(0,0,0,1)`, Specular `0`, Emissive `0`,
Power `0.1`.

The inference that this makes the cockpit's **ambient response zero** does not
follow, because the material is not the ambient source. The engine's
render-state default block at `0x004eb2da`–`0x004eb398` sets:

```
004eb2da  PUSH 1; PUSH 0x1c   ; FOGENABLE              := 1
004eb2e8  PUSH 0; PUSH 0x1d   ; SPECULARENABLE         := 0
004eb302  PUSH 1; PUSH 0x89   ; LIGHTING               := 1
004eb313  PUSH 1; PUSH 0x1a   ; DITHERENABLE           := 1
004eb321  PUSH 2; PUSH 0x09   ; SHADEMODE              := GOURAUD
004eb32f  PUSH 1; PUSH 0x91   ; DIFFUSEMATERIALSOURCE  := D3DMCS_COLOR1
004eb340  PUSH 0; PUSH 0x92   ; SPECULARMATERIALSOURCE := D3DMCS_MATERIAL
004eb351  PUSH 1; PUSH 0x93   ; AMBIENTMATERIALSOURCE  := D3DMCS_COLOR1
004eb362  PUSH 0; PUSH 0x94   ; EMISSIVEMATERIALSOURCE := D3DMCS_MATERIAL
004eb373  PUSH 0; PUSH 0x8f   ; NORMALIZENORMALS       := 0
004eb384  PUSH 0xf0ccface; PUSH 0x8b ; AMBIENT := sentinel (forces a first write)
```

A whole-image scan for the five-byte `PUSH imm32` encodings of these states
finds no other `mov ecx, 0x00855bb0` writer of `0x93` (`AMBIENTMATERIALSOURCE`),
`0x92`, `0x94`, or `0x1d` (`SPECULARENABLE`) anywhere. `D3DRS_COLORVERTEX`
(`0x8d`) is likewise never written through the cache, so it keeps its `TRUE`
default. Therefore, for the cockpit's FVF `0x152` stream (which carries a
`DIFFUSE` dword):

- the **ambient** reflectance is the vertex colour, not `material.Ambient = 0`;
- the **diffuse** reflectance is the vertex colour;
- **specular is impossible** (`SPECULARENABLE = 0` and `material.Specular = 0`);
- **emissive is impossible** (`EMISSIVEMATERIALSOURCE = MATERIAL`,
  `material.Emissive = 0`).

`material[0]` is a no-op record for this draw. The `D3DRS_AMBIENT` register
therefore *does* light the cockpit.

`D3DRS_DIFFUSEMATERIALSOURCE` survives the terrain intact:
`CDXLandscape::Render` sets it to `D3DMCS_MATERIAL` at `0x0054548d`, and the two
landscape sub-draw epilogues at `0x005461c9` and `0x0054686a` restore it to
`D3DMCS_COLOR1` (each paired with `ALPHABLENDENABLE := 1`) before the function
returns at `0x0054555a`.

`D3DRS_LIGHTING` is `1` at the cockpit: the only cache writers that clear it are
`0x0044a690` (never reached on this path), `RenderMeshCore`'s modes 2 and 6
(`0x0054a3fe`/`0x0054a451`, each restored at `0x0054a42a`/`0x0054a46d`), the
render-target helpers at `0x0054dc91`/`0x0054de98`, and the state-flush tail at
`0x005511ce`.

## 3. The lights, and the number they carry

`CEngine::SetupLights` @ `0x0044a2d0` has exactly **one** direct caller,
`0x0053e5b8`, inside the same gameplay frame function — it runs once per frame.
It reads the HFLD sun position as three floats:

```
0044a2d6  FLD dword [0x006fbe6c] / [0x006fbe70] / [0x006fbe74]
0044a2f2  FCHS  (x3)                       ; negate
0044a326  FSQRT ... 0044a339 FDIVR         ; normalize
```

so `light0.Direction = -normalize(sunPosition)` and, by the second negation at
`0x0044a4a1`–`0x0044a4d0`, `light1.Direction = +normalize(sunPosition)`. Light
colours are unpacked byte-wise and scaled by `_DAT_005db060 = 0x3b800000 = 1/256`
(`0x0044a431`, `0x0044a457`, `0x0044a470`; and `0x0044a4f8`–`0x0044a545`), then
`REP MOVSD` of `0x17` dwords into `0x009c65c0` and `0x009c661c`. Exactly two
lights are enabled (`0x009c68a0`, `0x009c68a1` := 1 at `0x0044a52a`,
`0x0044a584`; `0x009c68a2..a7` := 0). `D3DRS_AMBIENT` is loaded from
`[0x006fbe54]` into the shadow `0x009c68a8` at `0x0044a419`, and restored there
by `CDXLandscape::Render` at `0x00545525` after the terrain zeroes it.

Outside the terrain draw the lights' `Ambient` channel is zero:
`ApplyCachedLight(i, 0)` at `0x0054554c`, and the state flush at `0x005510d9`
also passes `0`. Only `0x0054550e` passes `1`.

Reading those five HFLD fields out of the shipped
`level100-heightfield.hfld.bin` (`CHFD` payload at `0x10`):

| field | offset | value |
| --- | --- | --- |
| light 0 colour | `CHFD+0x107C` | `0xbdb179` = (189, 177, 121) |
| light 1 colour | `CHFD+0x1080` | `0x232338` = (35, 35, 56) |
| `D3DRS_AMBIENT` | `CHFD+0x108C` | `0x000d0f2b` = (13, 15, 43) |
| sun position | `CHFD+0x10A4..0x10AC` | (0.0340740, 0.9086333, −0.4162026), unit length |

## 4. The law

```
C_vertex = COLOR1 x ( D3DRS_AMBIENT
                    + max(0, N.L0) x light0.Diffuse
                    + max(0, N.L1) x light1.Diffuse )

  D3DRS_AMBIENT   = (13,15,43)/255
  light0.Diffuse  = (189,177,121)/256 ,  L0 = +normalize(sunPosition)
  light1.Diffuse  = (35,35,56)/256    ,  L1 = -normalize(sunPosition)
  COLOR1          = the FVF 0x152 per-vertex DIFFUSE dword
```

`rebuild/OnslaughtRebuild.Godot/Level100StaticWorldAsset.cs`'s
`RetailFixedFunctionMaterial` vertex stage already computes this term for term
(`ambient_color + sun_color*sun + anti_sun_color*anti_sun`, then
`*= COLOR.rgb`), and `Level100HeightFieldAsset` already derives its
`SunlightDirection` as `-normalize(sunPosition)` mapped through `MapVector`,
which is `SetupLights`' negation exactly. **The reconstruction's cockpit
lighting law is retail's law.** It is not the source of the residual.

## 5. The day-cycle invariance is not a constraint

`operand_scan.py` over all 2,506,752 bytes finds, for each of `0x006fbe44`
(light 0 colour, 5 hits), `0x006fbe48`, `0x006fbe54` (ambient register, 5 hits)
and `0x006fbe6c` (sun position, 4 hits), that **every containing instruction is
a load**. There is no absolute-addressed store to any of them anywhere in the
image, and `SetupLights` rebuilds both lights from those same constants on every
frame.

Retail's light state is therefore **constant for the whole level**. The observed
fact that the cockpit's top rows read exactly `(61.1, 52.5, 59.4)` across the
17 frames of `settled-timeline-run3` is what *any* static lighting law predicts,
including the one the reconstruction already implements. It eliminates nothing,
and it also means the terrain band's 152.8 → 164.1 swing over the same window
**cannot** come from the light state.

## 6. Eliminated, with bytes

- **Alpha blending.** The cockpit really is drawn with
  `SRCALPHA`/`INVSRCALPHA` and z-write off (§1), so a translucent cockpit
  compositing warm background over cold interior was a live mechanism with the
  right sign. It is dead: every vertex of `m_cockpit2.msh.aya` is alpha 255
  (`RetailAquilaVertexDiffuseTests.EveryVertexDiffuseAlphaIsOpaque`), and
  inflating `cockpit.texture.aya` gives a 512x512 `DXT2` surface whose
  **262,144 texels are all alpha 15/15** — a histogram over the explicit
  4-bit alpha of every block returns a single bucket. `SRCALPHA` = 1 makes the
  blend an identity.
- **Specular.** `D3DRS_SPECULARENABLE` is written once in the image, to `0`, at
  `0x004eb2e8`; `material[0].Specular` is `0` and `SPECULARMATERIALSOURCE` is
  `MATERIAL`.
- **Emissive.** `material[0].Emissive` is `0` (sole writer `0x004eb9a0`) and
  `EMISSIVEMATERIALSOURCE` is `MATERIAL` (`0x004eb364`).
- **A cockpit-specific material.** `0x0083d248` is pushed at five `SetMaterial`
  sites and `0x0083d28c` at exactly one (the terrain); there is no third record.
- **A cockpit-specific ambient or light set.** Nothing between
  `CDXLandscape::Render`'s epilogue at `0x00545525` and the draw at `0x0053ec6a`
  writes `D3DRS_AMBIENT`, enables or disables a light, or calls
  `ApplyCachedLight`.

## 7. What is still open — the normal space, not the law

Immediately before the draw, `0x0053ebb6` uploads a world matrix.
`0x00550ca0` writes its 16 dwords to `[this+0x354]` = `0x009c6914`, and
`0x00551034` proves that slot is the **world** transform:

```
00551034  LEA  EDX, [EBP+0x354]
0055103a  PUSH EDX
0055103b  PUSH 0x100                  ; D3DTS_WORLDMATRIX(0)
00551043  CALL dword [ECX+0xb0]       ; IDirect3DDevice9::SetTransform
```

(the same function sets `[EBP+0x394]` with state `2` = `D3DTS_VIEW` at
`0x00551068` and `[EBP+0x3d4]` with state `3` = `D3DTS_PROJECTION` at
`0x005510bd`).

Its source is `0x0089d640` (3x4, transposed into the destination's upper 3x3)
and `0x0089d670` (row 3). Per-dword operand scans of
`0x0089d640`–`0x0089d67c` return exactly one writer for each — the identity
setter at `0x0053d240` and the zero setter at `0x0053d220` — and
`call_xref_scan.py` returns **0 direct references to either**. So this upload is
a reset, not the cockpit's transform, and the real per-part world matrix is set
inside the virtual mesh render reached through `[this+0x8c]->vtable[+8]` at
`0x0053bbea`, which this note did not resolve.

That matters because the world matrix is what decides the space of `N` in
`N.L`. The reconstruction parents the cockpit to the camera, so
`mat3(MODEL_MATRIX) * NORMAL` rotates the cockpit's normals by the camera
orientation before dotting them against the world sun; with the Level 100 sun
24.6 degrees above the horizon after `MapVector`, that is what makes the
reconstruction's cockpit read the blue anti-sun light. Whether retail's cockpit
world matrix carries the camera's rotation is the one remaining term that can
change the cockpit's hue **without** changing the law in §4, and it is the next
thing to establish.

### ANSWERED 2026-07-26 by controlled copied-runtime observation — it does

`IDirect3DDevice9::SetTransform(D3DTS_WORLDMATRIX(0), M)` was captured live at
the Level 100 cockpit draw under CDB on the verified safe copy (sha256
`e1436ef7…`), using a breakpoint *window*: entry to `0x0053bb50` arms the
`SetTransform` breakpoint at `0x00551043` and the return address `0x0053ec6f`
disarms it, so everything outside runs untrapped at ~77 fps. Full record and raw
logs: `local-lab/COCKPIT-WORLD-MATRIX-RUNTIME-2026-07-26.md` and
`local-lab/cockpit-worldmatrix-2026-07-26/`. Reusable probe:
`tools/cdb_worldmatrix_probe.ps1`.

**Seven** world uploads occur per cockpit render — seven draw batches. Batch 0,
D3D row-major, `det = +1.000000`, `|RRᵀ−I| = 1.9e-07`:

```
   0.88662648   0.46089223  -0.03836670   0
  -0.46159714   0.88701338  -0.01164191   0
   0.02866611   0.02803198   0.99919587   0
 288.67752    243.25581    -12.27214      1
```

The translation is the camera world position, and `R_world · R_view` is the axis
map `x→x, y→z, z→−y` to within **2.8774°**. So the cockpit is camera-attached in
world space and retail **does** rotate cockpit normals by the camera
orientation — which is what the reconstruction already does.

**This closes §7 as a precise negative: the normal *space* is not the defect.**
All seven matrices, `D3DTS_VIEW` and `D3DTS_PROJECTION` were bit-identical
across four independent launches and across cockpit frames 0, 2048 and 2400.
The projection shadow `diag(1, 1.3333333, 1.0001428)`, `_34=1`,
`_43=-0.10001428` independently reconfirms the 90° hfov / 4:3 / near-0.1 camera
fix at runtime.

Two findings redirect the work rather than closing it. First, **two of the seven
batches carry a negative-determinant (mirrored) world matrix**, and whether the
reconstruction accounts for the winding/normal flip is unestablished. Second,
with the texel cancelled in a ratio, retail's implied cockpit term has B/R
**0.631** (the sun's own is 0.640) against ours at **1.550** (the anti-sun's is
1.600); solving `L = ambient + a·light` needs `a = (2.605, 1.701, 0.404)` against
the anti-sun, i.e. `a > 1`, which is impossible for `max(0, N·L)`. That
impossibility is robust and is not a region-mean artefact: **retail's cockpit
normals face the sun and ours face away.** The remaining suspects are the
imported normals' sign/handedness and the two mirrored batches.

One measured constraint, stated honestly: the camera does not move in Level 100
under any scripted input (relative mouse-look, held `A`, held right-arrow all
produced bit-identical matrices), so this observes exactly **one** pose. It is
the pose of the t0+25065 ms parity frame, but it cannot demonstrate the matrix
*tracking* the camera; that rests on the structural facts above, not on observed
variation.

## Reproduction

```
py -3 tools/disasm_va.py <BEA.exe> 0x0053eb60 --count 150
py -3 tools/disasm_va.py <BEA.exe> 0x0053bb50 --count 60
py -3 tools/disasm_va.py <BEA.exe> 0x0044a2d0 --count 260 --bytes
py -3 tools/disasm_va.py <BEA.exe> 0x004eb2d0 --count 50
py -3 tools/disasm_va.py <BEA.exe> 0x00551014 --count 60
py -3 tools/call_xref_scan.py <BEA.exe> 0x0044a2d0 0x0053bb50 0x0053d220 0x0053d240
py -3 tools/operand_scan.py <BEA.exe> 0x006fbe44 0x006fbe48 0x006fbe54 0x006fbe6c
py -3 tools/operand_scan.py <BEA.exe> 0x0089d640 0x0089d670
py -3 tools/cockpit_light_state_probe.py
```
