# Ghidra Wave900+ Through Wave1035 Recheck

Status: validation passed
Date: 2026-06-01
Scope: `wave900-plus-through-wave1035-recheck`

This note extends the Wave900+ static re-audit recheck through Wave1035. It validates the Wave1035 focused probe/readiness/evidence/backup extension plus the prior Wave900-Wave1034 gate and current live queue closure at `6238/6238 = 100.00%`.

Command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1035-recheck
```

Expected coverage:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1035 focused probes are rerun directly by `tools/ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1035 --check`.
- Wave910 and Wave911 remain queue/planning records rather than saved mutation/review records with per-wave backup notes.
- Wave1035 readiness/evidence anchor: `spawner-value-apply-strip-review-wave1035`, `0x0043a170 CSpawnerDelay__ApplyToSpawnerByName`, `0x0043a4d0 CSpawnerRecall__ApplyToSpawnerByName`, `0x0043a7b0 CSpawnerInfinite__ApplyToSpawnerByName`, `DAT_008553f4`, `672/1408 = 47.73%`, `901/1493 = 60.35%`, `500/500 = 100.00%`, `[maintainer-local-ghidra-backup-root]\BEA_20260601-061824_post_wave1035_spawner_value_apply_strip_review_verified`, no mutation.

Boundary:

This is structural static evidence validation. It does not prove runtime PhysicsScript loading/application behavior, runtime spawner behavior, mission-script outcomes, exact source-body identity, concrete spawner layouts beyond observed offsets, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1035; wave900-plus-through-wave1035-recheck; spawner-value-apply-strip-review-wave1035; 0x0043a170 CSpawnerDelay__ApplyToSpawnerByName; 0x0043a4d0 CSpawnerRecall__ApplyToSpawnerByName; 0x0043a7b0 CSpawnerInfinite__ApplyToSpawnerByName; 672/1408 = 47.73%; 901/1493 = 60.35%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-061824_post_wave1035_spawner_value_apply_strip_review_verified.
