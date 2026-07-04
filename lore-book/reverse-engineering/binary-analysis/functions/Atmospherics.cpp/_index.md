# Atmospherics.cpp Functions

Wave1216 (`wave1216-render-resource-texture-hud-tail-current-risk-review`) re-read `CAtmosphericsProfile__ResetAndInitSnowResources` as part of the render/resource/texture/HUD tail current-risk review. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified`. Runtime atmospherics/weather behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

> Source File: Atmospherics.cpp | Binary: BEA.exe
> Debug Path: 0x00622ec4 (`[maintainer-local-source-export-root]\Atmospherics.cpp`)

## Overview

> **Queue status (2026-06-01):** Ghidra export-contract closure **6246/6246** (Wave1063 keeps the loaded function-quality export closed; not evidence-grade semantics or runtime proof). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

The Atmospherics system handles weather and environmental effects including rain, snow, lightning, and wind. It uses a linked list of atmospheric objects (stored at `DAT_006601a8`) that are updated and rendered each frame. The system registers console commands and variables for runtime tweaking of weather parameters.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00404a00 | Atmospherics__Init | Initialize atmospherics system, load textures, register console vars | ~400 bytes; saved signature `void __cdecl ...(void)` |
| 0x00404b90 | Atmospherics__ResetAndUpdate | Reset wind vector to zero, call update on all atmospheric objects | ~64 bytes; saved signature `void __cdecl ...(void)` |
| 0x00404bd0 | Atmospherics__UpdateAll | Iterate all atmospherics, call vtable method +0x08 (Update) | ~32 bytes; saved signature `void __cdecl ...(void)` |
| 0x00404bf0 | Atmospherics__RenderAll | Iterate all atmospherics, call vtable method +0x04 (Render) | ~32 bytes; saved signature `void __cdecl ...(void)` |
| 0x00404c10 | Atmospherics__Shutdown | Clean up all atmospheric objects and release texture | ~128 bytes; saved signature `void __cdecl ...(void)` |
| 0x00404c90 | Atmospherics__NotifyAll | Iterate all atmospherics, call vtable method +0x14 with parameter | ~48 bytes; saved signature `void __cdecl ...(int eventCode)` |

## Global Variables

| Address | Name | Type | Purpose |
|---------|------|------|---------|
| 0x00660188 | atm_lightningdensity | float | Lightning density (0-1) |
| 0x0066018c | atm_snowdensity | float | Snow density (0-1) |
| 0x00660190 | atm_raindensity | float | Rain density (0-1) |
| 0x00660198 | atm_windvector | vec3 | Prevailing wind vector (X, Y, Z) |
| 0x006601a8 | g_AtmosphericsList | ptr | Head of linked list of atmospheric objects |
| 0x006601ac | g_SnowTexture | CTexture* | Snow layer texture handle |

## Console Commands

| Command | Description |
|---------|-------------|
| `ListAtmospherics` | Displays a list of the atmospheric effects |

## Console Variables

| Variable | Type | Description |
|----------|------|-------------|
| `atm_windvector` | vec3 (type 5) | The prevailing wind vector |
| `atm_raindensity` | float (type 4) | Rain density (0-1) |
| `atm_snowdensity` | float (type 4) | Snow density (0-1) |
| `atm_lightningdensity` | float (type 4) | Lightning density (0-1) |

## Key Observations

1. **Linked List Structure**: Atmospheric objects form a singly-linked list with the next pointer at offset +0x04 from the object base.

2. **VTable Layout**: Each atmospheric object has a vtable pointer at offset 0. The vtable methods are:
   - +0x04: Render
   - +0x08: Update
   - +0x0C: Reset (called by ResetAndUpdate)
   - +0x10: Destructor
   - +0x14: Notify (takes parameter)

3. **Texture Loading**: The snow texture is loaded from `Atmospherics/Snow/SnowLayer.tga` during initialization.

4. **Memory Allocation**: Uses custom memory allocator (OID__AllocObject) with sizes 0x3a4 (932 bytes) and 0x334 (820 bytes) for different atmospheric types.

5. **Exception Handling**: Init and shutdown use structured exception handling (SEH) with unwind handlers at 0x005d0ff0 and 0x005d1006.

## Wave1063 Atmospherics Snow/Resource Re-Audit (2026-06-01)

Wave1063 (`atmospherics-snow-resource-review-wave1063`, `wave1063-readback-verified`) re-read the Atmospherics lifecycle/list-dispatch functions and the CAtmosphericsProfile/DXSnow snow-resource context after post-100 closure. Fresh exports showed the six core rows still had correct saved names, signatures, and comments, but empty function tags. The wave saved tag normalization for these rows only: `0x00404a00 Atmospherics__Init`, `0x00404b90 Atmospherics__ResetAndUpdate`, `0x00404bd0 Atmospherics__UpdateAll`, `0x00404bf0 Atmospherics__RenderAll`, `0x00404c10 Atmospherics__Shutdown`, and `0x00404c90 Atmospherics__NotifyAll`.

Context anchor: `0x00555020 CAtmosphericsProfile__ResetAndInitSnowResources`. Pre primary/context exports verified `6/6/6/802/6` and `11/11/12/272/11` rows; post exports verified `17` metadata rows, `17` tag rows, `18` xref rows, `1074` function-body instruction rows, and `17` decompile rows. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1187/1548 = 76.68%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-222739_post_wave1063_atmospherics_snow_resource_review_verified`.

