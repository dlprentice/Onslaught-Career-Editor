# Ghidra Wave900-Wave1000 Recheck Readiness Note

Status: passed structural static evidence recheck
Date: 2026-05-31
Scope: `Wave900-Wave1000`

This gate extends the operator-requested Wave900+ recheck through Wave1000 after the `gillm-grounded-movement-review-wave1000` read-only review was prepared. It is a structural static-evidence validation pass, not runtime proof, exact source-layout proof, or rebuild parity.

Command:

```powershell
cmd.exe /c npm run test:ghidra-wave900-plus-through-wave1000-recheck
```

Validated result:

- Status: `PASS`
- Readiness notes: `103`
- Covered waves: `101`
- Package probe scripts: `99`
- Evidence bases: `99`
- Backup references: `101`
- Apply scripts: `30`
- Direct Wave982-Wave1000 probes: `19` results, `1` pass, `18` classified current-state/rolled-doc drift failures, `0` disallowed evidence/unclassified failures.
- Current queue closure: `6222` total functions, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status `PASS`.

Wave1000 anchor:

- `gillm-grounded-movement-review-wave1000`
- `0x004799c0 CGillM__VFunc09_InitGroundedSpawnState`
- `0x00479d10 CGillM__UpdateGroundedVerticalDrift`
- `0x00479db0 CGillM__TriggerRandomArmHitAnimationIfReady`
- `0x00479f30 CGillM__ComputeTerrainClearanceNoiseScale`
- `0x0047a0b0 CGillM__ComputeLateralSlopeAlignment`
- `0x0047a160 CGillM__StartState1WithStoredMotionVector`
- Wave911 focused re-audit progress: `467/1408 = 33.17%`
- Expanded static surface progress: `606/1478 = 41.00%`
- Wave911 top-500 risk-ranked coverage: `350/500 = 70.00%`
- Static closure: `6222/6222 = 100.00%`
- Verified backup: `G:\GhidraBackups\BEA_20260531-101059_post_wave1000_gillm_grounded_movement_review_verified`

Interpretation:

- Wave900-Wave981 remain covered by the prior line-classified focused-probe sweep and second-level evidence audit.
- Wave982-Wave1000 focused probes are rerun directly by this gate; stale current-state baton and rolled-current-doc failures are classified separately from evidence mismatches.
- Wave910 and Wave911 remain queue/planning records, not saved Ghidra mutation/review records with per-wave backup notes.
- Wave1000 is a read-only risk-ranked residual review; no Ghidra mutation was needed.
- This recheck validates readiness/evidence structure, backup presence, apply-log cleanliness where applicable, focused-probe classifications, and current queue closure.

Boundary:

- Runtime GillM movement behavior remains unproven.
- Runtime terrain/grounding behavior remains unproven.
- Runtime arm-hit animation behavior remains unproven.
- Exact source-body identity remains unproven.
- Concrete CGillM/CMCGillM/CGillMAI/TerrainGuide layouts remain unproven.
- BEA patching behavior remains unproven.
- Rebuild parity remains unproven.
