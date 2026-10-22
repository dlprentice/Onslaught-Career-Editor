# Direct3D fog render states — which slot carries `D3DFOG_EXP`

> Scope: static evidence from the maintainer Ghidra database (`BEA` / `BEA.exe`,
> imported Steam specimen SHA-256
> `74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750`).
> Read-only headless export (`-readOnly -noanalysis`). No rename, comment, tag,
> or other database mutation was issued. Ghidra 12.1.2.
>
> Static instruction bytes prove the states, constants, and call sites listed
> here. They do not prove what a given driver reports at runtime, and they do
> not establish rendered-output parity.

## Verdict

Retail sets **both** fog-mode render states, mutually exclusively, from one
helper — `RenderState_Set_23_8C_Compat` at **`0x00514030`**:

| Device reports `RasterCaps & 0x100` | `D3DRS_FOGTABLEMODE` (0x23) | `D3DRS_FOGVERTEXMODE` (0x8C) |
| --- | --- | --- |
| yes (fog-enabled call) | `1` = `D3DFOG_EXP` | **never written** — stays at the D3D default `D3DFOG_NONE` |
| no (fog-enabled call) | `0` = `D3DFOG_NONE` | `1` = `D3DFOG_EXP` |
| — (fog-disabled call) | `0` = `D3DFOG_NONE` | `0` = `D3DFOG_NONE` |

`0x100` is `D3DPRASTERCAPS_FOGTABLE`. On any device that advertises table fog —
i.e. effectively all hardware the Steam build runs on — the released game uses
**per-pixel (table) `D3DFOG_EXP`**, and per-vertex fog is a capability fallback
only.

**The reconstruction's per-pixel exponential fog matches the released path.**
No change is warranted on fog-mode grounds, and switching the shaders to
per-vertex fog would be a regression.

### Correction to the state numbering used in the request

The states are the `D3DRENDERSTATETYPE` values — the enumeration is identical in
Direct3D 8 and Direct3D 9 — not the ones assumed in the task framing. Confirmed
by `D3DRS_CULLMODE == 22 == 0x16`, which both `RenderState_Set` and
`RenderState_SetRaw` special-case for a `2`↔`3` winding swap (see below).

> **Corrected 2026-07-28 — the API attribution, not the numbers.** This
> paragraph previously read: "The states are the D3D8 `D3DRENDERSTATETYPE`
> values, not the ones assumed in the task framing." **The binary is Direct3D
> 9.** Measured on the pristine specimen named at the head of this document
> (`74154bfa…`): the import directory contains `d3d9.dll` and `d3d9d.dll` and
> the import name table contains `Direct3DCreate9`; there is **no `d3d8.dll`
> import**. The three `Direct3DCreate8_*` strings that live in `.data` around
> file offset `0x24bea0` are leftover log text, not imports. This document
> self-refutes at its own line for `CALL dword ptr [ECX + 0xe4]`: `+0xe4` is
> `IDirect3DDevice9` index 57, whereas Direct3D 8 puts `SetRenderState` at
> `+0x0A4`.
>
> **Nothing in the verdict, the state table, or the byte evidence changes.** The
> `D3DRENDERSTATETYPE` values quoted here (`CULLMODE` 22, `FOGENABLE` 28,
> `FOGCOLOR` 34, `FOGTABLEMODE` 35, `FOGSTART` 36, `FOGEND` 37, `FOGDENSITY` 38,
> `RANGEFOGENABLE` 48, `FOGVERTEXMODE` `0x8C`) are the same in both APIs, and so
> are the `D3DCAPS` field offsets used below, which lie in the prefix that
> `D3DCAPS8` and `D3DCAPS9` share byte-for-byte through `TextureOpCaps`
> (`+0x90`). Only the attribution was wrong.
>
> See [`d3d-default-render-state-block-2026-07-27.md`](d3d-default-render-state-block-2026-07-27.md)
> §2 and its Correction 1, which established this from the same import
> directory and a nine-slot vtable table. Task #129.

