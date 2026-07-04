# Ghidra CDXMeshVB / CFastVB Strip Wave650 Readiness

Status: ready for public-safe release notes
Date: 2026-05-20

Wave650 CDXMeshVB/CFastVB strip hardening saved signatures, comments, and tags for fifteen adjacent CDXMeshVB/CFastVB strip-building rows:

- `0x0056eb50 CDXMeshVB__SetTriangleStripDebugFlag`
- `0x0056eb60 CDXMeshVB__SetEmitDegenerateFlag`
- `0x0056eb70 CDXMeshVB__SetWordIndexModeFlag`
- `0x0056eb80 CDXMeshVB__SetBatchSplitThreshold`
- `0x0056eb90 CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer`
- `0x0056f260 CFastVB__ReleaseBufferAndResetTriplet_0056f260`
- `0x0056f280 CFastVB__CountWordElements`
- `0x0056f2a0 CFastVB__InsertWordSpanFilled`
- `0x0056f4b0 CFastVB__CopyWordRangeToBufferAndAdvanceEnd`
- `0x0056f500 CFastVB__InitWordSpanHeader`
- `0x0056f520 CFastVB__ReleaseBufferAndResetTriplet_0056f520`
- `0x0056f540 CFastVB__FindEdgeRecord`
- `0x0056f580 CFastVB__ResolveOppositeAdjacencyRecord`
- `0x0056f5c0 CFastVB__ContainsTriangleTriplet`
- `0x0056f620 CFastVB__BuildTriangleAdjacency`

The pass made no renames, no function-boundary changes, and no executable-byte changes. Evidence is static retail Ghidra decompile, instruction, xref, saved metadata, saved comments, and saved tags. The current source checkout does not include `DXMeshVB.cpp`, `DXMeshVB.h`, or `FastVB.cpp`, so no source-parity tag was applied.

## Evidence

- Script: `tools/ApplyCdxMeshVbCFastVbStripWave650.java`
- Probe: `tools/ghidra_cdxmeshvb_cfastvb_strip_wave650_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave650-cdxmeshvb-cfastvb-strip`
- Dry/apply/final-dry: `updated=0 skipped=15 renamed=0 would_rename=0 signature_updated=15 missing=0 bad=0`, then `updated=15 skipped=0 renamed=0 would_rename=0 signature_updated=15 missing=0 bad=0`, then `updated=0 skipped=15 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `15` metadata rows, `15` tag rows, `86` xref rows, `1335` instruction rows, and `15` clean decompile rows
- Queue after Wave650: `6093` total, `3518` commented, `2575` commentless, `1217` exact-undefined signatures, `790` `param_N` signatures
- Comment-backed proxy: `3518/6093 = 57.74%`
- Strict clean-signature proxy: `3468/6093 = 56.92%`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-215037_post_wave650_cdxmeshvb_cfastvb_strip_verified`, `19` files, `162990983` bytes, `DiffCount=0`
- Next queue head: `0x0056fce0 CFastVB__SelectTriangleWithMaxOpenEdges`

## Boundaries

Wave650 proves observed static CDXMeshVB strip-state setters, strip-batch emission, CFastVB word-span helpers, edge lookup, opposite-adjacency resolution, triangle-triplet containment, and adjacency-record construction evidence only. Exact CDXMeshVB/CFastVB/word-span/edge-record/triangle-record layouts, runtime strip quality, concrete D3D output, BEA patching, and rebuild parity remain unproven.
