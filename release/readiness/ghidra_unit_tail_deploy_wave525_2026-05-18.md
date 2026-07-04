# Ghidra Unit Tail Deploy Wave525 Readiness

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for Unit/UnitAI tail deploy, child/spawner cleanup, destroyed-state cleanup, grid-map query, and deploy/fire animation helpers

## Summary

Wave525 hardened thirteen saved Ghidra function records around the Unit tail deploy/cleanup cluster immediately after the Wave524 support/deploy tranche. The pass removed stale `param_N` signatures, added comments and tags, and narrowed several helpers to register-this or one-stack-argument signatures.

Targets:

- `0x004fcdc0` - `CUnit__SetCollisionAndDamageFlags`
- `0x004fcf00` - `CUnit__ResetKinematicsAndNotifyController`
- `0x004fcfa0` - `CUnit__ClearSpawnerSet`
- `0x004fcfe0` - `CUnit__ReleaseChildUnits`
- `0x004fd040` - `CUnit__ResetDeploymentGraphAndScheduleEvent`
- `0x004fd140` - `CUnit__MarkDestroyedAndCleanupLinks`
- `0x004fd380` - `CUnit__GetGridMapByType`
- `0x004fd5b0` - `CUnit__IsActiveAndNotInState12`
- `0x004fd7a0` - `CUnit__HasAnyReadySpawner`
- `0x004fd7e0` - `CUnitAI__AreSpawnedChildrenReady`
- `0x004fde10` - `CUnitAI__IsDeployAnimationState`
- `0x004fde30` - `CUnit__BeginDeployAnimationIfIdle`
- `0x004fdeb0` - `CUnitAI__HandleDeployAndFireAnimationCompletion`

## Evidence

Read-back artifacts live under `subagents/ghidra-static-reaudit/wave525-unit-tail-deploy-004fcdc0/`.

Verified exports:

- 13 target metadata rows
- 13 target tag rows
- 116 target xref rows
- 3133 instruction rows
- 13 target decompile exports

Final apply evidence:

- Dry run: `updated=0 skipped=13 missing=0 bad=0`
- Apply: `updated=13 skipped=0 missing=0 bad=0`
- Verify dry run: `updated=0 skipped=13 missing=0 bad=0`
- Save status: `REPORT: Save succeeded`
- Focused probe: `py -3 tools\ghidra_unit_tail_deploy_wave525_probe.py`
- NPM probe: `npm run test:ghidra-unit-tail-deploy-wave525`

## Queue Impact

Fresh queue after Wave525:

- Function objects: 6082
- Functions with comments: 2507
- Commentless functions: 3575
- Exact `undefined` signatures: 1593
- Signatures still using `param_N` names: 1355
- Comment-backed telemetry: `2507/6082 = 41.22%`
- Strict clean-signature telemetry: `2453/6082 = 40.33%`

These are queue telemetry only, not certification and not a milestone.

## Backup

Verified backup:

- Path: `[maintainer-local-ghidra-backup-root]\BEA_20260518-012612_post_wave525_unit_tail_deploy_verified`
- Files: 19
- Bytes: 158862215
- MissingCount: 0
- ExtraCount: 0
- HashDiffCount: 0

## Boundaries

This wave proves saved static retail Ghidra evidence only. Runtime deploy behavior, runtime animation behavior, runtime destruction behavior, runtime collision/grid behavior, exact source-body identity, concrete Unit/UnitAI/profile/active-reader layouts, exact enum names, BEA patching, and rebuild parity remain unproven.
