# The default render-state block — `0x004EB1E0`, re-derived from bytes

Date: 2026-07-27.

`D3DStateCache__UseDefaultRenderState` at `0x004EB1E0` has been load-bearing for
several committed rendering decisions — lighting enable, the two material
sources, the stage-0 texture arguments, and the *absence* of
`D3DRS_COLORVERTEX` — while existing in **no tracked file**. It lived in agent
reports and in raw exports under the ignored `local-lab/`. This document
promotes it, and it is a **re-derivation, not a transcription**: the function
body and every call site below were read from the specimen's own bytes.

Three previously-believed statements did not survive that re-derivation. They are
in §7, §8 and §9.

## 1. Specimen, method, and the bound

| | |
| --- | --- |
| Specimen | `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (untracked local input) |
| sha256 | `74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750` |
| Identity | The same image imported into the canonical Ghidra project (`ghidra/README.md`) |
| Access | Read-only. The file was never opened for write, the Steam install was never touched, and the Ghidra project was not mutated. |
| Tool | `tools/pe_read_va.py` section mapping + a capstone x86-32 linear sweep. |

**Every scan in this document is bounded, and the bound is stated with it.**

**The function extent is `[0x004EB1E0, 0x004EB99D)`** — 1,981 bytes. A linear
sweep from `0x004EB1E0` decodes **569 instructions**, the last being the single
`RET` at `0x004EB99C`; the sweep was cut at `0x004EB99D` and nothing past it was
read or attributed to this function. The instruction count and the end address
agree independently with the Ghidra inventory row for this address, which is why
the extent is treated as settled rather than assumed. There is exactly one `RET`
and no tail-jump.

This matters because of the trap that bit this project on 2026-07-27: an
unbounded scalar/VA scan over `0x005386D0` read a hit that lay *inside the next
function* and would have "proved" a name that had just been demoted. Nothing
below is derived from an unbounded scan of a function body.

Whole-image scans (§7, §8) are deliberately unbounded **by design** and cover all
four PE sections — `.text`, `.rdata`, `.data`, `.rsrc` — because the question
they answer is an absence claim over the entire executable. Their scope is stated
in full where they are used.

## 2. The API is Direct3D **9**, not Direct3D 8

The import directory names `d3d9.dll` (and the debug `d3d9d.dll`), and the vtable
displacements used by the setters resolve on the `IDirect3DDevice9` layout:

| Displacement | Index | `IDirect3DDevice9` method | Used at |
| --- | --- | --- | --- |
| `+0x0B0` | 44 | `SetTransform` | `0x005514F8` |
| `+0x0DC` | 55 | `SetClipPlane` | `0x004EBA79` |
| `+0x0E4` | 57 | `SetRenderState` | `0x00513C63`, and §7 |
| `+0x104` | 65 | `SetTexture` | `0x00513A74` |
| `+0x10C` | 67 | `SetTextureStageState` | `0x0051389A` |
| `+0x114` | 69 | `SetSamplerState` | `0x00513925` |
| `+0x134` | 77 | `SetSoftwareVertexProcessing` | `0x00513CCF` |
| `+0x164` | 89 | `SetFVF` | `0x00513D0A` |
| `+0x170` | 92 | `SetVertexShader` | `0x00513CF6` |

Under Direct3D 8 `SetRenderState` sits at `+0x0A4`, and there is no
`SetSamplerState` at all — the whole `0x005138B0` family would be unexplainable.
Three committed comments call the `D3DRS_COLORVERTEX` default a "Direct3D 8
default" (§9). The **conclusion** is unaffected — `D3DRS_COLORVERTEX` defaults to
`TRUE` in both APIs — but the attribution is wrong and the correct D3D9 vtable
indices are what make the decode below checkable.

## 3. The object graph, and the five setters

`0x00855BB0` is the state-cache object. Its device pointer is the member at
`+0x32EA0`, and `0x00855BB0 + 0x32EA0 = 0x00888A50` — which is exactly the global
every setter loads. That arithmetic is the proof that the singleton and the
device global are the same object's two faces.

Three write-through shadow arrays:

| Array | Index | Note |
| --- | --- | --- |
| `0x00855540` | `state * 4` | render state; `D3DRS_LIGHTING` → `0x00855764` |
| `0x008557F0` | `(type + stage * 30) * 4` | shared by stage state **and** sampler state |
| `0x008554D0` | `stage * 4` | texture |

| Setter | Role | Device call | Call sites (whole image) |
| --- | --- | --- | --- |
| `0x00513BC0` | `SetRenderState`, **cached** — returns without touching the device if the shadow already holds the value (`0x00513BC8`) | `+0x0E4` | **440** |
| `0x00513C20` | `SetRenderState`, **forced** — writes the shadow and always calls | `+0x0E4` | **50** |
| `0x00513870` | `SetTextureStageState` | `+0x10C` | 80 |
| `0x005138B0` | `SetSamplerState` | `+0x114` | 32 |
| `0x00513A50` | **`SetTexture`** — *not* a render-state setter | `+0x104` | 57 |

Argument order, recovered from the register/stack moves rather than assumed:
`0x00513C20(state, value)`; `0x00513870(stage, type, value)`;
`0x005138B0(sampler, type, value)`.

Both general render-state setters carry the same quirk at `0x00513BD1` /
`0x00513C2D`: when `state == 0x16` (`D3DRS_CULLMODE`) and the byte at
`0x0089D680` is non-zero, the value `2`⇄`3` is swapped — `D3DCULL_CW` and
`D3DCULL_CCW` exchange. `0x0089D680` behaves as a mirrored/reflected-pass flag
and appears again at `0x004EB2CD` and `0x004EBA30`.

There are also three fixed-state inline wrappers, which matter only because they
are additional ways a render state can reach the device: `0x00513DA0` /
`0x00513DD0` write `D3DRS_ALPHAREF` (`0x18`), and `0x00514030` / `0x0051409F`
write `D3DRS_FOGTABLEMODE` (`0x23`) and `D3DRS_FOGVERTEXMODE` (`0x8C`).

## 4. Entry: the whole cache is invalidated before anything is set

`0x004EB1EB` calls `0x00513600`, which fills `0x00855540` (172 dwords),
`0x008557F0` (240 dwords) and `0x008554D0` (8 dwords) with `0xFEDCBA98`, and sets
`[0x00889070] = 0xFEDCBA98`, `[0x0088906C] = 0`, `[0x00889068] = 0xFEDCBA98`.

Every subsequent render-state write in this function goes through the **forced**
setter `0x00513C20`, so the invalidate is not what makes them reach the device —
they would anyway. What the invalidate does is guarantee that the *next* caller
of the cached setter `0x00513BC0`, for any state, cannot be short-circuited.
**This function is a hard reset, not a cache-warm.**

Conditionally, when `[0x00854E6C]` is non-zero, `0x004EB200` calls `0x00513CA0`,
which does `SetSoftwareVertexProcessing(0)`, `SetVertexShader(NULL)` and
`SetFVF(0x152)` — the same FVF the mesh lane already treats as canonical.

## 5. Answer 1 — the render states this function sets

Every call to `0x00513C20` inside `[0x004EB1E0, 0x004EB99D)`, with the two
literal pushes that precede it:

| Site | State | Value |
| --- | --- | --- |
| `0x004EB20E` | `0x1B` `D3DRS_ALPHABLENDENABLE` | `1` |
| `0x004EB21C` | `0x13` `D3DRS_SRCBLEND` | `5` `D3DBLEND_SRCALPHA` |
| `0x004EB22A` | `0x14` `D3DRS_DESTBLEND` | `6` `D3DBLEND_INVSRCALPHA` |
| `0x004EB238` | `0x0F` `D3DRS_ALPHATESTENABLE` | `1` |
| `0x004EB252` | `0x19` `D3DRS_ALPHAFUNC` | `7` `D3DCMP_GREATEREQUAL` |
| `0x004EB260` | `0x08` `D3DRS_FILLMODE` | `3` `D3DFILL_SOLID` |
| `0x004EB26E` | `0x16` `D3DRS_CULLMODE` | `3` `D3DCULL_CCW` (subject to the `0x0089D680` swap) |
| `0x004EB27C` | `0x0E` `D3DRS_ZWRITEENABLE` | `1` |
| `0x004EB28A` | `0x07` `D3DRS_ZENABLE` | `1` |
| `0x004EB298` | `0x17` `D3DRS_ZFUNC` | `4` `D3DCMP_LESSEQUAL` |
| `0x004EB2A9` | `0xA8` `D3DRS_COLORWRITEENABLE` | `0x0F` (RGBA) |
| `0x004EB2B7` | `0x34` `D3DRS_STENCILENABLE` | `0` |
| `0x004EB2C8` | `0x97` `D3DRS_VERTEXBLEND` | `0` |
| `0x004EB2E3` | `0x1C` `D3DRS_FOGENABLE` | **conditional** — `0` if `[0x0089D680]` non-zero, else `1` (select at `0x004EB2D4`/`0x004EB2D8`/`0x004EB2DA`) |
| `0x004EB2F1` | `0x1D` `D3DRS_SPECULARENABLE` | `0` |
| `0x004EB30E` | `0x89` `D3DRS_LIGHTING` | **`1`** |
| `0x004EB31C` | `0x1A` `D3DRS_DITHERENABLE` | `1` |
| `0x004EB32A` | `0x09` `D3DRS_SHADEMODE` | `2` `D3DSHADE_GOURAUD` |
| `0x004EB33B` | `0x91` `D3DRS_DIFFUSEMATERIALSOURCE` | **`1` `D3DMCS_COLOR1`** |
| `0x004EB34C` | `0x92` `D3DRS_SPECULARMATERIALSOURCE` | `0` `D3DMCS_MATERIAL` |
| `0x004EB35D` | `0x93` `D3DRS_AMBIENTMATERIALSOURCE` | **`1` `D3DMCS_COLOR1`** |
| `0x004EB36E` | `0x94` `D3DRS_EMISSIVEMATERIALSOURCE` | `0` `D3DMCS_MATERIAL` |
| `0x004EB37F` | `0x8F` `D3DRS_NORMALIZENORMALS` | `0` |
| `0x004EB393` | `0x8B` `D3DRS_AMBIENT` | `0xF0CCFACE` — **sentinel, see §9** |
| `0x004EB3A4` | `0x22` `D3DRS_FOGCOLOR` | `0xF0CCFACE` — sentinel |
| `0x004EB3B5` | `0x26` `D3DRS_FOGDENSITY` | `0xF0CCFACE` — sentinel |
| `0x004EB3C6` | `0x24` `D3DRS_FOGSTART` | `0xF0CCFACE` — sentinel |
| `0x004EB3D7` | `0x25` `D3DRS_FOGEND` | `0xF0CCFACE` — sentinel |
| `0x004EB3E8` | `0x3C` `D3DRS_TEXTUREFACTOR` | `0xF0CCFACE` — sentinel |
| `0x004EB3F9` | `0x9C` `D3DRS_POINTSPRITEENABLE` | `0` |
| `0x004EB40A` | `0x9D` `D3DRS_POINTSCALEENABLE` | `0` |
| `0x004EB484` | `0x9A` `D3DRS_POINTSIZE` | float, see below |
| `0x004EB49E` | `0x9B` `D3DRS_POINTSIZE_MIN` | float, see below |
| `0x004EB4BA` | `0x9E` `D3DRS_POINTSCALE_A` | `0.0f` |
| `0x004EB4D6` | `0x9F` `D3DRS_POINTSCALE_B` | `0.0f` |
| `0x004EB4F2` | `0xA0` `D3DRS_POINTSCALE_C` | `1.0f` (`0x3F800000`) |
| `0x004EB50C` | `0xA6` `D3DRS_POINTSIZE_MAX` | float, see below |
| `0x004EB51A` | `0x37` `D3DRS_STENCILPASS` | `1` `D3DSTENCILOP_KEEP` |
| `0x004EB528` | `0x34` `D3DRS_STENCILENABLE` | `0` (second write) |
| `0x004EB536` | `0x38` `D3DRS_STENCILFUNC` | `1` `D3DCMP_NEVER` |
| `0x004EB544` | `0x39` `D3DRS_STENCILREF` | `0` |
| `0x004EB561` | `0x88` `D3DRS_CLIPPING` | `1` |
| `0x004EB57B` | `0xA7` `D3DRS_INDEXEDVERTEXBLENDENABLE` | `0` |

The point-size group (`0x004EB40F`–`0x004EB50C`) is the function's one real
branch: it reads the float at `[0x00888B04]`, compares it against `[0x005D8568]`
at `0x004EB41C`, and **jumps clear of the whole group to `0x004EB511`** when they
are equal. Inside, `POINTSIZE_MIN` is `max(v, [0x005D8C44])` and `POINTSIZE_MAX`
is `v` when `v >= [0x005DB2B8]` and `32.0f` otherwise.

Two further render states are set on this function's behalf by callees:

- `0x004EB244` → `0x00513DD0(8)` → `D3DRS_ALPHAREF` (`0x18`) `= 8`, or `0x0808`
  when `[0x0085541C]` is non-zero.
- `0x004EB2FD` → `0x00514030(1)` → `D3DRS_FOGTABLEMODE` (`0x23`) `= 1`
  (`D3DFOG_EXP`) **only if** the caps dword `[0x00888A78]` has bit `0x100` set.
  That is the same slot the tracked
  [fog render-state contract](d3d-fog-render-state-static-contract-2026-07-25.md)
  describes, now with its gate.
- `0x004EB56A` → `0x004EBA30(1)` → `D3DRS_CLIPPLANEENABLE` (`0x98`) `= 1` with a
  clip plane `(0, 0, -1, [0x006FBDFC])` uploaded via `SetClipPlane` when
  `[0x0089D680]` is set and the FVF shadow is not the invalidate sentinel;
  otherwise `= 0` (`0x004EBAA2`).

`0x004EB550` calls `0x005514A0` on the camera object `0x009C65C0`, which uploads
a `D3DTS_PROJECTION` matrix carrying a depth-offset term. It sets no render
state.

## 6. Answer 2 — lighting is enabled, and it is unconditional

`0x004EB30E`: `SetRenderState(0x89 D3DRS_LIGHTING, 1)`.

**Unconditional within this function**, and the claim is structural rather than
visual. Bounded to `[0x004EB1E0, 0x004EB99D)`, only four conditional branches
exist before `0x004EB30E`:

| Branch | At | Targets | Does it bypass `0x004EB30E`? |
| --- | --- | --- | --- |
| `[0x00854E6C]` test | `0x004EB1F7` | `0x004EB205` | No — skips only the `0x00513CA0` call |
| `[0x0089D680]` fog select | `0x004EB2D4` | `0x004EB2DA` | No — both arms converge at `0x004EB2DC` |
| fog select join | `0x004EB2D8` | `0x004EB2DC` | No |
| — | — | — | — |

The only branch that skips a large span is the point-size test at `0x004EB427`,
which jumps to `0x004EB511` — **291 bytes after** the lighting write. No control
path through this function reaches `0x004EB99C` without executing `0x004EB30E`.

## 7. Answers 3 and 4 — material sources and stage 0

`D3DRS_DIFFUSEMATERIALSOURCE` (`0x91`) `= 1` `D3DMCS_COLOR1` at `0x004EB33B`.
`D3DRS_AMBIENTMATERIALSOURCE` (`0x93`) `= 1` `D3DMCS_COLOR1` at `0x004EB35D`.
Specular and emissive sources are both left at `D3DMCS_MATERIAL`.

Stage 0, texture-stage state via `0x00513870`:

| Site | Type | Value |
| --- | --- | --- |
| `0x004EB5E5` | `0x02` `D3DTSS_COLORARG1` | `2` `D3DTA_TEXTURE` |
| `0x004EB5F5` | `0x03` `D3DTSS_COLORARG2` | `0` `D3DTA_DIFFUSE` |
| `0x004EB605` | `0x05` `D3DTSS_ALPHAARG1` | `2` `D3DTA_TEXTURE` |
| `0x004EB615` | `0x06` `D3DTSS_ALPHAARG2` | `0` `D3DTA_DIFFUSE` |
| `0x004EB625` | `0x01` `D3DTSS_COLOROP` | `4` `D3DTOP_MODULATE` |
| `0x004EB635` | `0x04` `D3DTSS_ALPHAOP` | `4` `D3DTOP_MODULATE` |
| `0x004EB645` | `0x0B` `D3DTSS_TEXCOORDINDEX` | `0` |
| `0x004EB655` | `0x18` `D3DTSS_TEXTURETRANSFORMFLAGS` | `0` `D3DTTFF_DISABLE` |

Stage 0 sampler state via `0x005138B0`: `MINFILTER = MAGFILTER = 2`
(`D3DTEXF_LINEAR`) at `0x004EB58B`/`0x004EB59B`, `MIPFILTER = 2` via
`0x00551460` at `0x004EB5A2`, `MAXANISOTROPY = 1`, `ADDRESSU = ADDRESSV = 1`
(`D3DTADDRESS_WRAP`), `BORDERCOLOR = 0xFFFFFFFF`.

**Stages 1–3 are set up but disabled.** Each repeats the same shape with
`COLORARG2`/`ALPHAARG2` `= 1` (`D3DTA_CURRENT`) instead of `D3DTA_DIFFUSE`,
`TEXCOORDINDEX` equal to the stage index, `COLORARG0 = 3` (`D3DTA_TFACTOR`), and
crucially **`COLOROP = ALPHAOP = 1` (`D3DTOP_DISABLE`)** — at `0x004EB71F` /
`0x004EB72F` (stage 1), `0x004EB829` / `0x004EB839` (stage 2), `0x004EB933` /
`0x004EB943` (stage 3). Only stage 0 is live after this block.

Two behaviours of the sampler setter change what these calls actually do:

- `D3DSAMP_MIPMAPLODBIAS` (type `8`) is **discarded**: `0x005138BC`–`0x005138BF`
  branches to the bare epilogue at `0x0051392C`, so the four `(stage, 8, 0)`
  calls at `0x004EB665`, `0x004EB75F`, `0x004EB869` and `0x004EB973` never reach
  the device and never write the shadow.
- `MINFILTER = 3` (anisotropic) is dropped when caps bit `0x20000` of
  `[0x00888A78]` is clear (`0x005138F2`), and `MAXANISOTROPY` is clamped to
  `[0x00888AC0]`.
- For stages 1–3 the mip filter goes through `0x00551420`, which sets
  `MIPFILTER = 1` (`D3DTEXF_POINT`) **only when `[0x0082B474]` is non-zero** and
  otherwise sets nothing at all.

## 8. Answer 5 — `D3DRS_COLORVERTEX` is never written, and here is the scope

First, a correction of the question. **`D3DRS_COLORVERTEX` is `141` = `0x8D`.**
State `60` = `0x3C` is `D3DRS_TEXTUREFACTOR`, and it **is** written — at
`0x004EB3E8`, with the sentinel `0xF0CCFACE`. A search for "state 60" would have
found a hit and drawn the opposite conclusion.

The absence claim is made at **whole-image** scope, in four layers.

**(a) The only route to the device.** Every render state reaches the hardware
through `IDirect3DDevice9::SetRenderState` at vtable `+0x0E4`. A SIB-aware scan
of all four PE sections for `FF /2` with `disp32 == 0x000000E4` finds
**exactly 10** encodings; a companion scan for the load-then-call form
(`MOV r32,[r32+0xE4]` followed by `CALL r32` within 10 bytes) finds **0**. Of the
10, **9** load the device global `0x00888A50` within the preceding 40 bytes; the
tenth, `0x004FFBC9`, is a call on an unrelated interface held at `[esi+8]` whose
result is compared against `1`.

**(b) What those 9 sites can carry.** Seven are fixed-state: `0x00513C0C`
(`0x16` only, the cull-swap arm), `0x00513DBD` and `0x00513DF5` (`0x18`),
`0x00514058`, `0x00514077`, `0x005140B5` (`0x23`), `0x00514096` and `0x005140D4`
(`0x8C`). None can express `0x8D`. The remaining two are the general setters
`0x00513BC0` and `0x00513C20`.

**(c) Every general-setter call site, resolved.** All **490** call sites
(440 + 50) were located by an exhaustive `E8`/`E9` relative-target scan of all
sections and then back-decoded to recover the state operand. **Zero remained
unresolved** — every one of the 490 pushes a literal state id. Six needed a
back-decode window wider than 40 bytes and were resolved individually
(`0x00482F41` → `0x1B`, `0x00482FE5` → `0x07`, `0x00485C7B` → `0x17`,
`0x004B9BA1` → `0x13`, `0x00541C45` → `0x13`, `0x0055AB13` → `0x13`), and one
apparent `state == 0` at `0x004EBAA8` is an artefact of a jump into the middle of
a push pair — the real state there is `0x98`.

The complete set of `D3DRENDERSTATETYPE` values the executable **ever** writes:

```
07 08 09 0E 0F 13 14 16 17 18 19 1A 1B 1C 1D 22 23 24 25 26 34 37 38 39 3C
88 89 8B 8C 8F 91 92 93 94 97 98 9A 9B 9C 9D 9E 9F A0 A6 A7 A8
```

`0x8D` is not in it.

**(d) No state block can smuggle it in.** `CreateStateBlock` (`+0x0EC`),
`BeginStateBlock` (`+0x0F0`) and `EndStateBlock` (`+0x0F4`) were scanned the same
way. The raw encoding counts (1 / 85 / 43) are dominated by unrelated interfaces:
**none** of them loads `0x00888A50` within 40 bytes, so no D3D9 state-block
capture or apply path exists on the device.

**Conclusion:** `D3DRS_COLORVERTEX` is written at no site in the executable, and
therefore holds the Direct3D **9** default `TRUE` for every draw. Together with
`D3DMCS_COLOR1` on the diffuse and ambient sources, the per-vertex `DIFFUSE`
dword of the FVF `0x152` stream is the diffuse and ambient reflectance.

**What this scope does not cover, honestly:** it bounds `BEA.exe`. It does not
observe `d3d9.dll`'s own default, and no runtime confirmation of
`D3DRS_COLORVERTEX` exists or is easily obtainable — because the state is never
written, the shadow at `0x00855540 + 0x8D*4 = 0x00855774` holds the invalidate
sentinel `0xFEDCBA98`, not the device value. Confirming it at runtime would
require an actual `GetRenderState` call, not a shadow read.

## 9. Answer 6 — the call-site count, and where 547 came from

**`0x004EB1E0` has 7 callers.** Not 547.

Method: an exhaustive byte scan of all four PE sections for `E8`/`E9` with a
computed target of `0x004EB1E0`, plus a scan for the literal dword `0x004EB1E0`
anywhere in the image (which would catch a vtable slot or a function-pointer
table). Result: **7** relative `CALL`s, **0** `JMP`s, **0** absolute dword
references — so the function is not virtual and is not dispatched indirectly.

| Caller site | Containing function |
| --- | --- |
| `0x0042C8B4` | `CConsole__RenderLoadingScreen` |
| `0x0045EDDA` | `CFEPGoodies__Render` |
| `0x0047065E` | `CGame__DrawDebugStuff` |
| `0x0053E22B` | `CDXEngine__PreRender` |
| `0x0053E4D0` | `CDXEngine__Render` |
| `0x0053F25F` | `CDXFMV__VFunc_06_0053F180` |
| `0x00540F78` | `CDXFrontEnd__RenderStart` |

The 547 figure is arithmetically identifiable and is **wrong in composition**.
`Level100VertexDiffuseTests.cs` states it as the call sites "reachable from the
three setters `0x00513BC0`, `0x00513C20` and `0x00513A50`", and
`440 + 50 + 57 = 547` exactly. But `0x00513A50` is **`SetTexture`** (device
vtable `+0x104`, shadow `0x008554D0` indexed by stage), not a render-state
setter. Its 57 call sites could never have carried a render state, so quoting 547
as the number of *render-state* call sites over-counts by 57. The correct figure
is **490**.

Separately, 547 was **never** a count of call sites of `0x004EB1E0`, and any
restatement that reads it that way — "across all 547 call sites" of the default
block — is a second, independent drift away from what the source comment said.

Summary of the counts, each from an exhaustive whole-image scan:

| Quantity | Value |
| --- | --- |
| Callers of `0x004EB1E0` | **7** |
| Instructions in `0x004EB1E0` | **569** |
| Render-state call sites (`0x00513BC0` + `0x00513C20`) | **490** |
| `SetTextureStageState` call sites | 80 |
| `SetSamplerState` call sites | 32 |
| `SetTexture` call sites | 57 |
| Device `SetRenderState` encodings in the image | 9 |

## 10. What this evidence does **not** support

This project's standing rule is that a code path is weaker than a capture. This
function establishes what the **default block** is. It does not establish what
was live at any particular draw — 440 of the 490 render-state writes in the image
go through the *cached* setter and can land at any time after this block runs.

Three specific limits:

**The `0xF0CCFACE` writes are not values.** `D3DRS_AMBIENT`, `D3DRS_FOGCOLOR`,
`D3DRS_FOGSTART`, `D3DRS_FOGEND`, `D3DRS_FOGDENSITY` and `D3DRS_TEXTUREFACTOR`
are each set to `0xF0CCFACE`, a value that is passed to the device verbatim. It
is a cache-defeating sentinel — it guarantees the cached setter's `CMP` at
`0x00513BC8` cannot match whatever the next real write supplies. Reading
`D3DRS_AMBIENT = 0xF0CCFACE` as an ambient colour would be a category error. The
real ambient at the terrain and mesh draws is measured in
`local-lab/LIT-MESH-LIGHT-STATE-2026-07-26.md` (untracked lab note) and is a
completely different number.

**`D3DRS_FOGENABLE` here is conditional**, on `[0x0089D680]` — the same flag that
inverts cull winding. The default block does not fix fog on.

**Which committed decisions have a capture behind them, and which do not:**

| Committed decision | Static (§5–§8) | Runtime observation |
| --- | --- | --- |
| The base mesh pass runs **lit** | yes, `0x004EB30E` | **yes** — `D3DRS_LIGHTING` read from the shadow at `[0x00855764]` equals `1` at all 576 world and tree mesh draws of a Level 100 frame; the `RenderMeshCore` mode-2/mode-6 branches that clear it never fired across 4,393 mesh renders. See [`controlled-runtime-observations-2026-07-26.md`](controlled-runtime-observations-2026-07-26.md) and the lab note above. |
| `DIFFUSEMATERIALSOURCE = D3DMCS_COLOR1` | yes, `0x004EB33B` | **no** — static only, at the mesh draws. The terrain lane is the exception: `CDXLandscape::Render` was observed setting it to `D3DMCS_MATERIAL` for its own draw and restoring afterwards, which is itself proof that this default does **not** hold everywhere. |
| `AMBIENTMATERIALSOURCE = D3DMCS_COLOR1` | yes, `0x004EB35D` | **no** — static only. |
| Stage-0 `COLORARG1 = TEXTURE` / `COLORARG2 = DIFFUSE`, `COLOROP = MODULATE` | yes, §7 | **no** — static only. The stage-state shadow at `0x008557F0` makes this cheap to measure and it has not been measured. |
| `COLORVERTEX` left `TRUE` | yes, §8, whole-image | **no**, and not obtainable from the shadow (§8). |
| Stages 1–3 disabled by default | yes, §7 | **no** — and known to be overridden in practice; multi-texture paths exist. |

The honest position: **lighting-on is measured; everything else in this block is
a static default that a later cached write can change without leaving a trace in
this function.** Any reconstruction decision that needs the state *at a specific
draw* should read the shadow arrays at that draw — `0x00855540` for render state,
`0x008557F0` for stage and sampler state — using the probe pattern already
committed in `tools/cdb_lightstate_probe.ps1`.

## 11. Corrections this document makes

1. **"Direct3D 8 default"** — the binary imports `d3d9.dll` and every setter
   resolves on the `IDirect3DDevice9` vtable (§2). The conclusion survives;
   the attribution does not.
2. **"547 render-state call sites"** — `440 + 50 + 57`, where the 57 belong to
   `SetTexture`. The render-state figure is **490** (§9).
3. **"`D3DRS_COLORVERTEX` (value 60)"** — `COLORVERTEX` is `141`/`0x8D`. `60` is
   `D3DRS_TEXTUREFACTOR`, which *is* written, at `0x004EB3E8` (§8).
4. **`0x004EB1E0` has 7 callers**, not 547 (§9).
5. Four `D3DSAMP_MIPMAPLODBIAS` writes in this function are silently discarded by
   the setter and never reach the device (§7).
