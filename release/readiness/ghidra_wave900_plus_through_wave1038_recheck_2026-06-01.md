# Ghidra Wave900+ Through Wave1038 Recheck

Status: validation passed
Date: 2026-06-01
Scope: `wave900-plus-through-wave1038-recheck`

This note extends the Wave900+ static re-audit recheck through Wave1038. It validates the Wave1038 focused probe/readiness/evidence/backup extension plus the prior Wave900-Wave1037 gate and current live queue closure at `6238/6238 = 100.00%`.

Command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1038-recheck
```

Expected coverage:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1038 focused probes are rerun directly by `tools/ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1038 --check`.
- Wave910 and Wave911 remain queue/planning records rather than saved mutation/review records with per-wave backup notes.
- Wave1038 readiness/evidence anchor: `hazard-value-apply-strip-review-wave1038`, `0x0043c1a0 CHazardScalar14__ApplyToHazardByName`, `0x0043c280 CHazardScalar18__ApplyToHazardByName`, `0x0043c320 CHazardNoise__ApplyToHazardByName`, `0x0043c410 CHazardEffect__ApplyToHazardByName`, `DAT_00855408`, `696/1408 = 49.43%`, `925/1493 = 61.96%`, `500/500 = 100.00%`, `[maintainer-local-ghidra-backup-root]\BEA_20260601-072720_post_wave1038_hazard_value_apply_strip_review_verified`, no mutation.

Validation result:

- `npm run test:ghidra-wave900-plus-through-wave1038-recheck`: PASS.
- Readiness notes: `141`.
- Covered waves: `139`.
- Package probe scripts: `137`.
- Evidence bases: `137`.
- Backup references: `139`.
- Apply scripts: `40`.
- Wave982-Wave1038 direct probes: result count `57`, pass count `1`, fail count `56`, disallowed failure count `0`.
- Current queue: `6238` total, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status `PASS`.

Boundary:

This is structural static evidence validation. It does not prove runtime PhysicsScript loading/application behavior, runtime hazard behavior, mission-script outcomes, exact source-body identity, concrete hazard layouts beyond observed offsets, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1038; wave900-plus-through-wave1038-recheck; hazard-value-apply-strip-review-wave1038; 0x0043c1a0 CHazardScalar14__ApplyToHazardByName; 0x0043c280 CHazardScalar18__ApplyToHazardByName; 0x0043c320 CHazardNoise__ApplyToHazardByName; 0x0043c410 CHazardEffect__ApplyToHazardByName; 696/1408 = 49.43%; 925/1493 = 61.96%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-072720_post_wave1038_hazard_value_apply_strip_review_verified.