| Name | Decimal | Hex |
| --- | ---: | --- |
| `D3DRS_FOGENABLE` | 28 | `0x1C` |
| `D3DRS_FOGCOLOR` | 34 | `0x22` |
| `D3DRS_FOGTABLEMODE` | 35 | **`0x23`** |
| `D3DRS_FOGSTART` | 36 | **`0x24`** |
| `D3DRS_FOGEND` | 37 | **`0x25`** |
| `D3DRS_FOGDENSITY` | 38 | **`0x26`** |
| `D3DRS_RANGEFOGENABLE` | 48 | `0x30` |
| `D3DRS_FOGVERTEXMODE` | 140 | `0x8C` |

`0x24` is `FOGSTART`, not `FOGTABLEMODE`.

## Byte evidence — `RenderState_Set_23_8C_Compat`, `0x00514030`

A 44-instruction body, read with
`ExportFunctionBodyInstructionsByAddress.java`. Signature
`void __stdcall (char enable)` (`RET 0x4`). In prose:

- **Disable** (`enable == 0`, branch to `0x0051409f`): writes `D3DFOG_NONE`
  (0) to both `D3DRS_FOGTABLEMODE` (`0x23`) and `D3DRS_FOGVERTEXMODE`
  (`0x8c`), updating their shadows `0x008555cc` and `0x00855770`.
- **Enable, table fog available** (`RasterCaps` at `0x00888a78` has bit
  `0x100`, tested at `0x0051403d`): writes `D3DFOG_EXP` (1) to
  `FOGTABLEMODE` (shadow `0x008555cc`) and returns at `0x0051405e` without
  touching `0x8c`.
- **Enable, no table fog** (`0x00514061`): writes `D3DFOG_NONE` to
  `FOGTABLEMODE` and `D3DFOG_EXP` to `FOGVERTEXMODE` (shadow `0x00855770`).

Every write goes straight to `IDirect3DDevice9::SetRenderState` (vtable
`+0xe4`) on the device pointer held at `0x00888a50`.

The capability test masks bit 8 of `RasterCaps`, i.e. `RasterCaps & 0x00000100`.

### This is the only place either mode is set

Exhaustive operand scan of all **546,729** disassembled instructions
(`ExportInstructionsByOperandToken.java`, tokens `0x23` / `0x8c`, then filtered
to exact `PUSH <imm>`):

- `PUSH 0x23` (`6a 23`): 23 sites program-wide. Exactly **three** are in a
  render-state context — `0x00514053`, `0x00514072`, `0x005140b0`, all inside
  `0x00514030`. The other 20 are unrelated (`CCannon__Init`, `CGroundUnit__Init`,
  yacc tables, unwind stubs, …).
- `PUSH 0x8c` (`68 8c 00 00 00`): 6 sites program-wide. Exactly **two** are
  render-state — `0x0051408e`, `0x005140cc`, both inside `0x00514030`.

A separate call-site walk-back over every `CALL`/`JMP` reference to the four
render-state setters (`CEngine__SetRenderStateCached 0x00513A50`,
`RenderState_Set 0x00513BC0`, `RenderState_SetRaw 0x00513C20`,
`RenderState_Set_23_8C_Compat 0x00514030`; 4,912 instruction rows) found **no**
call passing `0x23` or `0x8C` as a state id. Nothing else in the binary writes
either fog-mode state.

### `DAT_00888a78` is `D3DCAPS9.RasterCaps`

Never written through direct addressing anywhere in the image — only read,
consistent with a field inside a caps block filled by `GetDeviceCaps`. Taking
the caps base as `0x00888A54`, the observed accesses line up with the `D3DCAPS9`
layout on every field the binary touches. *(All six offsets below lie in the
prefix that `D3DCAPS8` and `D3DCAPS9` share byte-for-byte through
`TextureOpCaps` (`+0x90`), so the table is unchanged by the 2026-07-28 API
correction above; only the struct name is.)*

