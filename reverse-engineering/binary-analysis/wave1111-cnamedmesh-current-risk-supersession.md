# Wave1111 CNamedMesh Current-Risk Supersession

Status: complete static supersession accounting
Last updated: 2026-06-04
Scope: `wave1111-cnamedmesh-current-risk-supersession`

Wave1111 accounts for `1 row` from the Wave1108 current focused denominator as already covered by Wave458 and Wave944 static evidence. This is no new Ghidra export, no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

## Accounting

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6410/6410 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave1108 current focused candidates | current focused candidates: 1179 |
| Wave1111 current focused supersession accounting | `25/1179 = 2.12%` |

## Superseded Row

| Address | Name | Prior evidence |
| --- | --- | --- |
| `0x004bc050` | `CNamedMesh__VFunc02_RemoveFromOccupancyAndForward` | Wave458 `mesh-optimization-wave458` saved the correction; Wave944 `building-namedmesh-lifecycle-review-wave944` re-read the row as Building/CBuildingNamedMesh lifecycle context. |

Wave458 corrected `0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward` from the older slot-number address label, with signature `void __fastcall CNamedMesh__VFunc02_RemoveFromOccupancyAndForward(void * this)`, tags including `mesh-optimization-wave458`, `named-mesh`, `occupancy`, and `vtable-slot`, xrefs from `0x00418450 CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh` and DATA vtable slot `0x005dd5f0`/`0x005dd5f8`, and vtable slot `2` pointing at `0x004bc050`. Wave458 backup: `G:\GhidraBackups\BEA_20260516-162849_post_wave458_mesh_optimization_verified`.

Wave944 then re-read the Building/CBuildingNamedMesh lifecycle cluster with fresh read-only metadata, tags, xrefs, instructions, decompile, vtable slots, and verified backup evidence. The `0x004bc050` decompile body calls `CWorld__RemoveUnitFromOccupancyGrid_Thunk(this)`, then forwards through the saved base cleanup path represented in decompile as `CComplexThing__Shutdown(this)`, while the saved comment preserves the `VFuncSlot_02_004f41b0` forwarding boundary. Wave944 backup: `G:\GhidraBackups\BEA_20260528-050722_post_wave944_building_namedmesh_lifecycle_review_verified`.

Latest completed Ghidra review backup remains `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Probe token anchor: Wave1111; wave1111-cnamedmesh-current-risk-supersession; 25/1179 = 2.12%; 1 row; current focused candidates: 1179; Wave458; mesh-optimization-wave458; Wave944; building-namedmesh-lifecycle-review-wave944; 0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward; 0x00418450 CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh; 0x005dd5f0; G:\GhidraBackups\BEA_20260516-162849_post_wave458_mesh_optimization_verified; G:\GhidraBackups\BEA_20260528-050722_post_wave944_building_namedmesh_lifecycle_review_verified; G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; no new Ghidra export; no mutation.

## Boundary

This wave closes current-risk accounting for this one row only. It does not prove runtime NamedMesh/world-occupancy behavior, exact CNamedMesh/CBuildingNamedMesh layouts, exact source virtual names, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
