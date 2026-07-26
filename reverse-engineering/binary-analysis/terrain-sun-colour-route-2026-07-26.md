# The sun colour and the terrain draw — all ten references, and a precise negative

> Verdict: **the sun colour does not multiply the terrain.** The two HFLD colour
> globals are read by exactly **ten** instructions in the whole image, and every
> one is now identified. Four are trees, two are a **dead branch** in an offline
> tool, two build fixed-function light state that the terrain draw disables, one
> tints projected shadow sprites, and the tenth — the unexplained
> `CDXLandscape__Render` reference — **restores** the ambient colour *after*
> `RenderTerrain` returns, immediately after the same function set it to **zero**
> for the terrain draw. The chromaticity agreement that motivated this search is
> a coincidence: several unrelated quantities built from the same two colours
> match the measured factor to within a few percent, and none carries a
> magnitude. **No gain, offset, or tint was applied.**

Specimen: `BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`,
2,506,752 bytes (local pristine safe copy). Image base `0x00400000`.
Ghidra exports taken headless with `-readOnly`; the maintainer database was not
mutated.

## 1. The two globals, and the exhaustive reference set

`CHeightField::Load` copies HFLD `CHFD+0x107C` (sun) and `CHFD+0x108C` (ambient)
into two BSS globals. All three of `0x006fbe44`, `0x006fbe54` and the notional
object base `0x006eadc8` are in the **uninitialised tail of `.data`**
(`pe_read_va.py` refuses all three), so they hold their values only at runtime.

A whole-file scan of the 2,506,752 image bytes for each little-endian operand
returns:

| global | operand bytes | occurrences |
| --- | --- | ---: |
| `0x006fbe44` (sun, `+0x107C`) | `44 be 6f 00` | **5** |
| `0x006fbe54` (ambient, `+0x108C`) | `54 be 6f 00` | **5** |
| `0x006fbe48` (`+0x1080`, second light colour) | `48 be 6f 00` | 2 |
| `0x006eadc8` (object base) | `c8 ad 6e 00` | **0** |

The object base appears **zero** times, so there is no pointer-based read route
to inspect either: the ten instructions below are the complete set. Every one is
a **load** (`a1` / `8b`), so neither global is written by any absolute-addressed
instruction — consistent with `CHeightField::Load` writing them through `this`.

| # | VA | instruction | containing function |
| --- | --- | --- | --- |
| 1 | `0x0044a402` | `MOV EAX, [0x006fbe44]` | `CEngine__SetupLights` @ `0x0044a2d0` |
| 2 | `0x0044a407` | `MOV ECX, [0x006fbe54]` | `CEngine__SetupLights` |
| 3 | `0x004ddc73` | `MOV EAX, [0x006fbe44]` | `CRTTree__VFuncSlot02_BuildRenderOutputs` @ `0x004dd960` |
| 4 | `0x004dde2e` | `MOV ECX, [0x006fbe44]` | `CRTTree__VFuncSlot02_BuildRenderOutputs` |
| 5 | `0x004dde34` | `MOV EAX, [0x006fbe54]` | `CRTTree__VFuncSlot02_BuildRenderOutputs` |
| 6 | `0x0054ecfc` | `MOV ECX, [0x006fbe44]` | `DXPalletizer__Palletize` @ `0x0054e9d0` |
| 7 | `0x0054ed02` | `MOV ESI, [0x006fbe54]` | `DXPalletizer__Palletize` |
| 8 | `0x00554788` | `MOV EAX, [0x006fbe54]` | `CRenderQueue__EmitBillboardStrip` @ `0x00554750` |
| 9 | `0x0055478d` | `MOV ECX, [0x006fbe44]` | `CRenderQueue__EmitBillboardStrip` |
| 10 | `0x00545525` | `MOV ECX, [0x006fbe54]` | `CDXLandscape__Render` @ `0x00545410` |

The shipped Level 100 values are sun `0x00BDB179` = (189, 177, 121) and ambient
`0x000D0F2B` = (13, 15, 43); their sum is (202, 192, 164).

## 2. Reference 10 — what `CDXLandscape__Render` actually does with the ambient

This was the one reference the stage census never explained. The bytes settle it
by address order alone:

```
005454db   C7 05 A8 68 9C 00 00 00 00 00   MOV  dword ptr [0x009c68a8], 0x0   ; ambient := 0
005454e5   C6 05 0C 69 9C 00 01            MOV  byte  ptr [0x009c690c], 0x1   ; mark dirty
...
00545520   E8 6B 00 00 00                  CALL 0x00545590                    ; RenderTerrain
00545525   8B 0D 54 BE 6F 00               MOV  ECX, dword ptr [0x006fbe54]   ; HFLD ambient
0054552b   C6 05 0C 69 9C 00 01            MOV  byte  ptr [0x009c690c], 0x1
00545532   89 0D A8 68 9C 00               MOV  dword ptr [0x009c68a8], ECX   ; ambient := HFLD
```

