# Ghidra Wave900 Through Wave1072 Recheck Readiness Note

Status: complete local validation evidence
Date: 2026-06-02
Scope: `wave900-plus-through-wave1072-recheck`

This note extends the rolling Wave900+ recheck gate through Wave1072 after the read-only `oid-target-profile-ballistic-review-wave1072` pass. It keeps the prior Wave900+ notes as historical evidence and adds the current Wave1072 readiness/probe/backup anchors to the live aggregate gate.

Current anchors:

- Latest operational wave: Wave1072, `oid-target-profile-ballistic-review-wave1072`.
- Latest focused probe: `tools/ghidra_oid_target_profile_ballistic_review_wave1072_probe.py`.
- Latest readiness note: `release/readiness/ghidra_oid_target_profile_ballistic_review_wave1072_2026-06-02.md`.
- Latest verified backup: `G:\GhidraBackups\BEA_20260602-035902_post_wave1072_oid_target_profile_ballistic_review_verified`.

Current percentages:

- Static export-contract function-quality closure: `6246/6246 = 100.00%`.
- Wave911 focused re-audit progress: `812/1408 = 57.67%`.
- Expanded static surface progress: `1334/1560 = 85.51%`.
- Wave911 top-500 risk-ranked coverage: `500/500 = 100.00%`.

Representative Wave1072 anchors:

- `0x00507ab0 OID__CanFireAtTarget_BallisticArcA`
- `0x005088b0 OID__CanFireAtTarget_BallisticArcB`
- `0x00509140 OID__UpdateAimTransformAndAttachTargetReader`
- `0x005094b0 OID__SolveBallisticPitchToTarget`
- `0x005096a0 CUnit__ComputeMinBallisticTravelDistance`
- `0x005099a0 CUnit__ComputeMaxBallisticTravelDistance`
- `0x00509c80 CBattleEngine__ComputeProjectileMetricFromTargetProfile`
- `0x00509e40 TargetSet__GetEntryByIndex`
- `0x00509e90 ProjectileBurst__ResolvePresetByPercentBucketFallback`
- `0x00509f70 TargetProfileContext__IsEligibleByDistanceBucketOrRange`
- `0x0050a080 TargetProfileContext__CanProceedByTargetRangeGate`
- `0x0050a0b0 CSquadNormal__HasActiveMaskMatchWithTarget`
- `0x0050a0d0 CUnit__HasMaskBitsA8`
- `0x0050a0e0 OID__ComputeForwardProjectedPointTowardTarget`
- `0x0050a290 CUnit__IsTargetTimeoutBeforeProfileLimit`

Validation expectation:

- The aggregate package script is `test:ghidra-wave900-plus-through-wave1072-recheck`.
- The focused Wave1072 probe validates the primary/context exports, docs, ledgers, package scripts, queue closure, and backup summary.

Latest aggregate run:

- `npm run test:ghidra-wave900-plus-through-wave1072-recheck`: PASS.
- Readiness notes: `175`.
- Covered waves: `173`.
- Package probe scripts: `171`.
- Evidence bases: `171`.
- Backup references: `173`.
- Apply scripts: `53`.
- Wave982-Wave1072 direct-probe summary: `resultCount=91`, `passCount=1`, `failCount=90`, `disallowedFailureCount=0`.
- Current queue: `totalFunctions=6246`, `commentlessFunctionCount=0`, `undefinedSignatureCount=0`, `paramSignatureCount=0`, `status=PASS`.

Boundary note: this aggregate gate proves local static evidence coverage, backup references, probe/doc wiring, and zero export-contract function-quality debt after validation. It does not prove runtime targeting/projectile/weapon behavior, exact OID/Unit/BattleEngine/CWeapon/CSquadNormal/target-profile/projectile-burst layouts, exact source-body identity, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1072; oid-target-profile-ballistic-review-wave1072; 0x00507ab0 OID__CanFireAtTarget_BallisticArcA; 0x00509c80 CBattleEngine__ComputeProjectileMetricFromTargetProfile; 0x00509e90 ProjectileBurst__ResolvePresetByPercentBucketFallback; 0x00509f70 TargetProfileContext__IsEligibleByDistanceBucketOrRange; 0x0050a0e0 OID__ComputeForwardProjectedPointTowardTarget; 812/1408 = 57.67%; 1334/1560 = 85.51%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260602-035902_post_wave1072_oid_target_profile_ballistic_review_verified; read-only review.
