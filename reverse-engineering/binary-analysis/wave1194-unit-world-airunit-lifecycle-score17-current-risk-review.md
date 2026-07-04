# Wave1194 Unit/World/AirUnit Lifecycle Score17 Current-Risk Review

Status: complete static read-back evidence
Date: 2026-06-06
Tag: `wave1194-unit-world-airunit-lifecycle-score17-current-risk-review`

Wave1194 accounts for `9 unit/world/airunit lifecycle score17 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. It saved comment/tag normalization for CUnit add-to-world, CUnit height clamp, CWorld occupancy add/remove thunks, and five aircraft destructor bodies.

The selected rows already had strong prior static evidence from Wave507, Wave557, Wave790, Wave912, Wave959, and Wave1075. Wave1194 does not re-claim those older waves as new discoveries; it gives the rows fresh current-risk read-back, rebuild-grade static boundary tags, and a single current accounting checkpoint.

Evidence summary:

| Address | Function | Fresh read-back contract |
| --- | --- | --- |
| `0x004dfa40` | `CUnit__VFunc08_InitAndAddToWorld` | CUnit-family vtable slot 8 at `0x005dfd60`; body calls `CUnit__Init`, dispatches `+0x48`, clears `this+0x13c`, and calls `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`. |
| `0x004dfd10` | `CUnit__VFunc18_SyncOldVectorAndClampHeight` | Calls `CActor__StickToGround`, then clamps current Z at `this+0x24` and old/render Z at `this+0x94` against `0x006fbdfc`. |
| `0x0050b010` | `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk` | Thin add/shadow thunk reached by UnitAI, Feature, WarspiteDome, Building, NamedMesh, Cannon, Hazard, BattleEngine, and CUnit add-to-world paths. |
| `0x0050b020` | `CWorld__RemoveUnitFromOccupancyGrid_Thunk` | Thin remove thunk reached by Building, BuildingNamedMesh, NamedMesh, Cannon, Dropship, UnitAI, Feature, and Hazard cleanup/remove paths. |
| `0x0050f130` | `CGroundAttackAircraft__Destructor_VFunc01` | Aircraft destructor body reached from scalar-deleting wrapper; clears `this+0x26c` and `this+0x25c` pointer sets, removes `this+0x250` global-list node, then calls `CUnit__dtor_base`. |
| `0x0050f1f0` | `CDropship__Destructor_VFunc01` | Same aircraft destructor body pattern, reached from `CDropship__scalar_deleting_dtor`. |
| `0x0050f260` | `CPlane__Destructor_VFunc01` | Same aircraft destructor body pattern, reached from `CPlane__scalar_deleting_dtor`. |
| `0x0050f2d0` | `CDiveBomber__Destructor_VFunc01` | Same aircraft destructor body pattern, reached from `CDiveBomber__scalar_deleting_dtor`. |
| `0x0050f3b0` | `CFenrir__Destructor_VFunc01` | Same aircraft destructor body pattern, reached from `CFenrir__scalar_deleting_dtor`. |

Read-back counts: `9` metadata rows, `9` tag rows, `26 xref rows`, `177 instruction rows`, and `9 decompile rows`. Dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=9 tags_added=132 missing=0 bad=0`, then `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=9 tags_added=132 missing=0 bad=0`, then final dry updated=0 skipped=9. No rename, no signature change, no function-boundary change, and no executable-byte change occurred.

Wave1108 current focused accounting is `865/1179 = 73.37%`; current risk candidates: 6166; current focused candidates: 1154; live regenerated current focused candidates: 1154; remaining active focused work: 314. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; expanded static surface remains `1560/1560 = 100.00%`.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-193734_post_wave1194_unit_world_airunit_lifecycle_score17_current_risk_review_verified`.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Exact source virtual/destructor identity, concrete CUnit/CWorld/aircraft/grid/set/list layouts, runtime lifecycle/occupancy/height/aircraft teardown behavior, gameplay parity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1194; wave1194-unit-world-airunit-lifecycle-score17-current-risk-review; 865/1179 = 73.37%; 9 unit/world/airunit lifecycle score17 current-risk rows; current focused candidates: 1154; live regenerated current focused candidates: 1154; remaining active focused work: 314; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=9 skipped=0; comment_only_updated=9; tags_added=132; final dry updated=0 skipped=9; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CUnit__VFunc08_InitAndAddToWorld; CUnit__VFunc18_SyncOldVectorAndClampHeight; CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk; CWorld__RemoveUnitFromOccupancyGrid_Thunk; CGroundAttackAircraft__Destructor_VFunc01; CDropship__Destructor_VFunc01; CPlane__Destructor_VFunc01; CDiveBomber__Destructor_VFunc01; CFenrir__Destructor_VFunc01; 0 / 0 / 0; 6411/6411 = 100.00%; 26 xref rows; 177 instruction rows; 9 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-193734_post_wave1194_unit_world_airunit_lifecycle_score17_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
