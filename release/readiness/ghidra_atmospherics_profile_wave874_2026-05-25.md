# Ghidra Atmospherics Profile Wave874 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `atmospherics-profile-wave874`

Wave874 atmospherics profile created seven missing function boundaries and saved signatures, comments, and tags for ten high-importance snow/weather renderer rows from `0x00554e80 DXSnow__StaticInitPrimaryTransformGlobals` through `0x00555b10 DXSnow__StaticInitOverlayTransformGlobals`. The pass made seven function-boundary creations, no executable-byte changes, and no BEA/runtime launches.

These rows are high-importance weather-renderer infrastructure with low local-evidence density, not low-importance filler. The main correction is that the CAtmosphericsProfile vtable now resolves slot `+0x00` to a `"Snow"` name getter and slot `+0x08` to the snow update/render coordinator, while the nearby DXSnow static initializer table now resolves the atmospherics-side transform/config/vector helpers.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00554e80 DXSnow__StaticInitPrimaryTransformGlobals` | Pointer-table DATA xref `0x00622ab8`; writes transform-basis values into globals `0x009c7f88` through `0x009c7fb4`; exact matrix padding remains unproven. |
| `0x00554f50 DXSnow__StaticInitDisableSnowConfig` | Pointer-table DATA xref `0x00622abc`; calls `CVar__Init(&0x009c7f78, "DISABLE_SNOW", 0)` and registers cleanup callback `0x00554f70`. |
| `0x00554f70 DXSnow__StaticDestroyDisableSnowConfig` | Callback immediate xref `0x00554f61`; jumps through `CTweak__dtor_base_thunk_004530a0` for the `DISABLE_SNOW` CVar object. |
| `0x00554f80 CAtmosphericsProfile__ctor` | `Atmospherics__Init` callsite `0x00404a98`; installs vtable `0x005e5974`, initializes snow defaults `+0x388/+0x38c/+0x3a0`, and gates `+0x14`. |
| `0x00555010 CAtmosphericsProfile__VFunc00_GetNameString` | Created from vtable `0x005e5974` slot `+0x00`; returns string pointer `0x0065246c`, dumped as `"Snow"`. |
| `0x00555410 CAtmosphericsProfile__ReleaseResources` | Vtable slot `+0x10` / slot address `0x005e5984`; releases resources at `this+0x08`, `this+0x0c`, and `this+0x10`. |
| `0x00555460 CAtmosphericsProfile__RenderOverlay` | Called from `0x00555a09`; copies matrix globals, samples camera/viewpoint state, clamps `atm_snowdensity`, and renders through `this+0x08`. |
| `0x00555600 CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay` | Created from vtable slot `+0x08`, dispatched by `Atmospherics__UpdateAll`; gates snow/shader/resource state, iterates 50 entries from `this+0x68`, calls `CDXTexture__GetAnimatedFrame`, and calls the overlay renderer. |
| `0x00555af0 DXSnow__StaticZeroOverlayVectorGlobals` | Pointer-table DATA xref `0x00622ac0`; clears globals `0x009c8000`, `0x009c8004`, and `0x009c8008`. |
| `0x00555b10 DXSnow__StaticInitOverlayTransformGlobals` | Pointer-table DATA xref `0x00622ac4`; writes transform-basis values into globals `0x009c7fd0` through `0x009c7ffc`; exact matrix padding remains unproven. |

Read-back evidence:

- `CreateFunctionsFromAddressList.java dry`: `created=0 would_create=7 already_exists=0 renamed=0 would_rename=0 failed=0`
- `CreateFunctionsFromAddressList.java apply`: `created=7 would_create=0 already_exists=0 renamed=7 would_rename=0 failed=0`
- `ApplyAtmosphericsProfileWave874.java dry`: `updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyAtmosphericsProfileWave874.java apply`: `updated=10 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyAtmosphericsProfileWave874.java final dry`: `updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 10 metadata rows, 10 tag rows, 10 xref rows, 601 instruction rows, 10 decompile rows, 8 vtable rows, 6 pointer-table rows, and 16 helper metadata rows.
- Queue after Wave874: 6,113 total functions, 5,872 commented, 241 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5872/6113 = 96.06%`, strict clean-signature proxy `5872/6113 = 96.06%`.
- Next raw commentless row: `0x00555be0 CVBufTexture__DrawSpriteEx`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-201600_post_wave874_atmospherics_profile_verified`, 19 files, 172,592,007 bytes, `DiffCount=0`.

What this proves:

- The ten target function rows exist in the saved Ghidra project.
- Seven missing function boundaries were created from vtable, pointer-table, or callback-pointer evidence.
- The saved signatures have no `undefined` return and no `param_N` names.
- The saved comments and tags include `atmospherics-profile-wave874` and `wave874-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to vtable/pointer-table DATA refs, strings, helper metadata, decompile, and instruction exports.

What remains unproven:

- Exact source method names for every helper.
- Concrete CAtmosphericsProfile, DXSnow, CVBufTexture, CTexture, and shader object layouts.
- Exact matrix padding/row-column semantics.
- Runtime snow/weather visual behavior.
- Runtime console/CVar behavior for `DISABLE_SNOW`.
- BEA patching behavior.
- Rebuild parity.
