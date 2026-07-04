# Wave1168 Unit Target-Reader Tail Current-Risk Review

Status: complete static read-only evidence pending validation
Date: 2026-06-06
Tag: `wave1168-unit-target-reader-tail-current-risk-review`

Wave1168 accounts for `12 CUnit / CSquadNormal / SharedUnitAI target-reader tail current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation. Codex read-only consult used; no Cursor/Composer used.

| Address | Static read-back evidence |
| --- | --- |
| `0x004fb3d0 CSquadNormal__IsValidLinkedSupportForTarget` | Support target mask and terrain-relative height gate; xrefs include `CSquadNormal__SelectBestEngagementTarget`, SharedUnitAI update/gate helpers, and `ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640`. |
| `0x004fb650 CUnit__ForwardAimTransformAndAttachTargetReader` | Generic CUnit forwarder to `OID__UpdateAimTransformAndAttachTargetReader`; xrefs include `CGillMHeadAI__UpdateAimTransformAndTargetReader`, `CWarspite__Update`, and `CInfantryAI__UpdateSupportSelection_0048a030`. |
| `0x004fc3a0 CUnit__SetSpawnCooldownState3` | Adjacent CUnit tail accounting row, not target-reader behavior; called from `CSpawnerThng__ProcessSpawnWave` after `CWorldPhysicsManager__CreateThingByType`. |
| `0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent` | Attached-node vfunc `+0x14` forwarder with CInfantryAI and CUnitAI door-wing call context. |
| `0x004fce80 CUnit__ForwardAttachedNodeVFunc18IfPresent` | Attached-node vfunc `+0x18` forwarder with CInfantryAI and unit-family call context. |
| `0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent` | Attached-node vfunc `+0x1c` forwarder with CSquadNormal attack formation and CUnitAI door-wing call context. |
| `0x004fd5e0 CUnit__VFunc26_GetRecentSegmentDamageMeter` | DATA-backed by many CUnit-family vtables; called from HiveBoss vfunc context. |
| `0x004fd6a0 CUnit__VFunc22_ActivateLinkedTargetsAndChildren` | Linked-target/child-reader activation helper, DATA-backed by many CUnit-family vtables. |
| `0x004fd700 CUnit__VFunc23_DeactivateLinkedTargetsAndChildren` | Linked-target/child-reader deactivation helper, DATA-backed by many CUnit-family vtables. |
| `0x004fea30 SharedUnitAI__CheckField24TargetState_004fea30` | SharedUnitAI/CInfantryAI vtable-boundary target-state boolean helper. |
| `0x004feac0 SharedUnitAI__CheckField24RangeAgainstCandidate_004feac0` | SharedUnitAI/CInfantryAI vtable-boundary range/candidate helper. |
| `0x004ffbb0 SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0` | SharedUnitAI/CInfantryAI vtable-boundary target-reader gate helper. |

Evidence counts:

- `12` metadata rows.
- `12` tag rows.
- `191` xref rows.
- `618` instruction rows.
- `12` decompile rows.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-052300_post_wave1168_unit_target_reader_tail_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.

Accounting:

- Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`.
- Wave911 top-500 remains `500/500 = 100.00%`.
- Wave1108 current focused accounting is now `648/1179 = 54.96%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 531.
- Focused threshold `15`.
- Not Wave911 reconstruction.

Boundary:

- `0x004fc3a0 CUnit__SetSpawnCooldownState3` is included as adjacent CUnit tail accounting evidence, not as target-reader behavior.
- Runtime targeting behavior, runtime squad AI behavior, runtime attached-node behavior, exact CUnit/CSquadNormal/CUnitAI/SharedUnitAI concrete layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1168; wave1168-unit-target-reader-tail-current-risk-review; 648/1179 = 54.96%; 12 CUnit / CSquadNormal / SharedUnitAI target-reader tail current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 531; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 191 xref rows; 618 instruction rows; CSquadNormal__IsValidLinkedSupportForTarget; CUnit__ForwardAimTransformAndAttachTargetReader; CUnit__SetSpawnCooldownState3; CUnit__ForwardAttachedNodeVFunc14IfPresent; CUnit__VFunc22_ActivateLinkedTargetsAndChildren; SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0; CSpawnerThng__ProcessSpawnWave; OID__UpdateAimTransformAndAttachTargetReader; [maintainer-local-ghidra-backup-root]\BEA_20260606-052300_post_wave1168_unit_target_reader_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
