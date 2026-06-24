# Ghidra Texture Filter MMX Dispatch Wave890 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `texture-filter-mmx-dispatch-wave890`

Task anchor: Wave890 texture filter MMX dispatch.

Wave890 saved Ghidra function comments and tags for five raw commentless texture filter/downsample dispatch rows from `0x0057d0ee CWaypointManager__BoxBlurPackedColorRows_Scalar` through `0x0057d47e CDXTexture__InitMmxDispatchAndRun`. Existing names and signature displays were preserved; the pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0057d0ee CWaypointManager__BoxBlurPackedColorRows_Scalar` | Scalar packed-color row filter/downsample fallback reached from the SIMD body and dispatch slot `0x00657974`; current CWaypointManager owner label is preserved as existing Ghidra state. |
| `0x0057d244 CDXTexture__Downsample2x2Average32` | Scalar 32-bit 2x2 average/downsample fallback reached through dispatch slot `0x00657978` when MMX support is disabled. |
| `0x0057d32e CWaypointManager__BoxBlurPackedColorRows_SIMD` | MMX/SIMD packed-color row filter/downsample kernel selected for dispatch slots `0x00657974` and `0x00657978`, falling back to `0x0057d0ee` for non-4-aligned widths. |
| `0x0057d446 CWaypointManager__InitMmxDispatchAndRun` | Calls `CDXTexture__IsMmxEnabledBySystemConfig`, writes slot `0x00657974` and paired slot `0x00657978`, then computed-dispatches slot `0x00657974`. |
| `0x0057d47e CDXTexture__InitMmxDispatchAndRun` | Calls `CDXTexture__IsMmxEnabledBySystemConfig`, selects `CDXTexture__Downsample2x2Average32` or `CWaypointManager__BoxBlurPackedColorRows_SIMD`, mirrors the paired slot, then computed-dispatches slot `0x00657978`. |

Read-back evidence:

- `ApplyTextureFilterMmxDispatchWave890.java dry`: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyTextureFilterMmxDispatchWave890.java apply`: `updated=5 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyTextureFilterMmxDispatchWave890.java final dry`: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 5 metadata rows, 5 tag rows, 15 xref rows, 307 instruction rows, and 5 decompile rows.
- Queue after Wave890: 6113 total, 6059 commented, 54 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict proxy `6059/6113 = 99.12%`.
- Next raw commentless row: `0x00580a05 CDXTexture__UploadSurfaceRegionWithFallback`.
- Verified backup: `G:\GhidraBackups\BEA_20260526-043655_post_wave890_texture_filter_mmx_dispatch_verified`, 19 files, 173149063 bytes, `DiffCount=0`.

What this proves:

- The 5 target function rows exist in the saved Ghidra project.
- The saved names/signature displays match pre-state metadata.
- The saved comments and tags include `texture-filter-mmx-dispatch-wave890` and `wave890-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to metadata, tags, xrefs, instructions, decompile exports, and the dispatch slots `0x00657974` / `0x00657978`.

What remains unproven:

- Exact owner/source identity for the CWaypointManager-labelled texture filter rows.
- Exact texture surface/context layout.
- Hidden dispatch ABI and pointer-table ownership.
- Runtime CPU selection and filtering/downsample behavior.
- BEA patching behavior.
- Rebuild parity.
