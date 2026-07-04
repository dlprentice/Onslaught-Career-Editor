# Ghidra Wave900+ Through Wave1020 Recheck

Status: complete local validation
Date: 2026-05-31

This gate extends the Wave900+ structural static re-audit evidence sweep through Wave1020 (`projectile-burst-spawn-spine-review-wave1020`).

Validation:

- `npm run test:ghidra-projectile-burst-spawn-spine-review-wave1020`
- `npm run test:ghidra-wave900-plus-through-wave1020-recheck`
- Wave900-Wave1020 aggregate recheck PASS: 123 readiness notes, 121 covered waves, 119 package probe scripts, 119 evidence bases, 121 backup references, 37 apply scripts, and 39 Wave982-Wave1020 direct-probe results with 0 disallowed failures.
- Validation scope before commit: focused Wave1020 probe, Wave900-Wave1020 aggregate recheck, static re-audit queue probe, docsync, release profile check, curated manifest check, public allowlist, doc-commands, md-links, repo hygiene, tracked JSON/JSONL parse, `git diff --check`, and `git diff --cached --check`.
- Current queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Wave1020 adds a focused read-only projectile-burst spawn spine review with verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260531-214433_post_wave1020_projectile_burst_spawn_spine_review_verified`.

This is structural static evidence validation only. Runtime stealth behavior, `weapon_fire_breaks_stealth`, runtime projectile behavior, exact layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Probe token anchor: Wave1020; projectile-burst-spawn-spine-review-wave1020; 0x005069f0 ProjectileBurst__SpawnFromCurrentPreset; 0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback; 0x00506930 CWeapon__HandleFireBurstEvent; 0x004d9f30 CRound__UpdateEffectTransformByMode_004d9f30; 0x004df530 CShell__CopyResourceNameToInlineBuffer; 528/1408 = 37.50%; 757/1493 = 50.70%; 456/500 = 91.20%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-214433_post_wave1020_projectile_burst_spawn_spine_review_verified; no mutation.
