# Ghidra Wave900+ Through Wave1036 Recheck

Status: validation passed
Date: 2026-06-01
Scope: `wave900-plus-through-wave1036-recheck`

This note extends the Wave900+ static re-audit recheck through Wave1036. It validates the Wave1036 focused probe/readiness/evidence/backup extension plus the prior Wave900-Wave1035 gate and current live queue closure at `6238/6238 = 100.00%`.

Command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1036-recheck
```

Verified coverage:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1036 focused probes are rerun directly by `tools/ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1036 --check`; the gate reported `Status: PASS`, `139` readiness notes, `137` covered waves, `135` package probe scripts, `135` evidence bases, `137` backup references, `40` apply scripts, and current live queue closure at `6238/6238 = 100.00%`.
- Wave910 and Wave911 remain queue/planning records rather than saved mutation/review records with per-wave backup notes.
- Wave1036 readiness/evidence anchor: `explosion-value-apply-strip-review-wave1036`, `0x0043afc0 CExplosionAirEffect__ApplyToExplosionByName`, `0x0043b3a0 CExplosionScalar34__ApplyToExplosionByName`, `0x0043b880 CExplosionWaterSound__ApplyToExplosionByName`, `DAT_008553f8`, `685/1408 = 48.65%`, `914/1493 = 61.22%`, `500/500 = 100.00%`, `G:\GhidraBackups\BEA_20260601-064537_post_wave1036_explosion_value_apply_strip_review_verified`, no mutation.

Boundary:

This is structural static evidence validation. It does not prove runtime PhysicsScript loading/application behavior, runtime explosion behavior, mission-script outcomes, exact source-body identity, concrete explosion layouts beyond observed offsets, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1036; wave900-plus-through-wave1036-recheck; explosion-value-apply-strip-review-wave1036; 0x0043afc0 CExplosionAirEffect__ApplyToExplosionByName; 0x0043b3a0 CExplosionScalar34__ApplyToExplosionByName; 0x0043b880 CExplosionWaterSound__ApplyToExplosionByName; 685/1408 = 48.65%; 914/1493 = 61.22%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-064537_post_wave1036_explosion_value_apply_strip_review_verified.
