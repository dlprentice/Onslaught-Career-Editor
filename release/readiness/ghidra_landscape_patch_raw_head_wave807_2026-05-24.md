# Ghidra Landscape Patch Raw Head Wave807 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `landscape-patch-raw-head-wave807`

Wave807 landscape patch raw head saved a bounded owner/name/signature/comment/tag correction for `0x0048f2f0`, replacing stale `CDXLandscape__SetUpdateBoundsAndRebuildVB` with `CDXPatch__SetGridOriginStepAndRebuild`. The pass made no function-boundary changes and no executable-byte changes.

Representative anchor:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x0048f2f0 CDXPatch__SetGridOriginStepAndRebuild` | `void __thiscall CDXPatch__SetGridOriginStepAndRebuild(void * this, int grid_origin_x, int grid_origin_z, int grid_step, int tile_metadata)` | `RET 0x10` proves four stack arguments after `ECX=this`. `CDXLandscape__UpdateLOD` callsite `0x00546fe6` calls this immediately after `CDXPatchManager__AllocatePatchSlot` returns a patch pointer, passes two tile coordinates scaled by `8`, `grid_step` derived as `4 >> lod_slot`, and a tile-record metadata dword from `[ESI+0x0b]`; the body stores those values into CDXPatch fields `+0x2c`, `+0x30`, `+0x34`, and `+0x4c`, then calls `CDXPatch__RebuildHeightGridVertexBuffer(this)`. |

Read-back evidence:

- Dry: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0`.
- Apply: `updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`, with read-back `OK` and `REPORT: Save succeeded`.
- Final dry: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 211 instruction rows, 1 decompile row, 76 post-callsite instruction rows, and 1 post-caller decompile row.
- Queue after Wave807: 6098 total, 5582 commented, 516 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5582/6098 = 91.54%`, strict clean-signature proxy `5582/6098 = 91.54%`.
- Next raw commentless row: `0x0048f620 CDXEngine__RenderPostMissionOverlayAndMenu`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-105819_post_wave807_landscape_patch_raw_head_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project with the Wave807 name/signature/comment/tags.
- The prior `CDXLandscape__SetUpdateBoundsAndRebuildVB` owner/signature is superseded for this row by saved static retail evidence.
- The corrected callsite decompile names the helper as `CDXPatch__SetGridOriginStepAndRebuild(pvVar12, iStack_c8 * 8, iStack_c4 * 8, 4 >> ..., *(pbVar16 + 0xb))`.

What remains unproven:

- Exact source-body identity.
- Exact CDXPatch field names and full tile-record layout.
- Runtime terrain rendering/GPU behavior.
- BEA patching behavior.
- Rebuild parity.
