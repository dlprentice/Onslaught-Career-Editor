# Ghidra Unit Faction / Spawn Wave527 Readiness

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for CUnit faction propagation, child-reader lookup, target propagation, support-spawn, spawn accounting, and engagement-mode helpers

## Summary

Wave527 hardened eight saved Ghidra function records around the CUnit faction/spawn tail. The pass removed stale register-carryover parameters, corrected two owner labels, and added bounded comments/tags for hierarchy propagation and support-spawn behavior.

Targets:

- `0x004fd830` - `CUnit__SetFactionForHierarchy`
- `0x004fd8d0` - `CUnit__FindChildReaderByField270`
- `0x004fd910` - `CUnit__FindNearestFactionAnchor`
- `0x004fda10` - `CUnit__GetProfileState120`
- `0x004fda20` - `CUnit__PropagateTargetUnitToHierarchy`
- `0x004fdad0` - `CUnit__TrySpawnMembersForTarget`
- `0x004fdc20` - `CUnit__UpdateSpawnCountAccounting`
- `0x004fdcb0` - `CUnit__SetEngagementModeAndMaybeClearTargetReader`

## Evidence

Read-back artifacts live under `subagents/ghidra-static-reaudit/wave527-unit-faction-spawn-004fd830/`.

Verified exports:

- 8 target metadata rows
- 8 target tag rows
- 85 target xref rows
- 3368 instruction rows
- 8 target decompile exports
- 7 context decompile exports

Final apply evidence:

- Dry run: `updated=0 skipped=8 renamed=0 would_rename=2 missing=0 bad=0`
- Apply: `updated=8 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`
- Verify dry run: `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`
- Save status: `REPORT: Save succeeded`
- Focused probe: `py -3 tools\ghidra_unit_faction_spawn_wave527_probe.py`
- NPM probe: `npm run test:ghidra-unit-faction-spawn-wave527`

## Queue Impact

Fresh queue after Wave527:

- Function objects: 6082
- Functions with comments: 2527
- Commentless functions: 3555
- Exact `undefined` signatures: 1593
- Signatures still using `param_N` names: 1336
- Comment-backed telemetry: `2527/6082 = 41.55%`
- Strict clean-signature telemetry: `2473/6082 = 40.66%`

These are queue telemetry only, not certification and not a milestone.

## Backup

Verified backup:

- Path: `[maintainer-local-ghidra-backup-root]\BEA_20260518-022151_post_wave527_unit_faction_spawn_verified`
- Files: 19
- Bytes: 158927751
- MissingCount: 0
- ExtraCount: 0
- HashDiffCount: 0

## Boundaries

This wave proves saved static retail Ghidra evidence only. Runtime spawn behavior, runtime AI behavior, runtime faction behavior, runtime target propagation, runtime engagement-mode behavior, exact source-body identity, concrete CUnit/profile/child-reader/spawner layouts, exact enum names, BEA patching, and rebuild parity remain unproven.
