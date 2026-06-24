# Ghidra Wave900+ Through Wave1100 Recheck

Status: validation gate for current Wave900+ static re-audit scope
Date: 2026-06-04
Scope: Wave900 through Wave1100

This note records the aggregate recheck scope after Wave1100. It is a gate over static evidence structure, focused probes, readiness notes, backup references, apply-log coverage, and the current zero-debt Ghidra queue. It does not prove runtime behavior, exact source-layout identity, gameplay outcomes, BEA patching, or rebuild parity.

Current anchor:

- Latest focused wave: Wave1100 (`cmeshpart-load-geometry-review-wave1100`), read-only review.
- Latest readiness note: `release/readiness/ghidra_cmeshpart_load_geometry_review_wave1100_2026-06-04.md`.
- Focused probe: `tools/ghidra_cmeshpart_load_geometry_review_wave1100_probe.py`.
- Aggregate command: `py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1100 --check`.
- Static closure: `6410/6410 = 100.00%`.
- Expanded static surface: `1560/1560 = 100.00%`.
- Wave911 focused progress: `812/1408 = 57.67%`.
- Wave911 top-500 risk-ranked progress: `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

Wave1100 probe token anchor: Wave1100; cmeshpart-load-geometry-review-wave1100; 0x004a51f0 CMeshPart__FreeResources; 0x004ae2b0 CMeshPart__CreatePolyBucket; 0x004ae860 CMeshPart__AllocateGeometry; 0x004aede0 CMeshPart__LoadOldStyle_VersionA; 0x004af470 CMeshPart__LoadVerticesAndTriangles; 0x004afbb0 CMeshPart__LoadVerticesWithBones; 0x004b27a0 CMeshPart__LoadFromStream; 0x004b31f0 CMeshPart__OptimizePolygons; 0x004b3b70 CMeshPart__Clone; 0x004b4250 CMeshPart__Merge; 0x004bae70 CMeshPart__CanOptimizePart_Strict; 0x004bb040 CMeshPart__CanMergeInOptimizePass; C:\dev\ONSLAUGHT2\MeshPart.cpp; resfile_cmeshpartsize; 0x13c; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; read-only review.

Boundary:

- This aggregate gate validates static read-back and repository evidence continuity.
- It does not certify runtime mesh loading, skinning, collision, render, optimization effects, exact layouts, exact source-body identity, BEA patching, gameplay outcomes, or rebuild parity.
