# Ghidra Targeting Wave523 Readiness

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for Unit/Squad targeting and ballistic range helpers

## Summary

Wave523 hardened six saved Ghidra function records around Unit/Squad target range checks, ballistic fire gates, support-target checks, and aim-forwarding. The pass corrected one stale owner label from a Warspite-specific name to a generic CUnit forwarding helper and fixed five stale stack-argument shapes.

Targets:

- `0x004fb280` - `CUnit__UpdateFireControlYawAndQueueEvent`
- `0x004fb3d0` - `CSquadNormal__IsValidLinkedSupportForTarget`
- `0x004fb500` - `CUnit__CanFireAtTarget_BallisticArcA`
- `0x004fb5a0` - `CUnit__CanFireAtTarget_BallisticArcB`
- `0x004fb650` - `CUnit__ForwardAimTransformAndAttachTargetReader`
- `0x004fb670` - `CUnit__ClassifyTargetRangeBand`

## Evidence

Read-back artifacts live under `subagents/ghidra-static-reaudit/wave523-unit-targeting-004fb280/`.

Verified exports:

- 6 target metadata rows
- 6 target tag rows
- 46 target xref rows
- 1566 instruction rows
- 6 target decompile exports
- 6 context metadata rows
- 6 context decompile exports

Final apply evidence:

- Dry run: `updated=0 skipped=6 renamed=0 would_rename=1 missing=0 bad=0`
- Apply run: `updated=6 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`
- Verify dry run: `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`
- Save status: `REPORT: Save succeeded`
- Focused probe: `py -3 tools\ghidra_targeting_wave523_probe.py`
- NPM probe: `npm run test:ghidra-targeting-wave523`

## Queue Impact

Fresh queue after Wave523:

- Function objects: 6082
- Functions with comments: 2483
- Commentless functions: 3599
- Exact `undefined` signatures: 1594
- Signatures still using `param_N` names: 1375
- Comment-backed telemetry: `2483/6082 = 40.83%`
- Strict clean-signature telemetry: `2429/6082 = 39.94%`

These are queue telemetry only, not certification and not a milestone.

## Backup

Verified backup:

- Path: `[maintainer-local-ghidra-backup-root]\BEA_20260518-002217_post_wave523_unit_targeting_verified`
- Files: 19
- Bytes: 158763911
- MissingCount: 0
- ExtraCount: 0
- HashDiffCount: 0

## Boundaries

This wave proves saved static retail Ghidra evidence only. Runtime targeting behavior, runtime weapon behavior, runtime squad AI behavior, exact source-body identity, concrete Unit/Squad/OID layouts, exact enum names, BEA patching, and rebuild parity remain unproven.
