# Ghidra CDXLandscape Core Wave602

Status: ready
Date: 2026-05-19

## Scope

Wave602 saved signature/comment/tag hardening for the CDXLandscape core terrain-data tranche:

- `0x00544fc0 CDXLandscape__BuildVertexBuffer`
- `0x00545070 CDXLandscape__Reset`
- `0x005453d0 CDXLandscape__LoadCloudShadowTexture`
- `0x005453f0 CDXLandscape__SetTileData`

No function renames were made. The pass used retail-binary evidence from xrefs, caller/callee instructions, decompiles, queue telemetry, and existing CDXLandscape lifecycle/resource context.

## What Changed

- `CDXLandscape__BuildVertexBuffer` now records the ECX-only vertex-buffer rebuild loop: lock `this+0x28`, emit a `0x41` by `0x41` grid of `0x14`-byte vertices, sample packed heightfield data every 8 units, scale heights by `DAT_006fbdf4`, and unlock the buffer.
- `CDXLandscape__Reset` now records the terrain reset path: destroy the existing `+0x24` resource-record array, reset the landscape-texture update queue, allocate one or two `0x34`-byte resource records depending on multiplayer state, rebuild mip levels and the vertex buffer, populate `64x64` tile records, compute tile complexity scores, reset patch slots, invalidate the landscape texture cache, and load waves texture state.
- `CDXLandscape__LoadCloudShadowTexture` now records the `CEngine__InitResources` call path and the `CTexture__FindTexture("clouds_shadow.tga", 4, 0, -1, 1, 1)` store to `this+0x38`.
- `CDXLandscape__SetTileData` now has a `void __thiscall` signature with `tile_context` and `record_index`; `RET 0x8` and `CEngine__UpdatePos` prove two stack arguments after ECX.

## Evidence

- Apply script: `tools/ApplyCDXLandscapeCoreWave602.java`
- Focused probe: `tools/ghidra_cdxlandscape_core_wave602_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave602-cdxlandscape-core-00544fc0/`
- Dry/apply/final dry:
  - dry: `updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0`
  - apply: `updated=4 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
  - final dry: `updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `4` metadata rows, `4` tag rows, `7` xref rows, `1476` instruction rows, and `4` decompile rows.
- Verified backup: `G:\GhidraBackups\BEA_20260519-184356_post_wave602_cdxlandscape_core_verified`
  - `fileCount=19`
  - `totalBytes=161221511`
  - `DiffCount=0`
  - `manifestHash=ff0bc70f109410ec28abe3a06adadb2b641ffce463c9824cf9ed3e539a2b3be1`

## Queue Delta

Post-Wave602 queue telemetry:

- Total functions: `6093`
- Commented functions: `3092`
- Commentless functions: `3001`
- Exact-undefined signatures: `1320`
- `param_N` signatures: `1073`
- Comment-backed proxy: `3092/6093 = 50.75%`
- Strict clean-signature proxy: `3047/6093 = 50.01%`
- Next queue head: `0x00545410 CDXLandscape__Render`

Delta from Wave601:

- `+4` commented rows
- `-4` commentless rows
- `-4` exact-undefined signatures
- `0` `param_N` signatures

## Limits

This is static retail evidence only. Runtime terrain rendering, runtime cloud-shadow/waves behavior, resource ownership under lost-device/reset conditions, exact CDXLandscape/CLandscape/CLandscapeTexture/CVBuffer/CIBuffer/CDXSurf layouts, exact source-body identity, BEA patching, and rebuild parity remain unproven.
