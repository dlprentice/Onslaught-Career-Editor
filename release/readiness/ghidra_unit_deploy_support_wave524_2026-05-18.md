# Ghidra Unit Deploy Support Wave524 Readiness

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for Unit/Squad support range, deploy, spawn, component-effect, and emitter-transform helpers

## Summary

Wave524 hardened eleven saved Ghidra function records around Unit/Squad support selection, deploy/spawn state helpers, recursive component effects, and emitter transform slot lookup. The pass corrected stale `CUnit__UpdateTransform` documentation: this address is an emitter-transform/cache helper, not a general movement or terrain integration routine.

Targets:

- `0x004fb780` - `CSquadNormal__GetSupportMinEngageDistance`
- `0x004fb7e0` - `CSquadNormal__GetSupportMaxEngageDistance`
- `0x004fb840` - `CSquadNormal__SelectBestSupportOrEscort`
- `0x004fbc90` - `CWarspite__GetMountedUnitPitchOrZero`
- `0x004fbcb0` - `CUnit__UpdateDeployStateAndChargeEffects`
- `0x004fc000` - `CUnit__CanDeployNow`
- `0x004fc080` - `CUnitAI__TrySpawnOrFinalizeAttachedUnit`
- `0x004fc170` - `CUnitAI__FinalizeSpawnAndAdvanceState`
- `0x004fc220` - `CUnit__SpawnComponentEffectsRecursive`
- `0x004fc4e0` - `CUnit__UpdateTransform`
- `0x004fc6e0` - `CUnit__FindEmitterIndexBySlotTag`

## Evidence

Read-back artifacts live under `subagents/ghidra-static-reaudit/wave524-unit-deploy-support-004fb780/`.

Verified exports:

- 11 target metadata rows
- 11 target tag rows
- 203 target xref rows
- 2651 instruction rows
- 11 target decompile exports
- 12 context metadata rows
- 12 context decompile exports

Final apply evidence:

- Initial apply: stopped after the first target because read-back compared generic pointer display text too strictly; Ghidra still reported `REPORT: Save succeeded` for that partial mutation.
- Pointer-type read-back fix: rerun apply reported `updated=11 skipped=0 missing=0 bad=0`.
- Instruction read-back correction: `CSquadNormal__SelectBestSupportOrEscort` was corrected from a two-explicit-argument signature to `void __thiscall CSquadNormal__SelectBestSupportOrEscort(void * this, void * target_unit)` because the tail instruction is `RET 0x4`, not `RET 0x8`.
- Final correction dry run: `updated=0 skipped=11 missing=0 bad=0`
- Final correction apply: `updated=1 skipped=10 missing=0 bad=0`
- Final verify dry run: `updated=0 skipped=11 missing=0 bad=0`
- Save status: `REPORT: Save succeeded`
- Focused probe: `py -3 tools\ghidra_unit_deploy_support_wave524_probe.py`
- NPM probe: `npm run test:ghidra-unit-deploy-support-wave524`

## Queue Impact

Fresh queue after Wave524:

- Function objects: 6082
- Functions with comments: 2494
- Commentless functions: 3588
- Exact `undefined` signatures: 1593
- Signatures still using `param_N` names: 1368
- Comment-backed telemetry: `2494/6082 = 41.01%`
- Strict clean-signature telemetry: `2440/6082 = 40.12%`

These are queue telemetry only, not certification and not a milestone.

## Backup

Verified backup:

- Path: `G:\GhidraBackups\BEA_20260518-005140_post_wave524_unit_deploy_support_corrected_verified`
- Files: 19
- Bytes: 158829447
- MissingCount: 0
- ExtraCount: 0
- HashDiffCount: 0

## Boundaries

This wave proves saved static retail Ghidra evidence only. Runtime deploy behavior, runtime squad AI behavior, runtime particle/effect behavior, exact source-body identity, concrete Unit/Squad/UnitAI/Warspite/profile/cache layouts, exact enum names, BEA patching, and rebuild parity remain unproven.
