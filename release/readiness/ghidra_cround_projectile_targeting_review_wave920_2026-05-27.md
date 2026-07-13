# Ghidra Wave920 CRound projectile/targeting review (2026-05-27)

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004d8410` comment correction; `0x004dac90` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: read-only static review
Date: 2026-05-27
Branch: `main`
Tag: `cround-projectile-targeting-review-wave920`

## Scope

Wave920 reviewed CRound projectile, targeting, preset, and launch helpers from the Wave911 focused correction queue:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x004d9ef0` | `CRound__UpdateRoundAndTriggerLaunchEffect` | Reviewed; no mutation |
| `0x004daab0` | `CRound__SetTargetReaderIfAllowed` | Reviewed; no mutation |
| `0x004daba0` | `CRound__FindNearbyHostileWithinProjectileRadius` | Reviewed; no mutation |
| `0x004dac90` | `CRound__SelectBestTargetReaderAndSyncAimState` | Reviewed; no mutation |
| `0x004db090` | `CRound__GetPresetScalarByConfigName` | Reviewed; no mutation |
| `0x004db150` | `CRound__SpawnConfiguredProjectile` | Reviewed; no mutation |
| `0x004db630` | `CRound__ArmProjectileAndSpawnTrailEffect` | Reviewed; no mutation |
| `0x004d8410` | `CRound__Init` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave920-cround-projectile-targeting-review/metadata.tsv
subagents/ghidra-static-reaudit/wave920-cround-projectile-targeting-review/tags.tsv
subagents/ghidra-static-reaudit/wave920-cround-projectile-targeting-review/instructions.tsv
subagents/ghidra-static-reaudit/wave920-cround-projectile-targeting-review/decompile/
```

Read-back result:

```text
metadata: 8/8 OK
tags: 8/8 OK
instructions: 1369 rows
decompile: 8/8 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the current evidence. The current source snapshot does not include full `Round.cpp`, so no stronger source-backed correction was available. Static read-back continues to support CRound-local target binding, nearby hostile lookup, aim-state synchronization, preset scalar lookup, configured projectile spawning, and trail-effect arming.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260527-140619_post_wave920_cround_projectile_targeting_review_verified
files=19
bytes=173247367
```

## Truth boundary

This review confirms static Ghidra coherence for selected CRound projectile/targeting helpers. It does not prove runtime projectile behavior, concrete round/config/init payload layouts, BEA patch behavior, or rebuild parity.

## Next

Continue Wave921 with another focused cluster from Wave911, preferably HiveBoss config helpers or frontend text/layout helpers where source-callsite evidence may provide correction opportunities.
