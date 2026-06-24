# Ghidra CDXLandscape Target/Shadow Wave604

Status: ready
Date: 2026-05-19

## Scope

Wave604 saved signature/comment/tag hardening for the CDXLandscape target and shadow tranche:

- `0x00546220 CDXLandscape__SetRenderTarget`
- `0x005463f0 CDXLandscape__ReleaseRenderTarget`
- `0x00546460 CDXLandscape__ReleaseSurfaces`
- `0x00546490 CDXLandscape__RenderShadowMap`
- `0x00546900 CDXLandscape__RenderTileRange`

No function renames were made. The pass used retail-binary evidence from xrefs, caller/callee instructions, decompiles, queue telemetry, and the prior CDXLandscape lifecycle/core/render context.

## What Changed

- `CDXLandscape__SetRenderTarget` now has a `bool __thiscall` signature with `target_surface`; `RET 0x4` plus the `CGame__Render` and `CDXLandscape__RenderShadowMap` callers prove one stack argument after the implicit ECX save-pair pointer.
- `CDXLandscape__ReleaseRenderTarget` now has a `void __thiscall` ECX-only signature; the `CGame__Render` caller and plain `RET` prove the local surface-pair restore/release shape.
- `CDXLandscape__ReleaseSurfaces` now has a `void __thiscall` ECX-only signature; `CGame__Render` final/unwind paths and plain `RET` prove the release-only surface-pair cleanup shape.
- `CDXLandscape__RenderShadowMap` now has a `bool __thiscall` signature with `record_index`; `CDXLandscape__RenderTerrain` pushes `0`, and the body guards shadow resources, switches render targets, draws the base/LOD tile ranges, calls `CWaterRenderSystem__RenderShadowPass(DAT_0089c9b4)`, and restores D3D state.
- `CDXLandscape__RenderTileRange` now has a `void __thiscall` signature with four coordinate bounds; `RET 0x10` and the `CDXEngine__RenderMultipassLayerA` callsite prove the four-stack-argument shape.

## Evidence

- Apply script: `tools/ApplyCDXLandscapeTargetShadowWave604.java`
- Focused probe: `tools/ghidra_cdxlandscape_target_shadow_wave604_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave604-cdxlandscape-target-shadow-00546220/`
- Dry/apply/final dry:
  - initial dry: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`
  - preserved first apply mismatch: `updated=2 skipped=0 renamed=0 would_rename=0 missing=0 bad=3`, caused by non-`this` ECX parameter modeling on three `__thiscall` rows
  - corrected dry: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`
  - corrected apply: `updated=3 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`
  - final dry: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `5` metadata rows, `5` tag rows, `8` xref rows, `9045` instruction rows, and `5` decompile rows.
- Verified backup: `G:\GhidraBackups\BEA_20260519-194745_post_wave604_cdxlandscape_target_shadow_verified`
  - `FileCount=19`
  - `TotalBytes=161287047`
  - `DiffCount=0`
  - `ManifestHash=657b521f4bc34af239e3cd22b7a3fa0505bbe4fb8f1e0b92ccf6cccdc11299ed`

## Queue Delta

Post-Wave604 queue telemetry:

- Total functions: `6093`
- Commented functions: `3099`
- Commentless functions: `2994`
- Exact-undefined signatures: `1313`
- `param_N` signatures: `1073`
- Comment-backed proxy: `3099/6093 = 50.86%`
- Strict clean-signature proxy: `3054/6093 = 50.12%`
- Next queue head: `0x00546b10 CDXLandscape__ResetCameraPosition`

Delta from Wave603:

- `+5` commented rows
- `-5` commentless rows
- `-5` exact-undefined signatures
- `0` `param_N` signatures

## Limits

This is static retail evidence only. Exact D3D interface semantics, COM/surface ownership lifetime, CDXLandscape/resource/tile-record layouts, runtime terrain/shadow rendering, exact source-body identity, BEA patching, and rebuild parity remain unproven.