`0x009c68a8` is the engine's ambient-colour register (`0x009c690c` is its dirty
flag). The write at `0x005454db` is unconditional straight-line code in the
prologue of the terrain block; the read at `0x00545525` is **after** the
`CALL` to `RenderTerrain`.

So the answer is the exact opposite of the hypothesis: **`CDXLandscape::Render`
suppresses the ambient colour for the terrain draw and restores it for
everything drawn afterwards.** The terrain renders at ambient = 0.

The same function brackets the draw with `CDXEngine__ApplyCachedLight(&DAT_009c65c0, i, 1)`
for `i` in `0..7` before, and `(..., 0)` after. `ApplyCachedLight` @ `0x00551200`
copies a `0x5c`-byte cached light record into a stack record and calls device
vtable `+0xcc` with `(index, record)`; the `enabled == 1` argument only controls
whether one extra vector triple is copied. It is a light-record upload, not an
enable.

## 3. References 1 and 2 — `CEngine__SetupLights`, and why lighting cannot reach terrain

`CEngine__SetupLights` unpacks the sun colour into light 0's record at
`0x009c65c0`, scaling each byte by `_DAT_005db060` = `0x3b800000` = **1/256**,
and writes the ambient colour to `0x009c68a8`. `0x006fbe48` (`+0x1080`,
(35, 35, 56)) becomes light 1 at `0x009c661c` the same way.

Three independent facts close this route for terrain:

- **The ambient is zero for the draw** — §2, unconditional.
- **Lighting is off for the draw.** `0x009c68ad` is the engine's lighting-enable
  byte (`0x009c6910` its dirty flag). `CEngine__SetupLights` sets it to 1 at
  `0x0044a39e`; `CDXLandscape__RenderTerrain` sets it to **0** at its own entry
  and back to 1 at exit:

  ```
  00545590   A1 4C A9 8A 00        MOV  EAX, [0x008aa94c]
  0054559e   3B C5                 CMP  EAX, EBP           ; EBP = 0
  005455a0   75 0E                 JNZ  0x005455b0
  005455a2   C6 05 AD 68 9C 00 00  MOV  byte ptr [0x009c68ad], 0x0
  ...
  005461fa   A1 4C A9 8A 00        MOV  EAX, [0x008aa94c]
  00546203   75 0E                 JNZ  0x00546213
  00546205   C6 05 AD 68 9C 00 01  MOV  byte ptr [0x009c68ad], 0x1
  ```

  Both writes are gated on `DAT_008aa94c == 0`. `0x008aa94c` is
  `0x008aa920 + 0x2c` — a member of the landscape/water object whose base
  `0x008aa920` `RenderTerrain` loads into `ECX` — and it lies in uninitialised
  `.data`, so its value is not decidable statically. This gate does not rescue
  the hypothesis, because the ambient suppression in §2 is ungated and because of
  the third fact.
- **The terrain vertices carry no normal.** The LOD tile loop indexes vertices at
  stride `0x14` = 20 bytes = position + one UV pair (established in
  [the stage-flag note](terrain-draw-stage-flags-2026-07-26.md)). No
  `D3DFVF_NORMAL` means no diffuse light term regardless of the light record.

`CVertexShader__ApplyCustomRenderStateShaderConstants` @ `0x00502920` does upload
both the ambient register (`0x00503098`, scaled by `_DAT_005df8fc` = 1/255) and
the light array (`LEA ESI,[EDX*4 + 0x9c65c0]` at `0x0050344a`) as shader
constants, and `CVertexShader__BuildAndCreateRenderInfoShader` @ `0x00503ac0`
reads the lighting flag at `0x00503bb3` when synthesising a shader. So a shader
route exists in principle — but it is fed by the same two values, which are
zero and disabled for this draw.

## 4. References 6 and 7 — `DXPalletizer__Palletize` is a dead branch in an offline tool

This is the most interesting of the ten and the only one that multiplies a
texture by a sun-derived factor. Inside `Palletize`, the `expand_half_palette`
branch synthesises the **upper half** of the palette from the lower half:

```
dest_c = src_c * ((((ambient_c << 8) / ((sun_c & 0xFE) + 1)) + 255) / 2) / 255
```

which for Level 100 is `src x (136, 138, 172) / 255` = `x (0.533, 0.541, 0.674)`
— a darkening, whose reciprocal is `(1.875, 1.848, 1.483)`. The inner term
`(ambient << 8) / ((sun & 0xFE) + 1)` is **byte-identical in form** to the base
of `CHeightField__InitColorGradient`, and `(base + 255) / 2` is exactly that
gradient's midpoint entry.

It is nevertheless unreachable:

- `DXPalletizer__Palletize` has **exactly one xref in the image**:
  `CDXEngine__BuildLandscapeTextureCache` @ `0x00547860`, call at `0x005479a6`.
- That call passes `expand_half_palette = 0`. The twelve pushes at
  `0x0054797a`–`0x0054799e` decompile to
  `Palletize(src, w, h, 0x100, &indices, &palette, 0, 1, 1, 0, 0, 0)`; the
  eleventh argument is the flag, and the three literal `PUSH 0x0` at
  `0x0054797a`/`0x0054797c` cover it.
