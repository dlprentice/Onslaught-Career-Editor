# Wave1215 Unit Targeting Combat Residual Current-Risk Review Readiness Note

Status: complete static current-risk read-only review; validation passed; historical artifact committed
Date: 2026-06-07
Scope: `wave1215-unit-targeting-combat-residual-current-risk-review`

Wave1215 re-read `5 unit-targeting combat residual current-risk rows` with fresh Ghidra export evidence: `CAirGuide__AcquireNearestTargetReader`, `CDiveBomber__SelectTarget`, `ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640`, `CSquadNormal__SelectBestEngagementTarget`, and `CRelaxedSquad__CreateIterator`.

Evidence:

- Fresh Ghidra export: `6 xref rows`, `794 instruction rows`, and `5 decompile rows`.
- Context export: `425 context xref rows`, `1123 context instruction rows`, and `15 context decompile rows`.
- Data-slot export: `1 data-slot xref row` confirming `0x005d96ac` is a non-function slot for the owner-deferred component-targeting boundary.
- Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`.
- Active current-risk progress uses unique-address accounting and is `1138/1179 = 96.52%`; remaining active focused work: 41.
- legacy additive counter is deprecated (`1169/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.
- current risk candidates: 6166; current focused candidates: 1127; live regenerated current focused candidates: 1127.
- Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; this is not Wave911 reconstruction.
- current-risk denominator, continuity denominator, focused threshold `15`, and `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence` remain the active measured lane.
- Codex read-only consults used; no Cursor/Composer.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-090802_post_wave1215_unit_targeting_combat_residual_current_risk_review_verified`.

Mutation status: read-only review; no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Accounting paths: `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `unit-battleengine-gameplay-static-contract.md`, and `wave1108-current-risk-rank`.

Boundary: this is static Ghidra evidence for rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime targeting behavior, runtime squad AI behavior, runtime component behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
