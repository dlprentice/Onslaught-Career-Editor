# Wave1160 Weapon Projectile Targeting Current-Risk Review

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x004dac90` proposed correction rejected; known-stale live metadata retained for separate correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static metadata correction evidence
Date: 2026-06-06
Tag: `wave1160-weapon-projectile-targeting-current-risk-review`

Wave1160 re-read nineteen CWeapon, ProjectileBurst, and CRound current-risk rows from the active `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra exports. The pass found two ProjectileBurst rows with saved names, signatures, and comments but missing current audit tags, then performed tag-only normalization for `0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback` and `0x005069f0 ProjectileBurst__SpawnFromCurrentPreset`.

Probe token anchor: Wave1160; wave1160-weapon-projectile-targeting-current-risk-review; 516/1179 = 43.77%; 19 CWeapon/ProjectileBurst/CRound current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 663; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=2 skipped=0 renamed=0; tags_added=16; no rename; no signature change; no comment change; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 51 xref rows; 3272 instruction rows; CWeapon__DoesTargetMaskMatchDistanceProfile; ProjectileBurst__SpawnFromPercentBucketFallback; ProjectileBurst__SpawnFromCurrentPreset; CRound__SpawnConfiguredProjectile; CRound__ArmProjectileAndSpawnTrailEffect; [maintainer-local-ghidra-backup-root]\BEA_20260606-011357_post_wave1160_weapon_projectile_targeting_current_risk_review_verified; weapon_fire_breaks_stealth; exact CBattleEngine::WeaponFired; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Read-back evidence:

- Pre exports: `19` metadata rows, `19` tag rows, `51` xref rows, `3272` instruction rows, and `19` decompile rows.
- Apply dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=16 missing=0 bad=0`.
- Apply: `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=16 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final dry: `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post exports: `19` metadata rows, `19` tag rows, `51` xref rows, `3272` instruction rows, and `19` decompile rows.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-011357_post_wave1160_weapon_projectile_targeting_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

Representative anchors:

| Address | Function | Static role |
| --- | --- | --- |
| `0x00505e00` | `CWeapon__ctor_base` | CWeapon construction, initial distance/profile state, and weapon-data/current context storage. |
| `0x005061f0` | `CWeapon__DoesTargetMaskMatchDistanceProfile` | Current-weapon target/profile mask gate reached by BattleEngine firing callers. |
| `0x005068f0` | `CWeapon__AdvanceChargeProgressIfAnySlotAssigned` | Assigned-slot charge/progress helper used by burst/charge paths. |
| `0x00506010` | `ProjectileBurst__SpawnFromPercentBucketFallback` | Shared percent-bucket fallback dispatcher; Wave1160 added missing audit/readback tags. |
| `0x005069f0` | `ProjectileBurst__SpawnFromCurrentPreset` | Current-preset projectile-burst body; Wave1160 added missing audit/readback tags. |
| `0x005078b0` | `ProjectileBurstPreset__GetListEntryIdByIndex` | One-argument preset/list entry id accessor. |
| `0x004dac90` | `CRound__SelectBestTargetReaderAndSyncAimState` | Aim-space target-reader selection and event scheduling. |
| `0x004db150` | `CRound__SpawnConfiguredProjectile` | Configured projectile spawn helper and CRoundInitThing-like payload builder. |
| `0x004db630` | `CRound__ArmProjectileAndSpawnTrailEffect` | Launch-state, velocity, and trail-effect arming helper. |

Accounting after Wave1160:

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave911 focused historical residual | `596` rows, historical-retired/non-reconstructable, `300` materialized focused rows |
| Wave911 top-500 risk-ranked subset | `500/500 = 100.00%` |
| Wave1108 current focused accounting | `516/1179 = 43.77%` |
| Current risk candidates | `6166` |
| Current focused candidates | `1178` |
| Live regenerated current focused candidates | `1178` |
| Remaining active focused work | `663` |

What this proves:

- The nineteen selected CWeapon/ProjectileBurst/CRound rows exist in the saved Ghidra project with clean names, signatures, comments, post-state tags, xrefs, instruction exports, and decompile exports.
- The two ProjectileBurst rows now carry the same current-risk audit/readback tag trail as the adjacent static weapon/projectile spine evidence.
- The static CWeapon distance-profile helpers, ProjectileBurst dispatcher/preset helpers, and CRound targeting/spawn/trail helpers form one documented static handoff path for clean-room planning.

What remains separate:

- Exact source `CWeapon::Fire` identity.
- Exact retail `CBattleEngine::WeaponFired` identity.
- `weapon_fire_breaks_stealth`.
- Runtime weapon, targeting, projectile, trail/effect, cloak, stealth, or fire behavior.
- Exact concrete CWeapon, profile, ProjectileBurst, CRound, preset/list, active-reader, and effect/trail layouts.
- BEA patching behavior.
- Visual QA.
- Clean-room rebuild parity.