| Global | Offset from `0x00888A54` | `D3DCAPS9` field | Observed use |
| --- | --- | --- | --- |
| `0x00888A78` | `+0x24` | `RasterCaps` | `& 0x100` = `FOGTABLE` at `0x00514038`; `& 0x20000` = `ANISOTROPY` at `0x005138C6`, `0x005138F2`, `0x00513970` |
| `0x00888A90` | `+0x3C` | `TextureCaps` | bit-tested in `CDXBattleLine__Constructor`, `CDXCompass__Init` |
| `0x00888AAC` | `+0x58` | `MaxTextureWidth` | compared against texture dims in `CDXTexture__CreateMipmaps` (`0x00559443`) |
| `0x00888AB0` | `+0x5C` | `MaxTextureHeight` | `0x0055944B` |
| `0x00888AC0` | `+0x6C` | `MaxAnisotropy` | anisotropy clamp at `0x005138DB`, `0x0051395A` |
| `0x00888AE4` | `+0x90` | `TextureOpCaps` | `& 0x1000000` in `CWaterRenderSystem__RenderMainPass` (`0x0055BABA`) |

The anisotropy pairing (`RasterCaps & 0x20000` = `D3DPRASTERCAPS_ANISOTROPY`
guarding a read of `MaxAnisotropy`) is independent confirmation of the base.

## Where each fog state is set

Two device abstractions exist. Both dispatch to the same `SetRenderState`-shaped
vtable slot family:

- `RenderState_Set` (`0x00513BC0`, cached) / `RenderState_SetRaw`
  (`0x00513C20`, forced) — shadow table at `0x00855540`, device at
  `0x00888A50`, vtable `+0xE4`. Both special-case state `0x16`
  (`D3DRS_CULLMODE`), swapping `2`↔`3` when `DAT_0089D680` is set.
- `CEngine__SetRenderStateCached` (`0x00513A50`) — shadow table at `0x008554D0`,
  device at `this+0x32EA0`, vtable `+0x104`. **No fog state is ever routed
  through it.**

### Device init — `D3DStateCache__UseDefaultRenderState`, `0x004EB1E0`

| Order | Call | State | Value |
| --- | --- | --- | --- |
| 1 | `RenderState_SetRaw` | `0x1C` FOGENABLE | 1 unless `DAT_0089D680` is set |
| 2 | `RenderState_SetRaw` | `0x1D` SPECULARENABLE | 0 |
| 3 | `RenderState_Set_23_8C_Compat` | fog mode | 1 (call at `0x004EB2FD`, argument pushed at `0x004EB2F6`) |
| later | `RenderState_SetRaw` | `0x22` FOGCOLOR, `0x26` FOGDENSITY, `0x24` FOGSTART, `0x25` FOGEND | sentinel `0xF0CCFACE` each |

`0xF0CCFACE` (`-0xF330532` read as a signed integer) is a poison sentinel written into the
shadow table so the first real per-frame write can never be swallowed by the
cache-equality early-out in `RenderState_Set`. It is **not** a fog value.

Fog mode is therefore established once at device reset, and re-established
around vertex-shader transitions — never per draw call with a different mode.

### Per frame — `CDXEngine__Render`, `0x0053E2E0`

At `0x0053e5c5`–`0x0053e5d2` it writes the packed fog colour global
`[0x006fbe40]` to `D3DRS_FOGCOLOR` (`0x22`) through `RenderState_Set`
(`0x00513bc0`, `this` = `0x00855bb0`); at `0x0053e5d7`–`0x0053e5e6` it passes the
fog density float `[0x006fbe60]` to the deferred fog-density setter `0x005513d0`
on the `CDXEngine` singleton `0x009c65c0`.

`0x006FBE40` is the packed fog colour and `0x006FBE60` the fog density, both
level-supplied (`#D8D8FC` / `0.0084` for Level 100 per existing runtime
evidence). Neither is written anywhere via direct addressing.

### Deferred flush — `CDXEngine__ApplyPendingRenderState`, `0x00550D50`

Dirty-flag driven; each state is written at most once per flush:

