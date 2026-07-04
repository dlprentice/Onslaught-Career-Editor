# Ghidra CDXSurf Core Wave616

Status: ready
Date: 2026-05-20

## Scope

Wave616 hardened `12` CDXSurf rows at the current high-signal queue head:

- `0x005563d0 CDXSurf__RenderSurface`
- `0x00556460 CDXSurf__Init`
- `0x00556470 CDXSurf__LoadWavesTexture`
- `0x00556490 CDXSurf__CreateSurfaceArray`
- `0x005565b0 CDXSurf__DestroyBuffers`
- `0x005565d0 CDXSurf__CreateSurfaceStrip`
- `0x005569e0 CDXSurf__Destroy`
- `0x00556a30 CDXSurf__Render`
- `0x00556d70 CDXSurf__ScalarDeletingDestructor`
- `0x00556d90 CDXSurf__dtor`
- `0x00556f80 CDXSurf__DestroyRenderTarget`
- `0x00556fc0 CDXSurf__SetupSurface`

The tranche is a saved-Ghidra signature/comment/tag pass with no renames and no function-boundary changes. It also recorded the adjacent CDXSurf vtable at `0x005e59a0`, including the bounded rows at slots `0..7` and the unbounded pointer targets `0x00558600` and `0x00556e90`.

## What Changed

- Saved bounded signatures/comments/tags for the sprite wrapper, water-strip lifecycle, render pass, destructor pair, render-target cleanup, and setup helper.
- Documented `CDXSurf__RenderSurface` as a cdecl wrapper over `CVBufTexture__DrawSpriteEx` with default UV bounds.
- Documented water-strip allocation/render evidence from the chunk reader, `mixers\\waves.tga`, two `CVBuffer` objects per strip, `DAT_0082b4a4` UV ordering, sine-offset vertices, and D3D triangle-strip draw calls.
- Documented `CDXSurf__SetupSurface` as the vtable slot `+0x18` / `RET 0x18` setup helper while leaving unbounded vtable pointer targets at `0x00558600` and `0x00556e90` deferred.
- Preserved the first apply log where Ghidra inserted an implicit `this` receiver and exposed a read-back signature mismatch for `CDXSurf__CreateSurfaceStrip`; the corrected dry/apply/final-dry passes are clean.

## Evidence

- Apply script: `tools/ApplyCDXSurfCoreWave616.java`
- Focused probe: `tools/ghidra_cdxsurf_core_wave616_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave616-cdxsurf-core/`
- Initial dry: `updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0`
- Preserved first apply mismatch: `updated=11 skipped=0 renamed=0 would_rename=0 missing=0 bad=1`, with `REPORT: Save succeeded`.
- Corrected thiscall dry/apply/final dry: `updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=1 skipped=11 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0`.
- RenderSurface parameter-label dry/apply/final dry: `updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=1 skipped=11 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0`.
- Read-back exports verified `15` context metadata rows plus `2` expected missing unbounded vtable targets, `15` tag rows plus the same `2` misses, `169` xref rows, `1445` instruction rows, `15` decompile rows plus `2` misses, and `32` vtable-slot rows.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-020900_post_wave616_cdxsurf_core_verified`
  - `sourceFileCount=19`
  - `destFileCount=19`
  - `sourceBytes=161614727`
  - `destBytes=161614727`
  - `DiffCount=0`

## Queue Delta

Post-Wave616 queue telemetry:

- Total functions: `6093`
- Commented functions: `3172`
- Commentless functions: `2921`
- Exact-undefined signatures: `1260`
- `param_N` signatures: `1056`
- Comment-backed proxy: `3172/6093 = 52.06%`
- Strict clean-signature proxy: `3127/6093 = 51.32%`
- Next queue head: `0x00557300 CDXTexture__LoadTextureFromFile`

Delta from Wave615:

- `+12` commented rows
- `-12` commentless rows
- `-11` exact-undefined signatures
- `0` `param_N` signatures
- `+12` strict clean rows

## Limits

This is static retail Ghidra signature/comment/tag/vtable evidence only. Runtime water/render behavior remains unproven. Exact `CDXSurf`, `CVBuffer`, `CVBufTexture`, `CDXTexture`, render-state, D3D, and serialized wave-strip layouts, concrete source identity, BEA patching, and rebuild parity remain deferred.
