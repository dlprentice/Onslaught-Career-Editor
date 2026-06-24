# Ghidra Unit Core Tail Wave526 Readiness

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for CUnit core init, event, cleanup, health, pickup, motion, and linked-effect helpers

## Summary

Wave526 hardened twelve saved Ghidra function records around the CUnit core tail. The pass corrected stale owner labels, removed stale `param_N` signatures, and fixed the `CUnit__Init` and `CUnit__HandleEvent` stack-argument shapes from instruction read-back.

Targets:

- `0x004f84c0` - `CUnit__VFunc01_ScalarDeletingDtor`
- `0x004f86d0` - `CUnit__Init`
- `0x004f9430` - `CUnit__ApplyRandomDestructibleDamageBurst`
- `0x004f9490` - `CUnit__SpawnConfiguredPickupIfAboveWater`
- `0x004f95d0` - `CUnit__VFunc02_CleanupWorldLinksAndForward`
- `0x004f9820` - `CUnit__HandleEvent`
- `0x004f99b0` - `CUnit__PlayRespawnVoiceCueIfAvailable`
- `0x004f99f0` - `CUnit__GetCurrentHealthOrSubtreeHealth`
- `0x004f9a40` - `CUnit__GetRootSubtreeHealthIfAnyActive`
- `0x004f9a60` - `CUnit__RemoveLinkedObjectFromSpawnerSet`
- `0x004fa800` - `CUnit__UpdateClosingAndUnshuttingState`
- `0x004fa8d0` - `CUnit__UpdateMotionAttachmentsAndEffects`

## Evidence

Read-back artifacts live under `subagents/ghidra-static-reaudit/wave526-unit-core-tail-004f84c0/`.

Verified exports:

- 12 target metadata rows
- 12 target tag rows
- 120 target xref rows
- 5052 instruction rows
- 3601 focused `CUnit__Init` instruction rows
- 12 target decompile exports

Final apply evidence:

- Dry run: `updated=0 skipped=12 renamed=0 would_rename=8 missing=0 bad=0`
- Apply: `updated=12 skipped=0 renamed=8 would_rename=0 missing=0 bad=0`
- Verify dry run: `updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0`
- Save status: `REPORT: Save succeeded`
- Focused probe: `py -3 tools\ghidra_unit_core_tail_wave526_probe.py`
- NPM probe: `npm run test:ghidra-unit-core-tail-wave526`

## Queue Impact

Fresh queue after Wave526:

- Function objects: 6082
- Functions with comments: 2519
- Commentless functions: 3563
- Exact `undefined` signatures: 1593
- Signatures still using `param_N` names: 1344
- Comment-backed telemetry: `2519/6082 = 41.42%`
- Strict clean-signature telemetry: `2465/6082 = 40.53%`

These are queue telemetry only, not certification and not a milestone.

## Backup

Verified backup:

- Path: `G:\GhidraBackups\BEA_20260518-015634_post_wave526_unit_core_tail_verified`
- Files: 19
- Bytes: 158862215
- MissingCount: 0
- ExtraCount: 0
- HashDiffCount: 0

## Boundaries

This wave proves saved static retail Ghidra evidence only. Runtime init behavior, runtime event behavior, runtime pickup behavior, runtime cleanup behavior, runtime health/HUD behavior, runtime motion/effect behavior, exact source-body identity, concrete CUnit/init/profile/active-reader/effect layouts, exact enum names, BEA patching, and rebuild parity remain unproven.