The pass made no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, and did not launch BEA. Runtime weather/snow/render/CVar/list-dispatch behavior, exact Atmospherics/CAtmosphericsProfile/DXSnow/CTexture/CVBufTexture layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1063; atmospherics-snow-resource-review-wave1063; 0x00404a00 Atmospherics__Init; 0x00404b90 Atmospherics__ResetAndUpdate; 0x00404bd0 Atmospherics__UpdateAll; 0x00404bf0 Atmospherics__RenderAll; 0x00404c10 Atmospherics__Shutdown; 0x00404c90 Atmospherics__NotifyAll; 0x00555020 CAtmosphericsProfile__ResetAndInitSnowResources; 812/1408 = 57.67%; 1187/1548 = 76.68%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-222739_post_wave1063_atmospherics_snow_resource_review_verified; tag normalization.

## Wave874 CAtmosphericsProfile / DXSnow Static Setup (2026-05-25)

Wave874 atmospherics profile (`atmospherics-profile-wave874`, `wave874-readback-verified`) created seven missing function boundaries and saved signatures/comments/tags for ten snow/weather renderer rows adjacent to the Atmospherics profile. These rows are high-importance weather-renderer infrastructure with low local-evidence density, not low-importance filler. The pass made no executable-byte changes and did not launch BEA.

