# Ghidra CDXLandscape LOD/Damage Wave605

Status: ready
Date: 2026-05-19

## Scope

Wave605 saved signature/comment/tag hardening for the next CDXLandscape LOD and landscape-damage tranche:

- `0x00546b10 CDXLandscape__ResetCameraPosition`
- `0x00546b40 CDXLandscape__UpdateLOD`
- `0x005475d0 CDXEngine__ApplyLandscapeDamageStamp`
- `0x00547a60 CDXEngine__ComputeLandscapeTileComplexityScore`

No function renames were made. The pass used retail-binary evidence from xrefs, caller/callee instructions, decompiles, queue telemetry, and the prior CDXLandscape lifecycle/core/render/target context.

## What Changed

- `CDXLandscape__ResetCameraPosition` now has a `void __fastcall` signature with `this`; all five fresh callsites load `ECX` from `DAT_0089c9b0`, and the body writes the `1234567.0f` sentinel to resource-record camera/cache slots at `+0x14` and, for multiplayer, `+0x48`.
- `CDXLandscape__UpdateLOD` now has a `void __thiscall` signature with `engine_context_470` and `record_index`; `RET 0x8` plus the `CDXEngine__Render` and `CDXLandscape__Render` callsites prove two stack arguments after `ECX`.
- `CDXEngine__ApplyLandscapeDamageStamp` now has a `void __stdcall` signature with `world_x`, `world_z`, and `stamp_value`; `RET 0xc` and the tree/rubble/world-load callsites prove the three-stack-argument shape.
- `CDXEngine__ComputeLandscapeTileComplexityScore` now has a `double __stdcall` signature with `tile_index`; `RET 0x4` proves one stack argument, the body does not consume `ECX`, and `CDXLandscape__Reset` casts the returned double to float before storing tile-record complexity.

## Evidence

- Apply script: `tools/ApplyCDXLandscapeLodDamageWave605.java`
- Focused probe: `tools/ghidra_cdxlandscape_lod_damage_wave605_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave605-cdxlandscape-lod-damage-00546b10/`
- Dry/apply/final dry:
  - dry: `updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0`
  - apply: `updated=4 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
  - final dry: `updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `4` metadata rows, `4` tag rows, `13` xref rows, `36004` instruction rows, and `4` decompile rows.
- Verified backup: `G:\GhidraBackups\BEA_20260519-201654_post_wave605_cdxlandscape_lod_damage_verified`
  - `FileCount=19`
  - `TotalBytes=161319815`
  - `DiffCount=0`
  - `ManifestHash=fa146228213520868a20790fe8b99cd58adf5bb9bc89b9e22b3aa1c36b6900d5`

## Queue Delta

Post-Wave605 queue telemetry:

- Total functions: `6093`
- Commented functions: `3103`
- Commentless functions: `2990`
- Exact-undefined signatures: `1311`
- `param_N` signatures: `1071`
- Comment-backed proxy: `3103/6093 = 50.93%`
- Strict clean-signature proxy: `3058/6093 = 50.19%`
- Next queue head: `0x00547d40 DXMemBuffer__SetBufferSize`

Delta from Wave604:

- `+4` commented rows
- `-4` commentless rows
- `-2` exact-undefined signatures
- `-2` `param_N` signatures

## Limits

This is static retail evidence only. Exact `engine_context_470` class semantics, CDXLandscape resource/tile/patch layouts, damage-entry layout, terrain deformation behavior, runtime LOD rendering, exact source-body identity, BEA patching, and rebuild parity remain unproven.
