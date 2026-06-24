# Wave1174 Building / NamedMesh Current-Risk Review Readiness

Status: complete static read-only evidence
Date: 2026-06-06
Scope: `wave1174-building-namedmesh-current-risk-review`

Wave1174 accounts for `5 Building/CBuildingNamedMesh/CNamedMesh current-risk rows` from the Wave1108 current-risk denominator. Fresh serialized Ghidra exports verified the selected rows and found no Ghidra mutation warranted.

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x00418450` | `CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh` | DATA xref `0x005d9114` under vtable `0x005d910c`; removes world occupancy and forwards to the NamedMesh slot-2 cleanup path. |
| `0x004178a0` | `CBuilding__ProcessClosingAndUnshuttingAnimations` | DATA xref `0x005d8fbc`; closing/unshutting state gates over `+0x254/+0x25c/+0x260/+0x264/+0x268`. |
| `0x004bbcd0` | `CNamedMesh__VFunc_09_004bbcd0` | CNamedMesh vtable `0x005dd5f0` slot 9 / DATA xref `0x005dd614`; `CActor__Init`, event `3000`, and world occupancy/static-shadow add path. |
| `0x00418120` | `CBuilding__AdvanceOpenCloseAnimationState` | DATA xref `0x005d8fa0`; animation-id stepper using vfunc `+0x58` checks and vfunc `+0xf0` transitions. |
| `0x004183d0` | `CBuildingNamedMesh__dtor_base` | Called by `0x00418433 CBuildingNamedMesh__scalar_deleting_dtor`; resets CBuildingNamedMesh vtable slots and forwards to `CActor__dtor_base`. |

Fresh evidence:

- `5` metadata rows, `5` tag rows, `6 xref rows`, `288 instruction rows`, and `5` decompile rows.
- Logs reported `targets=5 found=5 missing=0`, `rows=5 missing=0`, `Wrote 6 rows`, `Wrote 288 function-body instruction rows`, and `targets=5 dumped=5 missing=0 failed=0`.
- Verified backup: `G:\GhidraBackups\BEA_20260606-075804_post_wave1174_building_namedmesh_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Current-risk accounting moved from `675/1179 = 57.25%` to `680/1179 = 57.68%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 499; current risk candidates: 6166.

Mutation status: read-only review; no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

Prior context: Wave944 `building-namedmesh-lifecycle-review-wave944` covered the broader Building/CBuildingNamedMesh lifecycle cluster, and Wave1111 `wave1111-cnamedmesh-current-risk-supersession` already accounted for `0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward`.

Boundary: runtime building animation behavior, runtime NamedMesh/world-occupancy behavior, exact CBuilding/CBuildingNamedMesh/CNamedMesh/CUnit layouts, exact source virtual names, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1174; wave1174-building-namedmesh-current-risk-review; 680/1179 = 57.68%; 5 Building/CBuildingNamedMesh/CNamedMesh current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 499; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 6 xref rows; 288 instruction rows; CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh; CBuilding__ProcessClosingAndUnshuttingAnimations; CNamedMesh__VFunc_09_004bbcd0; CBuilding__AdvanceOpenCloseAnimationState; CBuildingNamedMesh__dtor_base; Wave944; building-namedmesh-lifecycle-review-wave944; Wave1111; wave1111-cnamedmesh-current-risk-supersession; 0x005d8fbc; 0x005d8fa0; 0x005d910c; 0x005d9114; 0x005dd5f0; G:\GhidraBackups\BEA_20260606-075804_post_wave1174_building_namedmesh_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
