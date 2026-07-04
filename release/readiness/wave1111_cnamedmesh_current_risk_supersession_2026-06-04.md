# Wave1111 CNamedMesh Current-Risk Supersession Readiness

Status: complete static supersession accounting
Date: 2026-06-04
Scope: `wave1111-cnamedmesh-current-risk-supersession`

Wave1111 accounts for `1 row` from the Wave1108 current focused denominator:

| Address | Saved row | Evidence |
| --- | --- | --- |
| `0x004bc050` | `CNamedMesh__VFunc02_RemoveFromOccupancyAndForward` | Wave458 `mesh-optimization-wave458` saved the name/signature/comment/tag correction; Wave944 `building-namedmesh-lifecycle-review-wave944` re-read the row as context with metadata, tags, xrefs, decompile, vtable slots, and verified backup evidence. |

Static read-back anchors:

- Current focused accounting after Wave1111: `25/1179 = 2.12%` of current focused candidates: 1179.
- Current static Ghidra function-quality closure remains `6410/6410 = 100.00%` with `0 / 0 / 0` commentless / exact-undefined / `param_N` debt.
- The row has current signature `void __fastcall CNamedMesh__VFunc02_RemoveFromOccupancyAndForward(void * this)`.
- The row's current comment ties slot 2 to `CWorld__RemoveUnitFromOccupancyGrid_Thunk`, `VFuncSlot_02_004f41b0`, `0x00418450 CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh`, and vtable `0x005dd5f0` slot 2.
- Wave944 xrefs re-read `0x00418460 -> 0x004bc050` as an `UNCONDITIONAL_CALL` and `0x005dd5f8 -> 0x004bc050` as a DATA vtable ref.
- Wave944 decompile re-read the body as removing this object from world occupancy and then forwarding through the saved base cleanup path represented as `CComplexThing__Shutdown(this)`.
- Wave458 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-162849_post_wave458_mesh_optimization_verified`.
- Wave944 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-050722_post_wave944_building_namedmesh_lifecycle_review_verified`.
- Latest completed Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.
- Mutation status: no new Ghidra export, no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

Probe token anchor: Wave1111; wave1111-cnamedmesh-current-risk-supersession; 25/1179 = 2.12%; 1 row; current focused candidates: 1179; Wave458; mesh-optimization-wave458; Wave944; building-namedmesh-lifecycle-review-wave944; 0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward; 0x00418450 CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh; 0x005dd5f0; [maintainer-local-ghidra-backup-root]\BEA_20260516-162849_post_wave458_mesh_optimization_verified; [maintainer-local-ghidra-backup-root]\BEA_20260528-050722_post_wave944_building_namedmesh_lifecycle_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; no new Ghidra export; no mutation.

## Boundary

This is static supersession accounting only. Runtime NamedMesh/world-occupancy behavior, exact CNamedMesh/CBuildingNamedMesh layouts, exact source virtual names, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
