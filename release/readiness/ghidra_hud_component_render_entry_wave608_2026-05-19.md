# Ghidra HUD Component Render Entry Wave608

Status: ready
Date: 2026-05-19

## Scope

Wave608 saved signature/comment/tag hardening for the next HUD component queue head:

- `0x0054b800 CHudComponent__RenderPassEntry`

The pass made no rename. It used retail-binary evidence from the direct caller `CHudComponent__RenderPass`, xrefs, instructions, decompiles, post-save tags, and queue telemetry. The current Stuart source snapshot does not include a matching `DXHud.cpp` body, so no source-parity tag was applied.

## What Changed

- `CHudComponent__RenderPassEntry` now has the saved signature `void __cdecl CHudComponent__RenderPassEntry(void * mesh_entry, void * hud_component)`.
- The direct caller `CHudComponent__RenderPass` loads each sub-item pointer from the owned mesh table at `+0x160`, passes it first, and passes the `CHudComponent` `this` pointer second.
- The helper is a plain `cdecl` body ending in `RET c3`.
- The saved comment records the bounded render behavior: skip mesh types `2` and `4`, render type `1` 2D mesh triangles through `CVBufTexture__SetVBFormat`, `CVBufTexture__SetIBFormat`, `CVBufTexture__AddVertices`, `CVBufTexture__AddIndices`, and `CVBufTexture__Render`, and emit `DebugTrace` for type `3` or unknown mesh types.

## Evidence

- Apply script: `tools/ApplyHudComponentRenderEntryWave608.java`
- Focused probe: `tools/ghidra_hud_component_render_entry_wave608_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave608-hud-component-render-entry-0054b800/`
- Dry/apply/final dry:
  - dry: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`
  - apply: `updated=1 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
  - final dry: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `1` metadata row, `1` tag row, `1` xref row, `512` instruction rows, `488` target-function instruction rows, and `1` decompile row.
- Caller context export verified `CHudComponent__RenderPassEntry(*(int *)(*(int *)(iVar1 + 0x160) + iVar2 * 4),this);`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-214647_post_wave608_hud_component_render_entry_verified`
  - `fileCount=19`
  - `totalBytes=161418119`
  - `DiffCount=0`

## Queue Delta

Post-Wave608 queue telemetry:

- Total functions: `6093`
- Commented functions: `3117`
- Commentless functions: `2976`
- Exact-undefined signatures: `1304`
- `param_N` signatures: `1064`
- Comment-backed proxy: `3117/6093 = 51.16%`
- Strict clean-signature proxy: `3072/6093 = 50.42%`
- Next queue head: `0x0054bf80 CDXMeshVB__ctor_like_0054bf80`

Delta from Wave607:

- `+1` commented row
- `-1` commentless row
- `0` exact-undefined signatures
- `-1` `param_N` signature

## Limits

This is static retail evidence only. Source-body identity, exact mesh-entry/component layouts, runtime HUD behavior, concrete render output, BEA patching, and rebuild parity remain unproven.