| Dirty byte | Value field | State |
| --- | --- | --- |
| `this+0x34D` | `this+0x2EC` (byte) | `0x1C` `FOGENABLE` — forced to `0` first if `DAT_0089D680` is set |
| `this+0xE2B` | `this+0xE1C` | `0x24` `FOGSTART` |
| `this+0xE2C` | `this+0xE20` | `0x25` `FOGEND` |
| `this+0xE2D` | `this+0x2F0` | `0x26` `FOGDENSITY` |

Fog mode is re-armed here around the vertex-shader boundary:

- `RenderState_Set_23_8C_Compat(1)` at `0x00550DC0` when a pending
  render-info shader is being torn down (returning to fixed function).
- `RenderState_Set_23_8C_Compat(EBX)` at `0x00550F71` — the disable call
  (`EBX == 0`) taken when a vertex shader is installed. With a vertex shader
  bound, both fog modes are set to `D3DFOG_NONE`, which is the correct
  fixed-function posture (fog factor then comes from the shader's `oFog`
  register). *(Corrected 2026-07-28; previously read "the correct D3D8
  posture".)*

`CDXEngine__SetShaderMode` (`0x005513F0`) calls
`RenderState_Set_23_8C_Compat(1)` at `0x00551416` when mode returns to `0`.

Field defaults from `CDXEngine__InitTransformCaches` (`0x005508E0`):
`this+0xE1C = 0` (FOGSTART `0.0f`), `this+0xE20 = 0x41200000` (FOGEND `10.0f`),
`this+0x2F0 = 0x3F800000` (FOGDENSITY `1.0f`), all four dirty bytes set to `1`.

### Water pass — `CWaterRenderSystem__RenderMainPass`, `0x0055B6C0`

Forces the whole fog block raw, then re-arms the mode:

| Site | Call | Value |
| --- | --- | --- |
| `0x0055b8a3` | `RenderState_SetRaw(FOGDENSITY 0x26)` | `[0x006fbe60]` |
| `0x0055b8b9` | `RenderState_SetRaw(FOGENABLE 0x1c)` | 1 |
| `0x0055b8cf` | `RenderState_SetRaw(FOGSTART 0x24)` | `0.0f` |
| `0x0055b8e0` | `RenderState_SetRaw(FOGEND 0x25)` | `10.0f` |
| `0x0055b8ee` | `RenderState_SetRaw(FOGCOLOR 0x22)` | `[0x006fbe40]` |
| `0x0055b901` | `RenderState_Set_23_8C_Compat` | 1 (argument pushed at `0x0055b8fa`) |

Note the water pass writes `FOGSTART`/`FOGEND` while the mode is `D3DFOG_EXP`,
under which D3D ignores both. They are dead writes under the table-fog path.

### Terrain

`CDXLandscape__Render` (`0x00545410`) and `CDXLandscape__RenderTerrain`
(`0x00545590`) set **no** fog state. Terrain inherits the global fog state
established by the device reset plus the per-frame `CDXEngine__Render` colour /
density writes. There is no terrain-specific fog override, and no second fog
mode anywhere in the frame.

### `D3DRS_RANGEFOGENABLE` (`0x30`) is never set

No call to any of the four setters passes `0x30`. The 56 program-wide
`PUSH 0x30` sites are all unrelated (`CEngine__Init`, `CMeshPart__LoadFromStream`,
`CDXTexture__*`, …). Range fog therefore remains at the D3D default `FALSE`, so
retail fog is depth-based, not radial.

### `DAT_0089D680`

Global byte set to `1` at `0x0046E4EB` and cleared at `0x0046E8D1`, both inside
`CGame__Render`. While set it (a) flips the `D3DRS_CULLMODE` `2`↔`3` winding in
`RenderState_Set` / `RenderState_SetRaw` and (b) forces `D3DRS_FOGENABLE` to `0`
in both `D3DStateCache__UseDefaultRenderState` and
`CDXEngine__ApplyPendingRenderState`. Shape of a mirrored/reflected pass. Its
exact pass identity is not established by these bytes.

## Bonus: far plane and view distance

`CDXEngine__SetProjectionMatrix` (`0x00550B10`) —
`(this, near_z, far_z, viewport_w, viewport_h)`, `RET 0x10`, builds
`far/(far-near)` and `-(near*far)/(far-near)`.

`CDXEngine__Render` issues two projections per frame:

1. **Sky / Kempy cube** — `near = 1.0f` (`PUSH 0x3f800000` at `0x0053E619`),
   `far = sqrt(double at 0x005E4FD8)`.
2. **World, terrain, and everything after it** — `near = CDXEngine+0x430`,
   **`far = 700.0f`**:

At `0x0053e665`–`0x0053e670` it pushes `0x442f0000` (700.0f) as `far_z` and
`[CDXEngine+0x430]` as `near_z` and calls `SetProjectionMatrix` (`0x00550b10`,
`this` = `0x009c65c0`); the far-plane immediate's signature is
`68 00 00 2f 44`.

`CDXLandscape__Render` runs immediately after this call, so **700.0 world units
is the terrain far plane**. The same `0x442F0000` literal is the far plane in
`CFrontEnd__RenderStart` (`0x00468626`) and `CFEPGoodies__Render`
(`0x0045F06C`), i.e. it is the shared world far plane, not a terrain-specific
value.

Relation to fog: with `D3DFOG_EXP` at density `0.0084`, the fog factor at the
700-unit far plane is `exp(-0.0084 * 700) ≈ 0.0028` — effectively fully fogged,
so geometry reaches the far plane already saturated to `#D8D8FC`. Fog end
distance and far plane do **not** coincide numerically here (`FOGEND` is only
ever `10.0f`/sentinel and is ignored under EXP); the far plane is hidden by fog
saturation instead. Whether the on-screen result matches is a capture question,
not a static one.

## Rename candidates — reported, not applied

The database was not modified. These three names are contradicted by their own
bytes:

1. **`CDXEngine__SetVertexFormatDeferred` (`0x005513D0`)** is not a vertex-format
   setter. Its two-instruction body is
   `MOV byte ptr [ECX+0xE2D], 1` / `MOV dword ptr [ECX+0x2F0], EAX` — exactly the
   dirty flag and value field that `CDXEngine__ApplyPendingRenderState`
   (`0x00551182`–`0x00551190`) flushes to `RenderState_Set(0x26 /* FOGDENSITY */)`.
   Its sole caller passes `FLD float ptr [0x006FBE60]`, the fog-density global.
   Suggested: `CDXEngine__SetFogDensityDeferred`.
2. **`RenderState_Set_23_8C_Compat` (`0x00514030`)** — descriptive but opaque.
   Suggested: `RenderState_SetFogMode` (states `0x23`/`0x8C`, value `D3DFOG_EXP`).
3. **`DAT_00888A78`** — suggested `g_D3DCaps8_RasterCaps`, with the caps block
   base at `0x00888A54` (see table above).

## Method and reproduction

All exports read-only against the maintainer project
`<maintainer Ghidra project directory>` (`BEA` / `BEA.exe`), Ghidra 12.1.2:

```
analyzeHeadless.bat <PROJECT_LOCATION> BEA -process BEA.exe -noanalysis -readOnly \
  -scriptPath tools -postScript <Script>.java <args...>
```

| Script | Purpose |
| --- | --- |
| `tools/ExportWeakFunctionList.java` (`mode=all`) | 6,969-function name/signature inventory |
| `tools/ExportFunctionsByAddressDecompile.java` | Function exports for the setters, flush, render, water, landscape (not reproduced here) |
| `tools/ExportFunctionBodyInstructionsByAddress.java` | Full 44-instruction body of `0x00514030` |
| `tools/ExportInstructionsByOperandToken.java` | Program-wide operand scans (546,729 instructions) |
| `tools/ExportInstructionsAroundAddresses.java` | Call-site context windows |
| `tools/ExportRenderStateCallSites.java` (**new, read-only**) | Every `CALL`/`JMP` to the four render-state setters with an 8-instruction walk-back, so literal `(state, value)` pairs are read off the bytes |
