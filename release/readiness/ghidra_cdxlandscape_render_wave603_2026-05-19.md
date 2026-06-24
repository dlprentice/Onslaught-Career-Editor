# Ghidra CDXLandscape Render Wave603

Status: ready
Date: 2026-05-19

## Scope

Wave603 saved signature/comment/tag hardening for the CDXLandscape render tranche:

- `0x00545410 CDXLandscape__Render`
- `0x00545590 CDXLandscape__RenderTerrain`

No function renames were made. The pass used retail-binary evidence from xrefs, caller/callee instructions, decompiles, queue telemetry, and the prior CDXLandscape lifecycle/resource/core context.

## What Changed

- `CDXLandscape__Render` now has a `void __thiscall` signature with `engine_context_470` and `record_index`; `RET 0x8` and the `CDXEngine__Render` callsite prove two stack arguments after ECX.
- `CDXLandscape__Render` now records the high-level render wrapper: optional reset on `DAT_0089ce44` changes, `CDXLandscape__UpdateLOD(engine_context_470, record_index)`, world-matrix setup from `DAT_008c0280..DAT_008c028c` and `DAT_008aa9c0`, render-state/cache changes, cached-light application, `CDXLandscape__RenderTerrain(record_index)`, and cached-light restore.
- `CDXLandscape__RenderTerrain` now has a `void __thiscall` signature with `record_index`; `RET 0x4` and the direct caller prove one stack argument after ECX.
- `CDXLandscape__RenderTerrain` now records the terrain draw path: `this+0x24 + record_index*0x34`, cloud-shadow scroll updates for record `0`, render-validation passes, landscape/waves/cloud-shadow texture-stage setup, index/vertex buffer binding, base and LOD tile drawing, optional `CDXLandscape__RenderShadowMap(0)`, and render-flag restore.

## Evidence

- Apply script: `tools/ApplyCDXLandscapeRenderWave603.java`
- Focused probe: `tools/ghidra_cdxlandscape_render_wave603_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave603-cdxlandscape-render-00545410/`
- Dry/apply/final dry:
  - dry: `updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`
  - apply: `updated=2 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
  - final dry: `updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `2` metadata rows, `2` tag rows, `2` xref rows, `1818` instruction rows, and `2` decompile rows.
- Verified backup: `G:\GhidraBackups\BEA_20260519-191021_post_wave603_cdxlandscape_render_verified`
  - `fileCount=19`
  - `totalBytes=161254279`
  - `DiffCount=0`
  - `manifestHash=bfb0b4f044d5d6c0aa6708eeee074e5ec1c4a65f6ab66448d51d0efa573f22ba`

## Queue Delta

Post-Wave603 queue telemetry:

- Total functions: `6093`
- Commented functions: `3094`
- Commentless functions: `2999`
- Exact-undefined signatures: `1318`
- `param_N` signatures: `1073`
- Comment-backed proxy: `3094/6093 = 50.78%`
- Strict clean-signature proxy: `3049/6093 = 50.04%`
- Next queue head: `0x00546220 CDXLandscape__SetRenderTarget`

Delta from Wave602:

- `+2` commented rows
- `-2` commentless rows
- `-2` exact-undefined signatures
- `0` `param_N` signatures

## Limits

This is static retail evidence only. Exact `engine_context_470` class semantics, matrix/light-state semantics, texture-stage/resource-record layouts, runtime terrain/shadow rendering, exact source-body identity, BEA patching, and rebuild parity remain unproven.
