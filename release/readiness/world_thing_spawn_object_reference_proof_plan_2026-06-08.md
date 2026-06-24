# World / Thing / Spawn / Object-Reference Bridge Proof Plan Readiness Note

Status: proof plan complete, not runtime proof
Date: 2026-06-08
Scope: `world-thing-spawn-object-reference-proof-plan`

This readiness note records the selected static-to-proof child lane after the completed MissionScript / IScript static contract: a World / Thing / Spawn / Object-Reference Bridge Proof Plan.

The selected child lane after this completed bridge plan is `world-thing-spawn-copied-corpus-schema-proof-plan.md`, which records the copied-corpus count vocabulary and first `SpawnThing` schema family before any runtime object-reference or spawn proof.

This is not a new static re-audit wave, not a Ghidra mutation, not a runtime test, not a mission execution proof, not a live loose-MSL loading proof, not a save/career mutation proof, not a screenshot/capture proof, not a native input proof, not a BEA patch, not a Godot slice, and not a rebuild parity claim.

Any later execution must stay copied/app-owned only, no runtime object identity claim until a later proof slice selects and observes a bounded target.

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.

Representative static anchors:

| Surface | Evidence |
| --- | --- |
| MissionScript bridge | `IScript__GetThingRef`, `IScript__SpawnThing`, `CThingPtrDataType`, `GetThingRef`, `SpawnThing`, and `missionscript-iscript-static-contract.md`. |
| Loose corpus | `mission-thing-usage.md` records `57` level rows, `418` `GetThingRef`, `18` `SpawnThing`, and `436` total thing/spawn refs; `world-thing-spawn-copied-corpus-schema-proof-plan.md` records `574` raw `GetThingRef`, `70` raw `SpawnThing`, `644` total raw rows, and `29` spawner-preserving unique `SpawnThing` rows. |
| Registry and bytecode | `0x0052ff30 ScriptCommandRegistry__InitBuiltins`, `144` contiguous `0x40`-byte descriptor records, `0x0064ce50`, `0x0064f210`, `0x005392a0 CScriptObjectCode__CollectSpawnThings`, opcode `0x18`, and `CWorldMeshList__Add`. |
| World/thing review | `mesh-motion-world-particle-static-review-wave905`: `506` function rows, `41` families, `CWorld 38`, `CWorldPhysicsManager 32`, `CThing 28`, `CThing__InitRenderThingFromInitMeshName`, `CWorld__InitOccupancyBitplanes`, `CWorldPhysicsManager__CreateThingByType`. |
| Unit/spawn review | `unit-battleengine-gameplay-static-review-wave906`: `633` function rows, `75` families, `Damage / destruction / spawn`, `CSpawnerThng 14`, `CSpawnerThng__DoSpawn`, `CUnit__VFunc08_InitAndAddToWorld`, `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`. |
| World load bridge | `CWorld__LoadWorld`, `CWorld__LoadScriptEvents`, `CWorld__LoadWorldFile`, `CWorld__DeserializeWorld`, `CWorld__SpawnInitialThings`, `CWorldPhysicsManager__CreateThingByType`, and `CWorldPhysicsManager__ResolveLoadedDefinitionReferences`. |
| InitThing / spawner bridge | `0x0048c650 InitThing__CreateThingByType`, `0x0040e280 CInitThing__LoadFromMemBuffer`, `0x0048dcf0 CInitThing__ctor`, `0x004e3010 CSpawnerThng__Init`, `0x004e36c0 CSpawnerThng__FindSpawnerByName`, `0x004e3c60 CSpawnerThng__DoSpawn`, `0x004e3f90 CSpawnerThng__ProcessSpawnWave`, `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed`, `0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName`, and `CUnit__SetSpawnCooldownState3`. |

Retained backups include:

- `G:\GhidraBackups\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`
- `G:\GhidraBackups\BEA_20260526-105331_post_wave906_unit_battleengine_gameplay_static_review_verified`
- `G:\GhidraBackups\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified`
- `G:\GhidraBackups\BEA_20260525-050626_post_wave844_cworld_load_world_verified`
- `G:\GhidraBackups\BEA_20260518-155904_post_wave556_cworld_tail_verified`
- `G:\GhidraBackups\BEA_20260525-060333_post_wave846_worldphysics_load_resolve_verified`
- `G:\GhidraBackups\BEA_20260525-053251_post_wave845_spawner_type_allowed_verified`
- `G:\GhidraBackups\BEA_20260525-013914_post_wave837_cunit_spawn_cooldown_verified`
- `G:\GhidraBackups\BEA_20260601-225655_post_wave1064_iscript_setthing_command_bridge_verified`

No runtime MissionScript execution, runtime `GetThingRef` behavior, runtime `SpawnThing` behavior, runtime world loading behavior, runtime object identity, runtime spawner behavior, runtime Unit/BattleEngine spawn behavior, live loose-MSL loading, packed-resource script selection, exact `IScript__GetThingRef` or `IScript__SpawnThing` handler address proof, exact world/thing/spawner/Unit/MissionScript layouts, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity claim is made.