- `CDXEngine__BuildLandscapeTextureCache` is itself the **offline PS2 cache
  writer** — it logs `Building texture cache...` and `fwrite`s to
  `ps2data/LandscapeTextureCache`, a lane already eliminated.

So references 6 and 7 join the per-node terrain light as **dead code**.

## 5. References 3–5 and 8–9 — trees and shadow sprites

- `CRTTree__VFuncSlot02_BuildRenderOutputs` @ `0x004dd960` **overwrites** the
  global light 0 record and the ambient register with its own sun/ambient-derived
  values, calls `CSphere__RenderAnimatedRecursive`, then restores both from
  saved copies. It is the tree-imposter render-target builder; it touches no
  landscape geometry.
- `CRenderQueue__EmitBillboardStrip` @ `0x00554750` computes
  `(sun & 0xFEFEFE) + (ambient & 0xFEFEFE)` at `0x00554788`–`0x0055478d`, then
  halves and alpha-scales it per channel into a vertex tint for projected
  shadow sprites (`CStaticShadows__SampleShadowHeightBilinear`,
  `CVBufTexture__AddVertices(..., 4)` / `AddIndices(..., 6)`). This is the only
  place in the image where the quantity **`sun + ambient` = (202, 192, 164)**
  literally appears — as a shadow-decal tint on separate geometry drawn through
  `CRenderQueue`, not as a modulation of the terrain draw.

## 6. Q3 — inherited state, and the one call still unidentified

`CDXLandscape::Render` does set state the terrain draw inherits:
`RenderState_Set(0x91, 0)` (`DIFFUSEMATERIALSOURCE`), `(0x1b, 0)`, `(0x0f, 0)`,
`D3DStateCache__SetSlotMode4or5` on stages 0 and 1, `SetStateCached(0, 4, 1)`,
the ambient zero of §2, and the cached-light uploads. None is a colour the sun
can reach, for the reasons in §3.

One call in that prologue remains unidentified and is recorded rather than
claimed:

```
005454ec   68 8C D2 83 00        PUSH 0x83d28c
005454f4   FF 92 C4 00 00 00     CALL dword ptr [EDX + 0xc4]      ; EDX = *DAT_00888a50
```

Device vtable `+0xc4` takes one pointer. Its six other call sites
(`CDXEngine__Render` ×2, `CDXFrontEnd__SetupRenderMatricesAndProjection`,
`CDXImposter__RenderAll`, `CRenderQueue__RenderMultipassLayerA`, plus
`CThing__Init` on a different object) all pass `0x0083d248`, which elsewhere is
used as an `ECX` `this` for engine methods. `CDXLandscape::Render` is the only
caller that passes `0x0083d248 + 0x44` instead — a terrain-specific selection.
`0x0083d28c` has **exactly one occurrence in the whole image** (the `PUSH`
above), is in uninitialised `.data`, and is never written by any
absolute-addressed instruction.

Whatever it is, it cannot carry the sun or ambient colour: §1 enumerates every
instruction in the image that reads either global, and none of the ten is on any
path that writes `0x0083d28c`. Identifying `+0xc4` is left as separate work.

## 7. The chromaticity match is a coincidence

`tools/terrain_sun_colour_candidates.py` re-derives every candidate from the
shipped HFLD bytes and normalises each to blue, against the measured factor
(1.457, 1.389, 1.147) from
[the inversion note](terrain-implied-macro-inversion-2026-07-26.md):

| candidate | raw | normalised to blue | error vs measured |
| --- | --- | --- | --- |
| measured terrain factor | (1.457, 1.389, 1.147) | (1.270, 1.211, 1.000) | — |
| `sun + ambient` | (202, 192, 164) | (1.232, 1.171, 1.000) | −3.0%, −3.3% |
| sun alone | (189, 177, 121) | (1.562, 1.463, 1.000) | +23.0%, +20.8% |
| 1 / Palletize half-palette factor | (1.875, 1.848, 1.483) | (1.265, 1.246, 1.000) | **−0.4%**, +2.9% |

The reciprocal of the *dead* palette branch matches red **better** than
`sun + ambient` does. That is the point: any quantity built from these two
colours lands in the same neighbourhood, so a few-percent chromaticity agreement
identifies nothing, and the best-matching candidate is provably unreachable.
Neither candidate supplies a magnitude — `sun + ambient` is not even
dimensionless, and the Palletize reciprocal is 1.875 against a measured 1.457.

## 8. What this leaves

The sun colour is eliminated as the terrain multiplier. The measured factor's
chromaticity is not evidence for it, and the search should be redirected away
from HFLD lighting data entirely.

Two surfaces named here are not yet closed, and neither is a sun-colour route:

- device vtable `+0xc4` and the terrain-specific argument `0x0083d28c` (§6);
- the landscape gate `0x008aa94c`, which also selects `SetSlotMode4or5` over
  `SetStateRaw(0, 1, 4)` at `RenderTerrain` entry and is compared again at
  `0x00545675` beside the `MODULATE`/`MODULATE2X` flag (§3).
