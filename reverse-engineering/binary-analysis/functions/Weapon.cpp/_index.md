# Weapon.cpp Functions

> Source File: Weapon.cpp | Binary: BEA.exe
> Last updated: 2026-06-06

## Current Status

Wave1160 (`wave1160-weapon-projectile-targeting-current-risk-review`) re-read the CWeapon and ProjectileBurst spine as part of the active current-risk denominator. It verified `19 CWeapon/ProjectileBurst/CRound current-risk rows` with fresh Ghidra metadata, tags, xrefs, instructions, and decompile exports, and saved tag-only normalization for `0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback` and `0x005069f0 ProjectileBurst__SpawnFromCurrentPreset`.

Probe token anchor: Wave1160; wave1160-weapon-projectile-targeting-current-risk-review; 516/1179 = 43.77%; 19 CWeapon/ProjectileBurst/CRound current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 663; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=2 skipped=0 renamed=0; tags_added=16; no rename; no signature change; no comment change; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 51 xref rows; 3272 instruction rows; CWeapon__DoesTargetMaskMatchDistanceProfile; ProjectileBurst__SpawnFromPercentBucketFallback; ProjectileBurst__SpawnFromCurrentPreset; CRound__SpawnConfiguredProjectile; CRound__ArmProjectileAndSpawnTrailEffect; [maintainer-local-ghidra-backup-root]\BEA_20260606-011357_post_wave1160_weapon_projectile_targeting_current_risk_review_verified; weapon_fire_breaks_stealth; exact CBattleEngine::WeaponFired; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Static Weapon / ProjectileBurst Spine

| Address | Saved Ghidra name | Static role |
| --- | --- | --- |
| `0x00505e00` | `CWeapon__ctor_base` | CWeapon construction and profile/weapon-data state initialization. |
| `0x005061f0` | `CWeapon__DoesTargetMaskMatchDistanceProfile` | Target-unit mask/profile gate reached by BattleEngine firing callers. |
| `0x00506350` | `CWeapon__GetDistanceProfileField90` | Distance/profile field `+0x90` accessor. |
| `0x00506440` | `CWeapon__GetDistanceProfileField94` | Distance/profile field `+0x94` float accessor. |
| `0x00506530` | `CWeapon__GetDistanceProfileFieldA8` | Distance/profile field `+0xa8` firing-mode selector accessor. |
| `0x00506620` | `CWeapon__GetDistanceProfileField98` | Distance/profile field `+0x98` float accessor. |
| `0x00506710` | `CWeapon__GetDistanceProfileField9C` | Distance/profile field `+0x9c` target-search scale accessor. |
| `0x00506800` | `CWeapon__GetDistanceProfileFieldA0` | Distance/profile field `+0xa0` target-search scale accessor. |
| `0x005068f0` | `CWeapon__AdvanceChargeProgressIfAnySlotAssigned` | Assigned-slot charge/progress update helper. |
| `0x00506010` | `ProjectileBurst__SpawnFromPercentBucketFallback` | Percent-bucket fallback dispatcher; Wave1160 tag normalization target. |
| `0x005069f0` | `ProjectileBurst__SpawnFromCurrentPreset` | Current-preset projectile-burst body; Wave1160 tag normalization target. |
| `0x005078b0` | `ProjectileBurstPreset__GetListEntryIdByIndex` | One-argument preset/list entry id accessor. |

## Static Handoff

The saved static path ties BattleEngine/WalkerPart/JetPart weapon callers into CWeapon profile gates, CWeapon charge/progress state, ProjectileBurst preset dispatch, and CRound projectile creation/effect helpers. CRound details live in [`../Round.cpp/_index.md`](../Round.cpp/_index.md), and the subsystem-level map lives in [`../../unit-battleengine-gameplay-static-contract.md`](../../unit-battleengine-gameplay-static-contract.md).

## Boundary

This page is static Ghidra evidence only. Exact source `CWeapon::Fire`, exact retail `CBattleEngine::WeaponFired`, `weapon_fire_breaks_stealth`, runtime fire/projectile/stealth behavior, concrete CWeapon/profile/ProjectileBurst/list layouts, BEA patch behavior, visual QA, and clean-room rebuild parity remain separate proof.
