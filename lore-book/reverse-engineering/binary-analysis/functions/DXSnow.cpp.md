# DXSnow.cpp Functions

> Source file evidence: `DXSnow.cpp` strings in `BEA.exe`
> Debug path string: `0x00652534` (`[maintainer-local-source-export-root]\DXSnow.cpp`)
> Last updated: 2026-05-25

## Wave874 CAtmosphericsProfile / DXSnow Static Setup

Wave874 atmospherics profile (`atmospherics-profile-wave874`, `wave874-readback-verified`) created seven missing function boundaries and saved signatures/comments/tags for ten DXSnow/CAtmosphericsProfile snow-weather renderer rows. These rows are high-importance weather-renderer infrastructure with low local-evidence density, not low-importance filler. The pass made no executable-byte changes and did not launch BEA.

Probe anchors for this wave: `Wave874 atmospherics profile`, `0x00554e80 DXSnow__StaticInitPrimaryTransformGlobals`, `0x00554f50 DXSnow__StaticInitDisableSnowConfig`, `0x00554f70 DXSnow__StaticDestroyDisableSnowConfig`, `0x00554f80 CAtmosphericsProfile__ctor`, `0x00555010 CAtmosphericsProfile__VFunc00_GetNameString`, `0x00555410 CAtmosphericsProfile__ReleaseResources`, `0x00555460 CAtmosphericsProfile__RenderOverlay`, `0x00555600 CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay`, `0x00555af0 DXSnow__StaticZeroOverlayVectorGlobals`, `0x00555b10 DXSnow__StaticInitOverlayTransformGlobals`, `DISABLE_SNOW`, next raw commentless row `0x00555be0 CVBufTexture__DrawSpriteEx`, strict proxy `5872/6113 = 96.06%`, and verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260525-201600_post_wave874_atmospherics_profile_verified`.

| Address | Current saved signature | Static evidence |
| --- | --- | --- |
| `0x00554e80 DXSnow__StaticInitPrimaryTransformGlobals` | `void __cdecl DXSnow__StaticInitPrimaryTransformGlobals(void)` | Created from pointer table `0x00622ab8`; writes transform-basis values into globals `0x009c7f88` through `0x009c7fb4`. |
| `0x00554f50 DXSnow__StaticInitDisableSnowConfig` | `void __cdecl DXSnow__StaticInitDisableSnowConfig(void)` | Created from pointer table `0x00622abc`; registers `DISABLE_SNOW` with `CVar__Init` and cleanup callback `0x00554f70`. |
| `0x00554f70 DXSnow__StaticDestroyDisableSnowConfig` | `void __cdecl DXSnow__StaticDestroyDisableSnowConfig(void)` | Cleanup callback for the `DISABLE_SNOW` CVar object through `CTweak__dtor_base_thunk_004530a0`. |
| `0x00554f80 CAtmosphericsProfile__ctor` | `void * __fastcall CAtmosphericsProfile__ctor(void * this)` | `Atmospherics__Init` callsite `0x00404a98`; installs vtable `0x005e5974` and initializes snow/profile fields. |
| `0x00555010 CAtmosphericsProfile__VFunc00_GetNameString` | `char * __fastcall CAtmosphericsProfile__VFunc00_GetNameString(void * this)` | Created from vtable `0x005e5974` slot `+0x00`; returns `0x0065246c`, dumped as `Snow`. |
| `0x00555410 CAtmosphericsProfile__ReleaseResources` | `void __fastcall CAtmosphericsProfile__ReleaseResources(void * this)` | Vtable slot `+0x10`; releases `this+0x0c`, destroys/frees `this+0x08`, and releases `this+0x10`. |
| `0x00555460 CAtmosphericsProfile__RenderOverlay` | `void __fastcall CAtmosphericsProfile__RenderOverlay(void * this)` | Called from `0x00555a09`; copies matrix globals, samples camera/viewpoint globals, clamps `atm_snowdensity`, and renders through `this+0x08`. |
| `0x00555600 CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay` | `void __fastcall CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay(void * this)` | Created from vtable slot `+0x08`, dispatched by `Atmospherics__UpdateAll`; gates snow/shader/resource state, copies wind globals, iterates 50 entries, calls `CDXTexture__GetAnimatedFrame`, and calls the overlay renderer. |
| `0x00555af0 DXSnow__StaticZeroOverlayVectorGlobals` | `void __cdecl DXSnow__StaticZeroOverlayVectorGlobals(void)` | Created from pointer table `0x00622ac0`; clears overlay vector globals `0x009c8000`, `0x009c8004`, and `0x009c8008`. |
| `0x00555b10 DXSnow__StaticInitOverlayTransformGlobals` | `void __cdecl DXSnow__StaticInitOverlayTransformGlobals(void)` | Created from pointer table `0x00622ac4`; writes transform-basis values into globals `0x009c7fd0` through `0x009c7ffc`. |

Post-Wave874 queue telemetry: `6113` total functions, `5872` commented, `241` commentless, 0 exact-undefined signatures, 0 `param_N`, and strict clean-signature proxy `5872/6113 = 96.06%`. Concrete CAtmosphericsProfile, DXSnow, CVBufTexture, CTexture, and shader object layouts, exact matrix padding/row-column semantics, runtime snow/weather visual behavior, runtime console/CVar behavior, BEA patching, and rebuild parity remain deferred.

## Wave615 Boundary Correction

Wave615 supersedes the older `0x0055515e CDXSnow__Init` note. The saved Ghidra database now records the full vtable-dispatched body as:

| Address | Current saved name | Current saved signature | Evidence boundary |
| --- | --- | --- | --- |
| `0x00555020` | `CAtmosphericsProfile__ResetAndInitSnowResources` | `void __thiscall CAtmosphericsProfile__ResetAndInitSnowResources(void * this)` | Vtable `0x005e5974` slot `+0x0c` / address `0x005e5980` points here; `Atmospherics__ResetAndUpdate` dispatches slot `+0x0c`. Body covers `0x00555020-0x00555403`. |
| `0x0055515e` | no longer a function entry | n/a | Former stale `CDXSnow__Init` split address; post-Wave615 metadata/decompile exports report it missing as a function entry, and instruction export shows it inside the corrected `0x00555020` body. |

The older `0x0055515e` boundary began after the SEH prologue and early resource setup, used stack artifacts such as `unaff_EBP`, and had no xrefs. Treat old docs, screenshots, or notes that identify `0x0055515e` as the function start as stale.

## Observed Behavior

The corrected body is reached through the atmospherics profile vtable and appears to reset/reinitialize snow resources for the profile object:

- Clears resource fields at `this+0x08`, `this+0x0c`, and `this+0x10`.
- When snow/render support is enabled, finds `Atmospherics/Snow/Snow.tga`.
- Compiles/creates the embedded snow vertex shader script.
- Allocates a `0x68`-byte `CVBufTexture` through the CDX memory manager with the `DXSnow.cpp` debug path.
- Stores the snow vertex/index buffer resource at `this+0x08`.
- Configures the vertex/index buffer formats and marks the buffer persistent.
- Registers `cg_snow`, `cg_snow_period`, `cg_snow_scale`, and `cg_snow_fadedistance`.
- Generates 1000 snowflake quads, each with four vertices and six indices.
- Fills 50 additional four-float entries beginning around `this+0x68`.
- Unlocks the vertex and index buffers before returning at `0x00555403`.

## Console Variables

| CVar | String Address | Description | Storage |
| --- | --- | --- | --- |
| `cg_snow` | `0x00652474` | Snow enable/disable | `this+0x14` |
| `cg_snow_period` | `0x006524f0` | Snow period | `this+0x388` |
| `cg_snow_scale` | `0x006524c4` | Snow scale | `this+0x3a0` |
| `cg_snow_fadedistance` | `0x00652490` | Snow flake fade distance | `this+0x38c` |

## Related Atmospherics Evidence

- `CAtmosphericsProfile__ctor` (`0x00554f80`) installs vtable `0x005e5974` and initializes the fields later used by the snow body, including defaults near `+0x388`, `+0x38c`, and `+0x3a0`.
- `Atmospherics__ResetAndUpdate` (`0x00404b90`) walks `DAT_006601a8` and dispatches vtable slot `+0x0c`; for the `CAtmosphericsProfile` vtable, that slot is `0x00555020`.
- `CAtmosphericsProfile__ReleaseResources` (`0x00555410`) begins immediately after the corrected body and releases fields at `+0x08`, `+0x0c`, and `+0x10`.
- `CAtmosphericsProfile__RenderOverlay` (`0x00555460`) is adjacent follow-on rendering evidence, but its exact runtime snow/weather output remains a separate proof task.

## Limits

This page records static retail Ghidra read-back evidence only. Runtime snow/weather behavior remains unproven. Exact source method identity, concrete `CAtmosphericsProfile` / `CDXSnow` / `CVBufTexture` / shader layouts, vertex format semantics, actual level weather enablement, BEA patching, and rebuild parity remain deferred.
