# Unit / BattleEngine / Gameplay Static Review

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: static-coherent system slice
Date: 2026-05-26
Scope: `unit-battleengine-gameplay-static-review-wave906`

MissionScript object references connect to this Unit/BattleEngine evidence
through `missionscript-iscript-static-contract.md`, world-load/factory anchors,
and spawner anchors. These static links do not establish runtime spawn behavior,
object identity, gameplay outcomes, visual output, or rebuild parity.

Wave906 reviews the Unit, BattleEngine, weapon, projectile, AI, target, spawn, and damage/destruction surface after the loaded Ghidra function-quality queue reached `6113/6113 = 100.00%`. It ties shared `CUnit` state, `CUnitAI` behavior, BattleEngine player-mode logic, weapon/round construction and firing, target selection, squad/spawn helpers, concrete unit subclasses, and damage/destructible-segment rows into one system classification.

Classification: `static-coherent Unit/BattleEngine/gameplay core`.

Source boundary: Stuart's source remains useful architecture/name/logic evidence, but the authority for this review is the Steam retail binary as loaded in Ghidra plus current public-safe read-back docs. This review is not runtime proof.

## Function-Family Surface

The Wave906 evidence snapshot covers `633` function rows across `75` selected owner families. Every selected row has a non-empty comment and a clean signature with no exact-`undefined` return and no `param_N` placeholders.

Cluster counts:

| Cluster | Rows |
| --- | ---: |
| Unit core / AI / squads | 199 |
| BattleEngine player state | 133 |
| Weapons / rounds / targeting | 106 |
| Unit subclasses / guides | 102 |
| Damage / destruction / spawn | 93 |

Representative family counts:

| Family | Rows |
| --- | ---: |
| `CUnit` | 90 |
| `CUnitAI` | 63 |
| `CBattleEngine` | 47 |
| `CSquadNormal` | 31 |
| `CBattleEngineWalkerPart` | 27 |
| `CBattleEngineJetPart` | 23 |
| `CGeneralVolume` | 23 |
| `CDestructableSegmentsController` | 19 |
| `CCollisionSeekingRound` | 17 |
| `CSpawnerThng` | 14 |
| `CRound` | 13 |
| `CWeapon` | 12 |

Representative anchors include `CUnit__ApplyDamage`, `CUnit__GetCurrentHealthOrSubtreeHealth`, `CUnitAI__UpdateActivationStateAndSpawnPickup`, `CUnitAI__UpdateDeployAimAndScheduleEvent`, `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`, `CBattleEngine__AddProjectile`, `CBattleEngine__Morph`, `CBattleEngine__HandleCloak`, `CBattleEngine__AugmentWeapon`, `CBattleEngineJetPart__WeaponFired`, `CBattleEngineWalkerPart__WeaponFired`, `CWeapon__HandleFireBurstEvent`, `CRound__SpawnConfiguredProjectile`, `CCollisionSeekingRound__ProcessMapWhoCollisionSweep`, `CDamage__CreateTextureBuffer`, `CGeneralVolume__SpawnPickupAndDispatch`, `CSquadNormal__SelectBestEngagementTarget`, `CSpawnerThng__DoSpawn`, `CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold`, `CDestroyableSegment__VFunc_03_ApplyDamage`, `BattleEngineConfigurations__GetConfiguration`, and `CBattleEngineData__LoadFromMemBuffer`.

## Static Classification

- The selected Unit/BattleEngine/gameplay owner families have no remaining function-quality queue debt.
- The current static documentation connects unit lifecycle, CUnitAI deploy/activation/target helpers, BattleEngine mode/weapon/target/projectile helpers, weapon and round config loaders, projectile spawn and collision-seeking paths, squad targeting, spawner waves, concrete unit subclass guide rows, and destructible segment damage handling.
- The verified read-only Ghidra backup for this review is `[maintainer-local-ghidra-backup-root]\BEA_20260526-105331_post_wave906_unit_battleengine_gameplay_static_review_verified`.

## What Remains Separate

- Exact concrete `CUnit`, `CUnitAI`, `CBattleEngine`, weapon, round, squad, spawner, and destructible object layouts.
- Runtime damage, AI, weapon, input, mode-switching, targeting, spawn, and projectile behavior.
- Runtime mission/gameplay outcomes.
- BEA patch behavior.
- Rebuild parity.
