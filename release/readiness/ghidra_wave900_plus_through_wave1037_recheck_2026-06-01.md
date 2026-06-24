# Ghidra Wave900+ Through Wave1037 Recheck

Status: validation passed
Date: 2026-06-01
Scope: `wave900-plus-through-wave1037-recheck`

This note extends the Wave900+ static re-audit recheck through Wave1037. It validates the Wave1037 focused probe/readiness/evidence/backup extension plus the prior Wave900-Wave1036 gate and current live queue closure at `6238/6238 = 100.00%`.

Command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1037-recheck
```

Verified coverage:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1037 focused probes are rerun directly by `tools/ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1037 --check`; the gate reported `Status: PASS`, `140` readiness notes, `138` covered waves, `136` package probe scripts, `136` evidence bases, `138` backup references, `40` apply scripts, and current live queue closure at `6238/6238 = 100.00%`.
- Wave910 and Wave911 remain queue/planning records rather than saved mutation/review records with per-wave backup notes.
- Wave1037 readiness/evidence anchor: `feature-value-apply-strip-review-wave1037`, `0x0043bb30 CFeatureScalar18__ApplyToFeatureByName`, `0x0043bc80 CFeatureFlag10__ApplyToFeatureByName`, `0x0043c010 CFeatureTexture__ApplyToFeatureByName`, `DAT_00855404`, `692/1408 = 49.15%`, `921/1493 = 61.69%`, `500/500 = 100.00%`, `G:\GhidraBackups\BEA_20260601-072938_post_wave1037_feature_value_apply_strip_review_verified`, no mutation.

Boundary:

This is structural static evidence validation. It does not prove runtime PhysicsScript loading/application behavior, runtime feature behavior, mission-script outcomes, exact source-body identity, concrete feature layouts beyond observed offsets, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1037; wave900-plus-through-wave1037-recheck; feature-value-apply-strip-review-wave1037; 0x0043bb30 CFeatureScalar18__ApplyToFeatureByName; 0x0043bc80 CFeatureFlag10__ApplyToFeatureByName; 0x0043c010 CFeatureTexture__ApplyToFeatureByName; 692/1408 = 49.15%; 921/1493 = 61.69%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-072938_post_wave1037_feature_value_apply_strip_review_verified.
