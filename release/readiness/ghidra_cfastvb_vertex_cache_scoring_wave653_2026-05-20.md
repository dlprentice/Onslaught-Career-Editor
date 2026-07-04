# Ghidra CFastVB Vertex Cache/Scoring Wave653 Readiness

Status: ready for public-safe release notes
Date: 2026-05-20

Wave653 CFastVB vertex-cache/scoring hardening saved signatures, comments, and tags for seven adjacent vertex-cache, batch-scoring, edge-scoring, and strip-candidate generation helpers:

- `0x005721f0 CFastVB__SeedVertexCacheFromTriangleRefs`
- `0x00572310 CFastVB__SeedVertexCacheFromTriangle`
- `0x005723c0 CFastVB__ComputeAverageVertexOverlapScore_005723c0`
- `0x00572490 CFastVB__CountTriangleVerticesInSet_00572490`
- `0x00572500 CFastVB__CountResolvedOppositeEdges`
- `0x00572570 CFastVB__ComputeAverageUnresolvedEdgesPerBatch`
- `0x005725e0 CFastVB__GenerateStripCandidatesFromAdjacency`

The pass corrected the stale `CDXTexture__InsertUniqueTripletAtFront` owner label at `0x00572310` to `CFastVB__SeedVertexCacheFromTriangle`. It made no function-boundary changes and no executable-byte changes. Evidence is static retail Ghidra decompile, instruction, xref, saved metadata, saved comments, and saved tags. The current source checkout does not include `DXMeshVB.cpp`, `DXMeshVB.h`, or `FastVB.cpp`, so no source-parity tag was applied.

## Evidence

- Script: `tools/ApplyCFastVBVertexCacheScoringWave653.java`
- Probe: `tools/ghidra_cfastvb_vertex_cache_scoring_wave653_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave653-cfastvb-vertex-cache-scoring`
- Dry/apply/final-dry: `updated=0 skipped=7 renamed=0 would_rename=1 signature_updated=7 missing=0 bad=0`, then `updated=7 skipped=0 renamed=1 would_rename=0 signature_updated=7 missing=0 bad=0`, then `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `7` metadata rows, `7` tag rows, `8` xref rows, `315` instruction rows, and `7` clean decompile rows
- Queue after Wave653: `6093` total, `3543` commented, `2550` commentless, `1217` exact-undefined signatures, `765` `param_N` signatures
- Comment-backed proxy: `3543/6093 = 58.15%`
- Strict clean-signature proxy: `3491/6093 = 57.30%`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-192250_post_wave653_cfastvb_vertex_cache_scoring_verified`, `19` files, `163023751` bytes, `DiffCount=0`
- Next queue head: `0x00572e40 CTexture__DestroyNodeTreeAndStorage`

## Boundaries

Wave653 proves observed static CFastVB vertex-cache seeding, vertex-overlap scoring, triangle-in-cache counting, resolved-opposite-edge counting, unresolved-edge batch scoring, and candidate-bucket generation only. Exact cache/span/candidate/tree layouts, runtime strip quality, concrete D3D output, BEA patching, and rebuild parity remain unproven.