Probe anchors for this wave: `Wave874 atmospherics profile`, `0x00554e80 DXSnow__StaticInitPrimaryTransformGlobals`, `0x00554f50 DXSnow__StaticInitDisableSnowConfig`, `0x00554f70 DXSnow__StaticDestroyDisableSnowConfig`, `0x00554f80 CAtmosphericsProfile__ctor`, `0x00555010 CAtmosphericsProfile__VFunc00_GetNameString`, `0x00555410 CAtmosphericsProfile__ReleaseResources`, `0x00555460 CAtmosphericsProfile__RenderOverlay`, `0x00555600 CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay`, `0x00555af0 DXSnow__StaticZeroOverlayVectorGlobals`, `0x00555b10 DXSnow__StaticInitOverlayTransformGlobals`, `DISABLE_SNOW`, next raw commentless row `0x00555be0 CVBufTexture__DrawSpriteEx`, strict proxy `5872/6113 = 96.06%`, and verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260525-201600_post_wave874_atmospherics_profile_verified`.

| Address | Static read-back evidence |
| --- | --- |
| `0x00554e80 DXSnow__StaticInitPrimaryTransformGlobals` | Created from pointer table `0x00622ab8`; writes transform-basis values into globals `0x009c7f88` through `0x009c7fb4`. |
| `0x00554f50 DXSnow__StaticInitDisableSnowConfig` | Created from pointer table `0x00622abc`; registers `DISABLE_SNOW` via `CVar__Init` and the cleanup callback `0x00554f70`. |
| `0x00554f70 DXSnow__StaticDestroyDisableSnowConfig` | Created from callback pointer evidence; destroys the `DISABLE_SNOW` CVar object through `CTweak__dtor_base_thunk_004530a0`. |
| `0x00554f80 CAtmosphericsProfile__ctor` | `Atmospherics__Init` callsite `0x00404a98`; installs vtable `0x005e5974` and initializes profile/snow defaults. |
| `0x00555010 CAtmosphericsProfile__VFunc00_GetNameString` | Created from vtable slot `+0x00`; returns string pointer `0x0065246c`, dumped as `Snow`. |
| `0x00555410 CAtmosphericsProfile__ReleaseResources` | Vtable slot `+0x10`; releases `this+0x0c`, destroys/frees `this+0x08`, and releases `this+0x10`. |
| `0x00555460 CAtmosphericsProfile__RenderOverlay` | Called from `0x00555a09`; copies matrix globals, samples camera/viewpoint state, clamps `atm_snowdensity`, and renders through `this+0x08`. |
| `0x00555600 CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay` | Created from vtable slot `+0x08`, dispatched by `Atmospherics__UpdateAll`; gates snow/shader/resource state, copies wind globals, iterates 50 entries from `this+0x68`, calls `CDXTexture__GetAnimatedFrame`, and calls the overlay renderer. |
| `0x00555af0 DXSnow__StaticZeroOverlayVectorGlobals` | Created from pointer table `0x00622ac0`; clears overlay vector globals `0x009c8000`, `0x009c8004`, and `0x009c8008`. |
| `0x00555b10 DXSnow__StaticInitOverlayTransformGlobals` | Created from pointer table `0x00622ac4`; writes transform-basis values into globals `0x009c7fd0` through `0x009c7ffc`. |

Queue after Wave874: `6113` total functions, `5872` commented, `241` commentless, 0 exact-undefined signatures, 0 `param_N`, and strict clean-signature proxy `5872/6113 = 96.06%`. Concrete CAtmosphericsProfile, DXSnow, CVBufTexture, CTexture, and shader object layouts, exact matrix padding/row-column semantics, runtime snow/weather visual behavior, runtime console/CVar behavior, BEA patching, and rebuild parity remain deferred.

## Wave741 unwind head callbacks

Wave741 unwind head saved `void __cdecl Unwind@005d0ff0(void)` and `void __cdecl Unwind@005d1006(void)` with the `unwind-head-wave741` and `wave741-readback-verified` tags. The saved comments record scope-table DATA xrefs `0x00619f04` and `0x00619f0c`, Atmospherics.cpp debug path `0x00622ec4`, lines `0x70` and `0x73`, memtype `0x65`, and `OID__FreeObject_Callback` on the pointer at `EBP-0x10`.

This is saved static retail Ghidra metadata only. Runtime weather cleanup behavior, exact source-body identity, BEA patching, and rebuild parity remain unproven.

## Related Functions (Not in Atmospherics.cpp)

These functions interact closely with the Atmospherics system but are defined in other source files:

| Address | Name | Purpose |
|---------|------|---------|
| 0x00404960 | CAtmospheric__Unlink | Remove atmospheric object from linked list |
| 0x00404920 | CAtmospheric__Link | Add atmospheric object to linked list |
| 0x00404210 | CAtmospheric__Process | Main per-instance simulation/update path (target selection, orientation update, movement step, event scheduling) |

## Lifecycle Signature Tranche (2026-05-10)

Fresh headless dry/apply/read-back saved proof-boundary signatures/comments for the lifecycle/list helpers above. Wave517 on 2026-05-17 superseded the earlier attribution of `0x004046d0` and `0x004f44a0` as CAtmospheric/trail helpers; current saved Ghidra maps those bodies to CAnimation / CComplexThing animation flow.

| Address | Current saved signature | Evidence boundary |
|---------|-------------------------|-------------------|
| 0x00404a00 | `void __cdecl Atmospherics__Init(void)` | Global init loads `SnowLayer`, allocates profile/cloud objects, and registers `ListAtmospherics` plus `atm_*` console variables. |
| 0x00404b90 | `void __cdecl Atmospherics__ResetAndUpdate(void)` | Clears prevailing wind vector globals and walks `DAT_006601a8`, dispatching list entry virtual slot `+0xc`. |
| 0x00404bd0 | `void __cdecl Atmospherics__UpdateAll(void)` | Walks `DAT_006601a8` and dispatches each entry virtual slot `+0x8`. |
| 0x00404bf0 | `void __cdecl Atmospherics__RenderAll(void)` | Walks `DAT_006601a8` and dispatches each entry virtual slot `+0x4`. |
| 0x00404c10 | `void __cdecl Atmospherics__Shutdown(void)` | Releases cached snow texture state, dispatches each entry virtual slot `+0x10`, unlinks entries, and frees objects. |
| 0x00404c90 | `void __cdecl Atmospherics__NotifyAll(int eventCode)` | Walks `DAT_006601a8` and dispatches each entry virtual slot `+0x14` with `eventCode`. |

This is saved Ghidra signature/comment refinement only. It does not prove concrete `CAtmospheric` layouts, exact source identity, concrete vtable slot names, runtime weather/trail behavior, or rebuild parity.

## Wave615 CAtmosphericsProfile Snow Boundary Correction (2026-05-20)

Wave615 corrected the stale `DXSnow.cpp` split boundary that previously started at `0x0055515e`. Current saved Ghidra evidence records `0x00555020` as the full `CAtmosphericsProfile` vtable slot `+0x0c` body:

| Address | Current saved name | Evidence boundary |
|---------|--------------------|-------------------|
| `0x00554f80` | `CAtmosphericsProfile__ctor` | Installs vtable `0x005e5974` and initializes snow/profile fields including `+0x14`, `+0x388`, `+0x38c`, and `+0x3a0`. |
| `0x00555020` | `CAtmosphericsProfile__ResetAndInitSnowResources` | Vtable slot address `0x005e5980` points here; `Atmospherics__ResetAndUpdate` dispatches atmospheric-object slot `+0x0c`. Body covers `0x00555020-0x00555403`, including the old `0x0055515e` split address. |
| `0x0055515e` | no function entry | Former stale `CDXSnow__Init` row. Post-Wave615 metadata/decompile exports report it missing as a function entry, and instruction exports show it inside the corrected `0x00555020` body. |
| `0x00555410` | `CAtmosphericsProfile__ReleaseResources` | Adjacent follow-on release helper; vtable slot address `0x005e5984` points here. |
| `0x00555460` | `CAtmosphericsProfile__RenderOverlay` | Adjacent renderer reached by callsite `0x00555a09`; runtime visual/weather behavior remains separate proof. |

Claim boundary: this is static saved-Ghidra boundary/signature/comment/tag evidence only. Runtime snow/weather behavior remains unproven. Exact source method identity, concrete `CAtmosphericsProfile` / `CDXSnow` layout, full vtable names, BEA patching, and rebuild parity remain deferred.

## Wave517 Superseded Animation Attribution (2026-05-17)

Wave517 revisited the old Atmospherics/trail-adjacent bodies with CComplexThing source parity, xrefs, decompile, instruction, and Ghidra read-back evidence. Treat these names as the current saved Ghidra truth:

| Address | Current saved name | Superseded older label |
|---------|--------------------|------------------------|
| 0x004046d0 | `CAnimation__ctor` | `CAtmospheric__Constructor` |
| 0x00404790 | `CAnimation__Process` | `CAtmospheric__UpdateBlendState` |
| 0x00404860 | `CAnimation__SetAnimMode` | `CAtmospheric__ConfigureTrail` |
| 0x004048c0 | `CAnimation__GetRenderFrame` | `CAtmospheric__GetInterpolatedBlendValue` |
| 0x004f3c80 | `CThing__GetRenderThingFrameIncrement` | `CAtmospheric__GetSamplerValueOrDefault` |
| 0x004f44a0 | `CComplexThing__SetAnimMode` | `CThing__AddTrail` |

Claim boundary: this is static saved-Ghidra/source-parity correction only. It does not prove runtime animation behavior, runtime mission-script behavior, exact CAnimation/CComplexThing layouts, or rebuild parity.

## Superseded Attribution

Earlier notes attributed `0x00404010` to `CAtmospheric__Destructor`. The 2026-05-09 CAnimal owner-correction wave supersedes that label: saved Ghidra now records `0x00404010` as `CAnimal__dtor_base` after `CAnimal` RTTI/vtable and animal-list evidence. Treat any older atmospheric-owner use of this address as stale.

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
