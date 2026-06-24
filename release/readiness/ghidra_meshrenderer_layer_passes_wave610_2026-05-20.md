# Ghidra Mesh Renderer Layer-Passes Wave610

Status: ready
Date: 2026-05-20

## Scope

Wave610 saved signature/comment/tag hardening for one render-pass helper:

- `0x0054d530 CMeshRenderer__RenderMeshWithLayerPasses`

The pass made no rename. The current source checkout does not include the matching `DXMeshVB.cpp` or `MeshRenderer.cpp` implementation body, so the evidence is retail Ghidra decompile, instruction, xref, callsite, and post-save tag read-back.

## What Changed

- `CMeshRenderer__RenderMeshWithLayerPasses` now has the saved signature `void __thiscall CMeshRenderer__RenderMeshWithLayerPasses(void * this, void * frame_provider, uint render_flags, void * unused_render_context, void * unused_transform_payload)`.
- `RET 0x10` and the two `CMeshRenderer__RenderMeshCore` callsites at `0x0054a4b6` and `0x0054b265` prove four stack arguments after ECX.
- The receiver comes from the caller's `+0x138` render-object field and matches the adjacent CDXMeshVB-style layout fields used by Wave609: group count `+0x108`, source mesh `+0x10c`, shader pointer `+0x110`, vertex stride `+0x114`, FVF/shader state `+0x118`, and primitive selector `+0x11c`.
- `frame_provider` is optional and supplies frame index/time data through vtable slots `+0x1c` and `+0x18`.
- `render_flags` uses bits `0x10`, `0x20`, and `0x40`; the trailing stack payloads are retained for ABI accuracy but are not consumed by the current retail decompile.
- The body loops material/texture groups, binds vertex buffers, applies shader/FVF state, iterates up to six texture layer passes, handles water/reflection paths through `DAT_0089c9c0` and `DAT_0089c9c4`, restores `DAT_0063012c`, disables vertex shaders when required, and restores render state `0xb`.

## Evidence

- Apply script: `tools/ApplyMeshRendererLayerPassesWave610.java`
- Focused probe: `tools/ghidra_meshrenderer_layer_passes_wave610_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave610-meshrenderer-layer-passes-0054d530/`
- Dry/apply/final dry:
  - dry: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`
  - apply: `updated=1 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
  - final dry: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `1` metadata row, `1` tag row, `2` xref rows, `2201` instruction rows, `763` target-function instruction rows, `1` decompile row, and `114` callsite instruction rows.
- Verified backup: `G:\GhidraBackups\BEA_20260519-224655_post_wave610_meshrenderer_layer_passes_verified`
  - `sourceFileCount=19`
  - `destFileCount=19`
  - `sourceBytes=161418119`
  - `destBytes=161418119`
  - `DiffCount=0`

## Queue Delta

Post-Wave610 queue telemetry:

- Total functions: `6093`
- Commented functions: `3125`
- Commentless functions: `2968`
- Exact-undefined signatures: `1301`
- `param_N` signatures: `1059`
- Comment-backed proxy: `3125/6093 = 51.29%`
- Strict clean-signature proxy: `3080/6093 = 50.55%`
- Next queue head: `0x0054e500 DXPalletizer__InsertColor`

Delta from Wave609:

- `+1` commented row
- `-1` commentless row
- `0` exact-undefined signatures
- `-1` `param_N` signature
- `+1` strict clean row

## Limits

This is static retail evidence only. Exact source identity, exact CDXMeshVB/mesh/texture/render-state layouts, runtime rendering, concrete D3D output, BEA patching, and rebuild parity remain unproven.
