# Ghidra CFastVB Strip Merge/Emission Wave652 Readiness

Status: ready for public-safe release notes
Date: 2026-05-20

Wave652 CFastVB strip merge/emission hardening saved signatures, comments, and tags for eight adjacent strip candidate, merge/order, duplicate-index, and emission helpers:

- `0x00570cb0 CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0`
- `0x00570dd0 CFastVB__MergeAndOrderStripBatches_Impl_00570dd0`
- `0x00571060 CFastVB__IsEven`
- `0x00571080 CFastVB__IsDirectedEdgeInTriangle`
- `0x005710d0 CFastVB__EmitTriangleStripIndexBuffer`
- `0x00571870 CFastVB__HasDuplicateTriangleIndices32`
- `0x00571890 CFastVB__HasDuplicateTriangleIndices16`
- `0x005718c0 CFastVB__MergeAndOrderStripBatches`

The pass made no renames, no function-boundary changes, and no executable-byte changes. Evidence is static retail Ghidra decompile, instruction, xref, saved metadata, saved comments, and saved tags. The current source checkout does not include `DXMeshVB.cpp`, `DXMeshVB.h`, or `FastVB.cpp`, so no source-parity tag was applied.

## Evidence

- Script: `tools/ApplyCFastVBStripMergeEmissionWave652.java`
- Probe: `tools/ghidra_cfastvb_strip_merge_emission_wave652_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave652-cfastvb-strip-merge-emission`
- Dry/apply/final-dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`, then `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `8` metadata rows, `8` tag rows, `16` xref rows, `200` instruction rows, and `8` clean decompile rows
- Queue after Wave652: `6093` total, `3536` commented, `2557` commentless, `1217` exact-undefined signatures, `772` `param_N` signatures
- Comment-backed proxy: `3536/6093 = 58.03%`
- Strict clean-signature proxy: `3486/6093 = 57.21%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-185249_post_wave652_cfastvb_strip_merge_emission_verified`, `18` files, `163023751` bytes, `DiffCount=0`
- Next queue head: `0x005721f0 CFastVB__SeedVertexCacheFromTriangleRefs`

## Boundaries

Wave652 proves observed static CFastVB edge-chain candidate selection, internal/public strip-batch merge and order logic, parity and directed-edge helpers, duplicate-index guards, and dword index emission with restart-separator accounting only. Exact CFastVB/span/batch/edge/triangle layouts, runtime strip quality, concrete D3D index buffer behavior, BEA patching, and rebuild parity remain unproven.
