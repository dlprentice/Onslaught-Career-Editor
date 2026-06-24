# Wave1174 Building / NamedMesh Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-06
Tag: `wave1174-building-namedmesh-current-risk-review`

Wave1174 accounts for `5 Building/CBuildingNamedMesh/CNamedMesh current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Targets:

| Address | Name | Static read-back evidence |
| --- | --- | --- |
| `0x00418450` | `CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh` | DATA xref `0x005d9114` under CBuildingNamedMesh vtable `0x005d910c`; removes the object from world occupancy and forwards to `CNamedMesh__VFunc02_RemoveFromOccupancyAndForward`. |
| `0x004178a0` | `CBuilding__ProcessClosingAndUnshuttingAnimations` | DATA xref `0x005d8fbc`; runs closing/unshutting animation gates over fields `+0x254/+0x25c/+0x260/+0x264/+0x268`, checks CUnit spawner readiness, and dispatches closing/unshutting animations. |
| `0x004bbcd0` | `CNamedMesh__VFunc_09_004bbcd0` | DATA xref `0x005dd614` in CNamedMesh vtable `0x005dd5f0` slot 9 plus call context from `0x004183a8`; initializes through `CActor__Init`, snapshots position globals, conditionally schedules event `3000`, and adds the object to world occupancy/static-shadow tracking. |
| `0x00418120` | `CBuilding__AdvanceOpenCloseAnimationState` | DATA xref `0x005d8fa0`; compares active animation ids through vfunc `+0x58`, dispatches open/close/shut transitions through vfunc `+0xf0`, and updates state fields `+0x254/+0x264`. |
| `0x004183d0` | `CBuildingNamedMesh__dtor_base` | Call xref from `0x00418433 CBuildingNamedMesh__scalar_deleting_dtor`; resets CBuildingNamedMesh vtable slots and forwards to `CActor__dtor_base`. |

Evidence counts:

- Fresh Ghidra export verified `5` metadata rows, `5` tag rows, `6 xref rows`, `288 instruction rows`, and `5` decompile rows.
- Prior context: Wave944 `building-namedmesh-lifecycle-review-wave944` re-read the broader Building/CBuildingNamedMesh lifecycle cluster; Wave1111 `wave1111-cnamedmesh-current-risk-supersession` already accounted for `0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward`.
- Verified backup: `G:\GhidraBackups\BEA_20260606-075804_post_wave1174_building_namedmesh_current_risk_review_verified` (`19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`).
- Current-risk accounting after Wave1174: `680/1179 = 57.68%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 499; current risk candidates: 6166; focused threshold `15`; not Wave911 reconstruction.

A Codex read-only consult independently checked tracked prior evidence and target membership; final claims are based on Codex root's fresh Ghidra exports, backup verification, and repo evidence.

Boundary: runtime building animation behavior, runtime NamedMesh/world-occupancy behavior, exact CBuilding/CBuildingNamedMesh/CNamedMesh/CUnit layouts, exact source virtual names, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1174; wave1174-building-namedmesh-current-risk-review; 680/1179 = 57.68%; 5 Building/CBuildingNamedMesh/CNamedMesh current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 499; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 6 xref rows; 288 instruction rows; CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh; CBuilding__ProcessClosingAndUnshuttingAnimations; CNamedMesh__VFunc_09_004bbcd0; CBuilding__AdvanceOpenCloseAnimationState; CBuildingNamedMesh__dtor_base; Wave944; building-namedmesh-lifecycle-review-wave944; Wave1111; wave1111-cnamedmesh-current-risk-supersession; 0x005d8fbc; 0x005d8fa0; 0x005d910c; 0x005d9114; 0x005dd5f0; G:\GhidraBackups\BEA_20260606-075804_post_wave1174_building_namedmesh_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
