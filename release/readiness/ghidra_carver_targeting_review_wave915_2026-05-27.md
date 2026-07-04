# Ghidra Wave915 Carver targeting review (2026-05-27)

Status: read-only static review
Date: 2026-05-27
Branch: `main`
Tag: `carver-targeting-review-wave915`

## Scope

Wave915 reviewed six Carver AI/guide targeting helpers from the Wave911 focused correction queue:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00422db0` | `CCarverAI__CheckNearbyEnemies` | Reviewed; no mutation |
| `0x00423510` | `CCarverGuide__AcquireNearestTargetReader` | Reviewed; no mutation |
| `0x00422970` | `CCarverAI__CanStartAttack` | Reviewed; no mutation |
| `0x00422aa0` | `CCarverAI__RefreshTargetReaderAndScheduleMove` | Reviewed; no mutation |
| `0x00422b90` | `CCarverAI__UpdateAttackAndReschedule` | Reviewed; no mutation |
| `0x00423490` | `CCarverGuide__HandleEvent` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave915-carver-targeting-review/metadata.tsv
subagents/ghidra-static-reaudit/wave915-carver-targeting-review/tags.tsv
subagents/ghidra-static-reaudit/wave915-carver-targeting-review/instructions.tsv
subagents/ghidra-static-reaudit/wave915-carver-targeting-review/decompile/
```

Read-back result:

```text
metadata: 6/6 OK
tags: 6/6 OK (no saved tags on these six)
instructions: 510 rows
decompile: 6/6 OK
```

## Review Result

No tracked `Carver.cpp` source body exists in `references/Onslaught/`; the repo has debug-path and retail decompile evidence only. The saved names/signatures/comments remain appropriate for the current evidence, so no Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260527-103639_post_wave915_carver_targeting_review_verified
files=19
bytes=173247367
```

## Truth boundary

This review confirms static Ghidra coherence for selected Carver targeting helpers. It does not prove runtime AI/weapon behavior, concrete Carver/guide layouts, exact source identities, BEA patch behavior, or rebuild parity.

## Next

Continue Wave916 with another focused cluster, preferably high-level collision detector helpers (`0x00480a30` and neighbors) or physics statement load helpers.
