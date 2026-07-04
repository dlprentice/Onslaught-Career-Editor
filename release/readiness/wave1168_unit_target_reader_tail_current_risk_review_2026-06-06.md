# Wave1168 Unit Target-Reader Tail Current-Risk Review

Status: complete static read-only evidence pending validation
Date: 2026-06-06
Tag: `wave1168-unit-target-reader-tail-current-risk-review`

Wave1168 re-read twelve active Wave1108 focused rows in the CUnit / CSquadNormal / SharedUnitAI target-reader and linked-target gate tail. The saved comments, signatures, names, and tags remain coherent with prior Wave523, Wave540, Wave837, Wave838, and Wave1082 evidence. The wave is a read-only review with no mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004fb3d0 CSquadNormal__IsValidLinkedSupportForTarget` | Calls from squad/AI targeting rows including `CSquadNormal__SelectBestEngagementTarget` and SharedUnitAI helpers; validates support target masks and terrain-relative height gates. |
| `0x004fb650 CUnit__ForwardAimTransformAndAttachTargetReader` | Calls from `CGillMHeadAI__UpdateAimTransformAndTargetReader`, `CWarspite__Update`, and `CInfantryAI__UpdateSupportSelection_0048a030`; forwards aim transform and target reader to `OID__UpdateAimTransformAndAttachTargetReader`. |
| `0x004fc3a0 CUnit__SetSpawnCooldownState3` | Adjacent CUnit tail accounting row, not target-reader behavior; called from `CSpawnerThng__ProcessSpawnWave`, writes state literal 3 and an absolute cooldown/ready-time value. |
| `0x004fce40` / `0x004fce80` / `0x004fcec0` | CUnit attached-node forwarders for vfunc slots `+0x14`, `+0x18`, and `+0x1c`, with CInfantryAI, CSquadNormal, and CUnitAI door-wing call context. |
| `0x004fd5e0 CUnit__VFunc26_GetRecentSegmentDamageMeter` | DATA-backed by many CUnit-family vtables and called from the HiveBoss vfunc context; returns a bounded recent damage meter. |
| `0x004fd6a0` / `0x004fd700` | CUnit activation/deactivation linked-target/child-reader helpers, DATA-backed by many CUnit-family vtables. |
| `0x004fea30`, `0x004feac0`, `0x004ffbb0` | SharedUnitAI/CInfantryAI vtable-boundary target-state, range-candidate, and target-reader gate rows. |

Read-back evidence:

- Fresh exports: `12` metadata rows, `12` tag rows, `191` xref rows, `618` instruction rows, and `12` decompile rows.
- Logs report `targets=12 found=12 missing=0`, `rows=12 missing=0`, `Wrote 191 rows`, `targets=12 missing=0`, and `targets=12 dumped=12 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-052300_post_wave1168_unit_target_reader_tail_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Accounting after Wave1168: `648/1179 = 54.96%`, remaining active focused work: 531, current risk candidates: 6166, current focused candidates: 1178, live regenerated current focused candidates: 1178, focused threshold `15`, not Wave911 reconstruction.
- Static quality remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt.
- Codex read-only consult used; no Cursor/Composer used.
- Probe token anchor: Wave1168; wave1168-unit-target-reader-tail-current-risk-review; 648/1179 = 54.96%; 12 CUnit / CSquadNormal / SharedUnitAI target-reader tail current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 531; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 191 xref rows; 618 instruction rows; CSquadNormal__IsValidLinkedSupportForTarget; CUnit__ForwardAimTransformAndAttachTargetReader; CUnit__SetSpawnCooldownState3; CUnit__ForwardAttachedNodeVFunc14IfPresent; CUnit__VFunc22_ActivateLinkedTargetsAndChildren; SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0; CSpawnerThng__ProcessSpawnWave; OID__UpdateAimTransformAndAttachTargetReader; [maintainer-local-ghidra-backup-root]\BEA_20260606-052300_post_wave1168_unit_target_reader_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

What this proves:

- The twelve target function rows exist in the saved Ghidra project.
- The saved comments/signatures/tags remain coherent with prior CUnit, CSquadNormal, and SharedUnitAI static evidence.
- The cluster bridges support-target selection, aim-transform/target-reader forwarding, attached-node forwarding, linked-target activation/deactivation, and AI-side target-reader gates.

What remains unproven:

- Runtime targeting behavior.
- Runtime squad AI behavior.
- Runtime attached-node behavior.
- Exact CUnit/CSquadNormal/CUnitAI/SharedUnitAI concrete layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA, gameplay outcomes, and rebuild parity.
