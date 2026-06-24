# Ghidra CFastVB Strip Selection Wave651 Readiness

Status: ready for public-safe release notes
Date: 2026-05-20

Wave651 CFastVB strip-selection hardening saved signatures, comments, and tags for ten adjacent strip-selection and candidate-link rows:

- `0x0056fce0 CFastVB__SelectTriangleWithMaxOpenEdges`
- `0x0056fdc0 CFastVB__SelectNextStripTriangle`
- `0x0056fe70 CFastVB__AreTriangleVertexSetsEquivalent`
- `0x0056fec0 CFastVB__GetSharedVerticesBetweenTriangles`
- `0x0056ff40 CFastVB__TriangleListContainsVertexTriplet_0056ff40`
- `0x00570000 CFastVB__BuildTriangleStripFromSeedRecord`
- `0x00570870 CFastVB__StampRecordOwnerFields`
- `0x005708a0 CFastVB__InsertStripCandidatesIntoBuffer_005708a0`
- `0x00570a90 CFastVB__HasAdjacentFaceTouchingPivotVertex_00570a90`
- `0x00570be0 CFastVB__InitializeCandidateParentLinks_00570be0`

The pass made no renames, no function-boundary changes, and no executable-byte changes. Evidence is static retail Ghidra decompile, instruction, xref, saved metadata, saved comments, and saved tags. The current source checkout does not include `DXMeshVB.cpp`, `DXMeshVB.h`, or `FastVB.cpp`, so no source-parity tag was applied.

## Evidence

- Script: `tools/ApplyCFastVBStripSelectionWave651.java`
- Probe: `tools/ghidra_cfastvb_strip_selection_wave651_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave651-cfastvb-strip-selection`
- Dry/apply/final-dry: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0`, then `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0`, then `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `10` metadata rows, `10` tag rows, `15` xref rows, `250` instruction rows, and `10` clean decompile rows
- Queue after Wave651: `6093` total, `3528` commented, `2565` commentless, `1217` exact-undefined signatures, `780` `param_N` signatures
- Comment-backed proxy: `3528/6093 = 57.90%`
- Strict clean-signature proxy: `3478/6093 = 57.08%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-182101_post_wave651_cfastvb_strip_selection_verified`, `19` files, `162990983` bytes, `DiffCount=0`
- Next queue head: `0x00570cb0 CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0`

## Boundaries

Wave651 proves observed static CFastVB open-edge triangle selection, next-triangle selection, vertex-set comparison, shared-vertex extraction, triangle-list membership, seed-strip growth, owner stamping, candidate-buffer insertion, adjacent-face owner checks, and candidate parent-link initialization only. Exact CFastVB/strip-candidate/span/triangle-record layouts, runtime strip quality, concrete D3D output, BEA patching, and rebuild parity remain unproven.
