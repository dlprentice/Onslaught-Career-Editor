# Ghidra Mesh Optimization / NamedMesh Wave458 Evidence

Date: 2026-05-16

## Scope

Wave458 saved Ghidra signature/comment/tag corrections for `5` mesh optimization and NamedMesh targets:

`0x004bae70`, `0x004bb040`, `0x004bb210`, `0x004bbcd0`, and `0x004bc050`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave458-mesh-optimization-current/`
- Apply script: `tools/ApplyMeshOptimizationWave458.java`
- Probe: `tools/ghidra_mesh_optimization_wave458_probe.py`
- Test alias: `npm run test:ghidra-mesh-optimization-wave458`
- Dry summary: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0`
- Apply summary: `updated=5 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `5` metadata rows, `5` tag rows, `10` xref rows, `5` decompile exports plus `index.tsv`, `3205` focused instruction rows, and `16` NamedMesh vtable-slot rows.
- Hardened `CMeshPart__CanOptimizePart_Strict`, `CMeshPart__CanMergeInOptimizePass`, and `CMesh__HasSpecialOptimizationConstraints` as the mesh-part/mesh predicate cluster used by `CMesh__OptimizeParts`.
- Kept `CNamedMesh__VFunc_09_004bbcd0` comment/tag-only because the body uses an EAX-carried init pointer that ordinary Ghidra `__thiscall` storage does not model cleanly.
- Corrected `0x004bc050` to `CNamedMesh__VFunc02_RemoveFromOccupancyAndForward`, vtable `0x005dd5f0` slot 2.
- Queue after refresh: `6057` functions, `2023` commented, `4034` commentless, `1730` undefined signatures, `1645` `param_N` signatures.
- Current telemetry proxies: comment-backed `2023/6057 = 33.40%`; strict comment-plus-clean-signature `1959/6057 = 32.34%`.
- Verified backup: `G:\GhidraBackups\BEA_20260516-162849_post_wave458_mesh_optimization_verified` (`19` files, `Mismatches=0`).

## Boundary

This is static retail-binary evidence only. Runtime mesh optimization behavior, NamedMesh actor behavior, occupancy/static-shadow behavior, exact layouts, exact source identity, BEA launch behavior, game patching, and rebuild parity remain unproven.
