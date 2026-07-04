# Wave1160 Weapon Projectile Targeting Current-Risk Review

Status: complete static metadata correction evidence
Date: 2026-06-06
Tag: `wave1160-weapon-projectile-targeting-current-risk-review`

Wave1160 accounts for `19 CWeapon/ProjectileBurst/CRound current-risk rows` from the active `wave1108-current-risk-rank` current-risk denominator. Fresh Ghidra exports showed the prior static names, comments, and signatures were coherent, but `ProjectileBurst__SpawnFromPercentBucketFallback` and `ProjectileBurst__SpawnFromCurrentPreset` lacked the current audit/readback tags. The Ghidra write was tag-only normalization for those two rows.

Probe token anchor: Wave1160; wave1160-weapon-projectile-targeting-current-risk-review; 516/1179 = 43.77%; 19 CWeapon/ProjectileBurst/CRound current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 663; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=2 skipped=0 renamed=0; tags_added=16; no rename; no signature change; no comment change; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 51 xref rows; 3272 instruction rows; CWeapon__DoesTargetMaskMatchDistanceProfile; ProjectileBurst__SpawnFromPercentBucketFallback; ProjectileBurst__SpawnFromCurrentPreset; CRound__SpawnConfiguredProjectile; CRound__ArmProjectileAndSpawnTrailEffect; [maintainer-local-ghidra-backup-root]\BEA_20260606-011357_post_wave1160_weapon_projectile_targeting_current_risk_review_verified; weapon_fire_breaks_stealth; exact CBattleEngine::WeaponFired; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Evidence

Fresh exports under `subagents/ghidra-static-reaudit/wave1160-weapon-projectile-targeting-current-risk-review/`:

| Artifact | Pre rows | Post rows |
| --- | ---: | ---: |
| `metadata.tsv` | 19 | 19 |
| `tags.tsv` | 19 | 19 |
| `xrefs.tsv` | 51 | 51 |
| `instructions.tsv` | 3272 | 3272 |
| `decompile/index.tsv` | 19 | 19 |

Mutation logs:

| Step | Summary |
| --- | --- |
| Dry | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=16 missing=0 bad=0` |
| Apply | `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=16 missing=0 bad=0` |
| Final dry | `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |

Reviewed anchors:

| Address | Function | Static role |
| --- | --- | --- |
| `0x00505e00` | `CWeapon__ctor_base` | CWeapon construction, profile state, weapon-data pointer, and caller context storage. |
| `0x005061f0` | `CWeapon__DoesTargetMaskMatchDistanceProfile` | Current-weapon target/profile mask gate. |
| `0x00506350` | `CWeapon__GetDistanceProfileField90` | Distance/profile table field `+0x90` accessor. |
| `0x00506440` | `CWeapon__GetDistanceProfileField94` | Distance/profile table float field `+0x94` accessor. |
| `0x00506530` | `CWeapon__GetDistanceProfileFieldA8` | Distance/profile firing-mode selector field `+0xa8` accessor. |
| `0x00506620` | `CWeapon__GetDistanceProfileField98` | Distance/profile facing/range field `+0x98` accessor. |
| `0x00506710` | `CWeapon__GetDistanceProfileField9C` | Distance/profile target-search scale field `+0x9c` accessor. |
| `0x00506800` | `CWeapon__GetDistanceProfileFieldA0` | Alternate distance/profile target-search scale field `+0xa0` accessor. |
| `0x005068f0` | `CWeapon__AdvanceChargeProgressIfAnySlotAssigned` | Assigned-slot charge/progress helper. |
| `0x00506010` | `ProjectileBurst__SpawnFromPercentBucketFallback` | Percent-bucket fallback dispatcher; Wave1160 tag normalization target. |
| `0x005069f0` | `ProjectileBurst__SpawnFromCurrentPreset` | Current-preset burst body; Wave1160 tag normalization target. |
| `0x005078b0` | `ProjectileBurstPreset__GetListEntryIdByIndex` | Preset/list index helper. |
| `0x004d9ef0` | `CRound__UpdateRoundAndTriggerLaunchEffect` | Launch-effect update helper. |
| `0x004dac90` | `CRound__SelectBestTargetReaderAndSyncAimState` | Target-reader selection and aim-state synchronization. |
| `0x004db150` | `CRound__SpawnConfiguredProjectile` | Configured projectile spawn and CRoundInitThing-like payload build. |
| `0x004d9f30` | `CRound__UpdateEffectTransformByMode_004d9f30` | Mode-dispatched effect-transform helper. |
| `0x004daab0` | `CRound__SetTargetReaderIfAllowed` | Target-reader binding and replacement helper. |
| `0x004db090` | `CRound__GetPresetScalarByConfigName` | Preset-list scalar lookup by round-config name. |
| `0x004db630` | `CRound__ArmProjectileAndSpawnTrailEffect` | Launch-state, velocity, and trail-effect arming helper. |

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-011357_post_wave1160_weapon_projectile_targeting_current_risk_review_verified`; `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

## Accounting

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

This is the active current-risk denominator, not Wave911 reconstruction.

## Boundary

This review proves static retail Ghidra metadata/decompile/xref/instruction evidence plus tag-only read-back normalization for two ProjectileBurst rows. It does not prove exact source `CWeapon::Fire`, exact retail `CBattleEngine::WeaponFired`, `weapon_fire_breaks_stealth`, runtime weapon/projectile/stealth behavior, exact concrete layouts, BEA patching behavior, visual QA, or rebuild parity.
