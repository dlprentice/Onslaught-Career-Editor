# Unit Targeting / Active-Reader Proof Plan Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x0044e640` → `CFenrirMainGunAI__ScanListsAndSelectSupportTarget` (was `CSquadNormalReader__ScanListsAndSelectSupportTarget_0044e640`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: proof plan complete, not runtime proof
Date: 2026-06-08
Scope: `unit-targeting-active-reader-proof-plan`

This readiness note records a public-safe static-to-proof planning slice for Unit/BattleEngine targeting and active-reader behavior. It is not a new static re-audit wave, not a runtime test, not a screenshot/capture proof, not a BEA patch, not a Godot slice, and not a rebuild parity claim.

Primary static contract source: `unit-battleengine-gameplay-static-contract.md`. The plan records copied-profile guardrails, candidate-list/reader layout unknowns, and stop conditions before any runtime/proof work can start.

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.

Static source evidence:

- Wave1215 (`wave1215-unit-targeting-combat-residual-current-risk-review`): `5` primary targeting rows, `6` xref rows, `794` instruction rows, `5` decompile rows, `425` context xref rows, `1123` context instruction rows, `15` context decompile rows, and `1` data-slot xref row. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-090802_post_wave1215_unit_targeting_combat_residual_current_risk_review_verified`.
- Wave927 (`cunit-active-reader-targeting-review-wave927`): `5` active-reader targeting rows, `23` xref rows, `464` instruction rows, and `5` decompile rows, plus `CUnit__ForwardAimTransformAndAttachTargetReader` context. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified`.

Representative anchors:

| Surface | Static anchor |
| --- | --- |
| Air-guide acquisition | `0x004027c0 CAirGuide__AcquireNearestTargetReader` |
| Dive-bomber target output | `0x00445070 CDiveBomber__SelectTarget` |
| Component targeting boundary | `0x0044e640 ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640` |
| Normal-squad target scoring | `0x00477cb0 CSquadNormal__SelectBestEngagementTarget` |
| Relaxed-squad iterator snapshot | `0x004ea8d0 CRelaxedSquad__CreateIterator` |
| Active-reader assignment | `0x00428b50 CUnit__SetReaderAndComputeRelativeYaw` |
| Heading readback | `0x00428bc0 CUnitAI__GetTargetHeadingWithOffset` |
| Heading update/clamp | `0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped` |
| Formation reader swap | `0x004e97e0 CGenericActiveReader__SwapWithCandidateIfFormationCloser` |
| Side/team compatibility | `0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting` |
| Aim/reader forwarder | `0x004fb650 CUnit__ForwardAimTransformAndAttachTargetReader` |

Proof-plan boundaries:

- The plan is limited to target acquisition, candidate filtering/scoring, active-reader assignment, heading update, and iterator snapshot behavior.
- copied-profile guardrails apply to any later runtime/proof execution.
- Any later proof must use copied profiles or app-owned artifact roots.
- Any later proof must use one selected unit/squad/state target and stop on ambiguous identity, non-reproducible target state, private artifact leakage, unexpected file mutation, or any need to touch the installed game.
- The plan explicitly does not include weapon fire, projectile, damage, collision, morph/mode switching, cloak/stealth, broad squad AI, broad Unit/BattleEngine runtime proof, visual QA, patching behavior, rebuild parity, or no-noticeable-difference parity.

No runtime targeting behavior, runtime squad AI behavior, runtime component behavior, runtime active-reader lifetime/ownership behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, rebuild parity, or no-noticeable-difference parity claim is made.
