# Weapon / Projectile Spawn Handoff Proof Plan Readiness Note

Status: proof plan complete, not runtime proof
Date: 2026-06-08
Scope: `weapon-projectile-spawn-handoff-proof-plan`

This readiness note records a public-safe static-to-proof planning slice for the Unit/BattleEngine weapon-to-projectile handoff. It is not a new static re-audit wave, not a runtime test, not a screenshot/capture proof, not a BEA patch, not a Godot slice, and not a rebuild parity claim.

Primary static contract source: `unit-battleengine-gameplay-static-contract.md`. The plan records copied-profile guardrails, weapon/burst/round layout unknowns, and stop conditions before any runtime/proof work can start.

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.

Static source evidence:

- Wave1160 (`wave1160-weapon-projectile-targeting-current-risk-review`): `19` metadata rows, `19` tag rows, `51` xref rows, `3272` instruction rows, and `19` decompile rows. Verified backup: `G:\GhidraBackups\BEA_20260606-011357_post_wave1160_weapon_projectile_targeting_current_risk_review_verified`.
- Wave1027 (`battleengine-walkerpart-weapon-spine-review-wave1027`): `12` primary metadata rows, `12` tag rows, `39` xref rows, `704` body-instruction rows, and `12` decompile rows. Verified backup: `G:\GhidraBackups\BEA_20260601-014543_post_wave1027_battleengine_walkerpart_weapon_spine_review_verified`.
- Wave1029 (`battleengine-jetpart-weapon-status-review-wave1029`): `13` primary metadata rows, `13` tag rows, `19` xref rows, `790` body-instruction rows, and `13` decompile rows. Verified backup: `G:\GhidraBackups\BEA_20260601-025247_post_wave1029_battleengine_jetpart_weapon_status_review_verified`.
- Wave1020 (`projectile-burst-spawn-spine-review-wave1020`): `5` primary metadata rows, `5` tag rows, `22` xref rows, `1651` body-instruction rows, `5` decompile rows, and a `48`-row pointer-table export from `0x005dfc94`. Verified backup: `G:\GhidraBackups\BEA_20260531-214433_post_wave1020_projectile_burst_spawn_spine_review_verified`.

Representative anchors:

| Surface | Static anchor |
| --- | --- |
| Auto-target/projectile wrapper boundary | `0x00406560 CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` |
| WalkerPart fire dispatch | `0x00413cc0 CBattleEngineWalkerPart__FireWeapon` |
| WalkerPart fired bookkeeping | `0x004140d0 CBattleEngineWalkerPart__WeaponFired` |
| JetPart fired bookkeeping | `0x00412050 CBattleEngineJetPart__WeaponFired` |
| Current weapon resolver | `0x00414030 CBattleEngineWalkerPart__GetCurrentWeapon` |
| Weapon target/profile filter | `0x005061f0 CWeapon__DoesTargetMaskMatchDistanceProfile` |
| Weapon charge/progress helper | `0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned` |
| Weapon burst event handler | `0x00506930 CWeapon__HandleFireBurstEvent` |
| ProjectileBurst fallback dispatcher | `0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback` |
| ProjectileBurst current-preset body | `0x005069f0 ProjectileBurst__SpawnFromCurrentPreset` |
| Preset/list entry accessor | `0x005078b0 ProjectileBurstPreset__GetListEntryIdByIndex` |
| Round target-reader sync | `0x004dac90 CRound__SelectBestTargetReaderAndSyncAimState` |
| Round spawn helper | `0x004db150 CRound__SpawnConfiguredProjectile` |
| Round arming/trail helper | `0x004db630 CRound__ArmProjectileAndSpawnTrailEffect` |

Proof-plan boundaries:

- The plan is limited to a selected weapon path through WalkerPart or JetPart weapon state, `CWeapon` event/filtering helpers, `ProjectileBurst` preset/fallback dispatch, and `CRound` spawn/arming handoff.
- `0x00406560 CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` is projectile/auto-target evidence only, not exact `CBattleEngine::WeaponFired` identity.
- `0x00506930 CWeapon__HandleFireBurstEvent` remains behavior-backed event-handler naming, not final source `CWeapon::Fire` identity.
- copied-profile guardrails apply to any later runtime/proof execution.
- Any later proof must use copied profiles or app-owned artifact roots.
- Any later proof must use one selected weapon/path/state target and stop on ambiguous weapon identity, ambiguous projectile identity, non-reproducible state, private artifact leakage, unexpected file mutation, or any need to touch the installed game.
- Wave1161/Wave1162 collision and terrain rows as context only.
- The plan explicitly does not include runtime weapon fire, collision, terrain interaction, target damage, target kill, cloak/stealth, broad Unit/BattleEngine runtime proof, visual QA, patching behavior, rebuild parity, or no-noticeable-difference parity.

No runtime weapon fire behavior, runtime projectile behavior, runtime projectile collision behavior, runtime damage behavior, stealth/cloak behavior, exact retail `CBattleEngine::WeaponFired` identity, `weapon_fire_breaks_stealth`, exact source `CWeapon::Fire` identity, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, rebuild parity, or no-noticeable-difference parity claim is made.
