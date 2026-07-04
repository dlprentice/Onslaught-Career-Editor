# World / Thing / Spawn / Object-Reference Bridge Proof Plan

Status: proof plan complete, not runtime proof
Last updated: 2026-06-08
Scope: `world-thing-spawn-object-reference-proof-plan`
Canonical file: `world-thing-spawn-object-reference-proof-plan.md`

This completed plan is the selected static-to-proof child lane after the completed MissionScript / IScript static contract. It bridges static MissionScript `GetThingRef` / `SpawnThing` evidence into the saved world-loading, world-factory, thing lifecycle, Unit/BattleEngine spawn, spawner, and mesh/resource contracts before any runtime mission execution or rebuild prototype work.

The selected child lane after this bridge plan is [World / Thing / Spawn Copied-Corpus Object-Reference Schema Proof Plan](world-thing-spawn-copied-corpus-schema-proof-plan.md). That schema slice makes the loose-MSL count vocabulary reproducible before any runtime object-reference or spawn proof. The copied-corpus schema result is [World / Thing / Spawn Copied-Corpus Schema Proof](world-thing-spawn-copied-corpus-schema-proof.md), backed by [world-thing-spawn-copied-corpus-schema.v1.json](../game-assets/world-thing-spawn-copied-corpus-schema.v1.json). The next completed child lane is [World / Thing / Spawn Spawner Handoff Static Proof](world-thing-spawn-spawner-handoff-static-proof.md), backed by [world-thing-spawn-spawner-handoff-static.v1.json](world-thing-spawn-spawner-handoff-static.v1.json), with status: static spawner handoff proof complete, not runtime proof. It maps the selected `training-target-spawn-family` through static spawner handoff anchors without runtime spawn proof. The next completed object-reference child lane is [World / Thing / Spawn GetThingRef Object-Reference Static Proof](world-thing-spawn-getthingref-object-reference-static-proof.md), backed by [world-thing-spawn-getthingref-object-reference-static.v1.json](world-thing-spawn-getthingref-object-reference-static.v1.json), with status: static GetThingRef object-reference proof complete, not runtime proof. It maps the selected `training-target-zone-getthingref-family` through static corpus, descriptor/datatype, and world-boundary anchors without runtime object lookup proof.

This plan does not launch BEA, mutate Ghidra, mutate the installed game, patch an executable, execute scripts, load a live mission, drive native input, mutate saves/options, capture screenshots, start Godot work, or claim runtime object identity, spawn behavior, world-load behavior, mission outcomes, exact concrete layouts, patch behavior, visual QA, rebuild parity, or no-noticeable-difference parity.

The plan records static authorities, copied/app-owned guardrails, object-reference identity unknowns, world/spawn bridge anchors, and stop conditions. It is a map and proof-design artifact, not proof that a runtime level has resolved or spawned any specific object.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; it is not the active completion gate.

The percentage front door remains `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md` and `reverse-engineering/binary-analysis/static-reaudit-progress.json`. This proof plan does not create a new static RE percentage.

Primary static and corpus sources:

- `reverse-engineering/binary-analysis/missionscript-iscript-static-contract.md`
- `reverse-engineering/binary-analysis/missionscript-iscript-proof-plan.md`
- `reverse-engineering/game-assets/mission-thing-usage.md`
- `reverse-engineering/binary-analysis/mesh-motion-world-particle-static-review-2026-05-26.md`
- `reverse-engineering/binary-analysis/unit-battleengine-gameplay-static-review-2026-05-26.md`
- `reverse-engineering/binary-analysis/unit-battleengine-gameplay-static-contract.md`
- `reverse-engineering/binary-analysis/functions/ScriptObjectCode.cpp.md`
- `reverse-engineering/binary-analysis/functions/World.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/World.cpp/CWorld__LoadWorld.md`
- `reverse-engineering/binary-analysis/functions/WorldPhysicsManager.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/SpawnerThng.cpp/_index.md`
- `release/readiness/ghidra_cworld_load_tail_review_wave1073_2026-06-02.md`
- `release/readiness/ghidra_cworld_load_world_wave844_2026-05-25.md`
- `release/readiness/ghidra_cworld_tail_wave556_2026-05-18.md`
- `release/readiness/ghidra_worldphysics_load_resolve_wave846_2026-05-25.md`
- `release/readiness/ghidra_spawner_type_allowed_wave845_2026-05-25.md`
- `release/readiness/ghidra_cunit_spawn_cooldown_wave837_2026-05-25.md`
- `release/readiness/ghidra_iscript_setthing_command_bridge_wave1064_2026-06-01.md`

## Retained Evidence Anchors

| Surface | Static evidence |
| --- | --- |
| MissionScript object commands | `IScript__GetThingRef`, `IScript__SpawnThing`, `GetThingRef`, `SpawnThing`, `CThingPtrDataType`, and the `missionscript-iscript-static-contract.md` thing/spawn/object-reference bridge. |
| Loose MSL thing corpus | `mission-thing-usage.md` records `57` level rows, `418` `GetThingRef`, `18` `SpawnThing`, and `436` total thing/spawn refs from `game/data/MissionScripts/**.msl`; [World / Thing / Spawn Copied-Corpus Object-Reference Schema Proof Plan](world-thing-spawn-copied-corpus-schema-proof-plan.md) records the raw detailed rows as `574` raw `GetThingRef`, `70` raw `SpawnThing`, `644` total raw rows, and `29` unique spawner-preserving `SpawnThing` rows; [World / Thing / Spawn Copied-Corpus Schema Proof](world-thing-spawn-copied-corpus-schema-proof.md) and [world-thing-spawn-copied-corpus-schema.v1.json](../game-assets/world-thing-spawn-copied-corpus-schema.v1.json) make those counts executable as a copied-corpus schema result; [World / Thing / Spawn Spawner Handoff Static Proof](world-thing-spawn-spawner-handoff-static-proof.md) and [world-thing-spawn-spawner-handoff-static.v1.json](world-thing-spawn-spawner-handoff-static.v1.json) map the selected training-target `SpawnThing` family into static handoff anchors; [World / Thing / Spawn GetThingRef Object-Reference Static Proof](world-thing-spawn-getthingref-object-reference-static-proof.md) and [world-thing-spawn-getthingref-object-reference-static.v1.json](world-thing-spawn-getthingref-object-reference-static.v1.json) map the selected training target-zone `GetThingRef` family into static object-reference anchors. |
| Script object-code spawn pre-scan | `0x005392a0 CScriptObjectCode__CollectSpawnThings` scans `SpawnThing` opcode `0x18` style instructions and calls `CWorldMeshList__Add` for mesh preload planning. |
| World/thing static review | `mesh-motion-world-particle-static-review-wave905` covers `506` function rows across `41` selected owner families, including `CWorld 38`, `CWorldPhysicsManager 32`, and `CThing 28`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`. |
| Unit/spawn static review | `unit-battleengine-gameplay-static-review-wave906` covers `633` function rows across `75` families, including `Damage / destruction / spawn`, `CSpawnerThng 14`, and Unit/BattleEngine spawn handoff anchors. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-105331_post_wave906_unit_battleengine_gameplay_static_review_verified`. |
| CWorld load tail | Wave1073 `cworld-load-tail-review-wave1073` read-only evidence covers `23` metadata rows, `23` tag rows, `62` xref rows, `2095` instruction rows, and `23` decompile rows, plus context around `CWorld__LoadScriptEvents`, `CWorld__LoadWorldFile`, `CWorld__DeserializeWorld`, `CWorld__SpawnInitialThings`, and `CWorldPhysicsManager__CreateThingByType`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified`. |
| CWorld load entry | Wave844 names `0x0050b9c0 CWorld__LoadWorld`, with static calls to `CWorld__LoadScriptEvents`, `CWorld__LoadWorldFile`, `CWorldPhysicsManager__CreateThingByType`, and `CWorld__SpawnInitialThings`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-050626_post_wave844_cworld_load_world_verified`. |
| World factory bridge | Wave556 hardens `0x0050dcb0 CWorld__SpawnInitialThings` and `0x0050df80 CWorldPhysicsManager__CreateThingByType` as CWorld tail / world-thing factory bridge evidence. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-155904_post_wave556_cworld_tail_verified`. |
| World physics resolve | Wave846 covers `CWorldPhysicsManager__ResolveLoadedDefinitionReferences`, `FreeNestedThingSets_6C`, `ReloadDefaultPhysicsAndBattleEngineData`, and `ClearAndFreeAllDefinitionLists`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-060333_post_wave846_worldphysics_load_resolve_verified`. |
| Spawner gate | Wave845 covers `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed`, with callers from `CSpawnerThng__Init` and `CSpawnerThng__Constructor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-053251_post_wave845_spawner_type_allowed_verified`. |
| Spawn cooldown handoff | Wave837 covers `0x004fc3a0 CUnit__SetSpawnCooldownState3`, called from `0x004e430f CSpawnerThng__ProcessSpawnWave` after `CWorldPhysicsManager__CreateThingByType` and spawned-object init-slot dispatch. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-013914_post_wave837_cunit_spawn_cooldown_verified`. |
| IScript thing command bridge | Wave1064 covers six IScript thing command bridge rows including `IScript__SetThingValueViaVFunc198_FromArg`, `IScript__SetThingValueViaVFunc19C_FromArg`, `CEngine__EnableThingByNameFlag`, `CEngine__DisableThingByNameFlag`, and `CUnit__SetFactionForHierarchy`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-225655_post_wave1064_iscript_setthing_command_bridge_verified`. |

## Static Anchors

The plan is built around saved retail Ghidra evidence and public-safe corpus docs. Stuart source remains useful for names and architecture, but the loaded Steam retail binary and copied corpus evidence remain authority.

| Surface | Static anchor |
| --- | --- |
| Script reference entry | `IScript__GetThingRef` and `IScript__SpawnThing` are the MissionScript command-side entry points for object reference and spawn planning. |
| Script registry entry | `0x0052ff30 ScriptCommandRegistry__InitBuiltins` writes `144` contiguous `0x40`-byte command descriptor records from `0x0064ce50` through `0x0064f210`; `GetThingRef` / `SpawnThing` are command anchors, not exact handler-address proof in this slice. |
| Thing pointer datatype | `CThingPtrDataType` is the static datatype-family anchor for thing pointer values in MissionScript planning; exact VM/value layout remains open. |
| Loose corpus names | `mission-thing-usage.md` preserves level, file, thing, and spawner strings for `GetThingRef` and `SpawnThing`; casing and spelling must be preserved in later copied-corpus proof. The selected copied-corpus schema child lane is `world-thing-spawn-copied-corpus-schema-proof-plan.md`. |
| SpawnThing pre-scan | `0x005392a0 CScriptObjectCode__CollectSpawnThings` scans opcode `0x18` / SpawnThing-style bytecode and calls `CWorldMeshList__Add` before runtime execution proof exists. |
| World load shell | `0x0050b9c0 CWorld__LoadWorld` links world file loading, script events, factory creation, and initial spawn work into one static world-load shell. |
| Script-event load handoff | `0x0050ac70 CWorld__LoadScriptEvents` is the world-side script-event load anchor; it is not proof that loose scripts are selected or executed at runtime. |
| World file parse | `CWorld__LoadWorldFile`, `CWorld__DeserializeWorld`, and `CWorld__LoadWorldHeader` are world-data parse anchors, not exact file-format completeness proof. |
| World mesh list | `0x0050d9e0 CWorldMeshList__Add` is called by `CWorld__LoadWorld`, `CSpawnerThng__Init`, `CScriptObjectCode__CollectSpawnThings`, and recursive child-name paths; it deduplicates `DAT_00855358` and compares definitions at `DAT_008553fc +0xb0`. |
| Initial spawn pass | `0x0050dcb0 CWorld__SpawnInitialThings` is the static initial-spawn pass anchor. |
| Factory bridge | `0x0050df80 CWorldPhysicsManager__CreateThingByType` and `CWorldPhysicsManager__CreateProjectile` are world/physics factory bridge anchors. |
| Definition reference resolve | `CWorldPhysicsManager__ResolveLoadedDefinitionReferences` is the static handoff for loaded definition references after parse. |
| InitThing factory | `0x0048c650 InitThing__CreateThingByType`, `0x0040e280 CInitThing__LoadFromMemBuffer`, and `0x0048dcf0 CInitThing__ctor` are static init-object creation/load anchors for later world/object-reference proof. |
| Thing render/resource init | `CThing__InitRenderThingFromInitMeshName` ties thing lifecycle to mesh/resource initialization. |
| Occupancy setup | `CWorld__InitOccupancyBitplanes` and `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk` are world occupancy/static shadow handoff anchors. |
| Unit init handoff | `CUnit__VFunc08_InitAndAddToWorld` is the Unit/BattleEngine side of a spawn/init world-add bridge. |
| Spawner behavior shell | `0x004e3010 CSpawnerThng__Init`, `0x004e36c0 CSpawnerThng__FindSpawnerByName`, `0x004e3c60 CSpawnerThng__DoSpawn`, `0x004e3f90 CSpawnerThng__ProcessSpawnWave`, `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed`, and `0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName` define the static spawner shell for later proof. |
| Spawn cooldown | `CUnit__SetSpawnCooldownState3` is the static post-spawn cooldown state handoff. |

## Static Field Roles To Preserve

These are static role labels for proof planning. Do not promote them to final C++ field names until exact layout proof exists.

| Offset / slot | Planned role in later proof |
| --- | --- |
| `script_state+0x218` | MissionScript VM state role retained from MissionScript/IScript proof planning. |
| `script_object_code+0x68` | Object-code execution role retained from MissionScript/IScript proof planning. |
| CWorld load buffers | World file / script-event parse state; exact fields remain open. |
| CWorld occupancy bitplanes | World occupancy and static-shadow handoff role. |
| CWorldPhysicsManager definition lists | Loaded definition reference and factory lookup role. |
| CThing render mesh name | Mesh/resource initialization bridge role. |
| CSpawnerThng type/config state | Spawn type allowlist, spawn wave, and object creation role. |
| CUnit world-add handoff | Unit init, occupancy insertion, and shadow rebuild role. |
| CUnit spawn cooldown state | Post-spawn cooldown/activation state role. |

## Future Proof Checklist

The first executable or corpus proof after this plan should be scoped and copied/app-owned only. This plan records the expected evidence shape; it does not run that proof.

| Row | Planned proof item | Required evidence | Public-safe result |
| --- | --- | --- | --- |
| 1 | Select one object-reference family | Choose one copied corpus level/file set with concrete `GetThingRef` or `SpawnThing` entries from `mission-thing-usage.md`. | Sanitized level/file/thing/spawner label and reason for selection. |
| 2 | Preserve corpus names | Preserve exact level directory, script file, thing name, spawner name, casing, and duplicate call counts. | Public-safe aggregate/case-preservation checklist. |
| 3 | Static command handoff | Tie the selected corpus command to `IScript__GetThingRef` or `IScript__SpawnThing` static anchors without claiming runtime execution. | Command-to-handler checklist. |
| 4 | Bytecode pre-scan handoff | Tie `SpawnThing` corpus rows to `CScriptObjectCode__CollectSpawnThings`, opcode `0x18`, and `CWorldMeshList__Add` as static preload/dependency evidence only. | SpawnThing pre-scan checklist, no live script execution claim. |
| 5 | World-load dependency map | Identify which world-load/static factory anchors are required before runtime proof: `CWorld__LoadWorld`, `CWorld__LoadScriptEvents`, `CWorld__LoadWorldFile`, `CWorldMeshList__Add`, `CWorld__SpawnInitialThings`, `InitThing__CreateThingByType`, and `CWorldPhysicsManager__CreateThingByType`. | Static dependency table with unknown layouts marked. |
| 6 | Spawner path map | If the selected case uses `SpawnThing`, map `CSpawnerThng__Init`, `CSpawnerThng__FindSpawnerByName`, `CSpawnerThng__DoSpawn`, `CSpawnerThng__ProcessSpawnWave`, `CSpawnerThng__IsSpawnTypeAllowed`, `CWorldPhysicsManager__CreateSpawner`, `CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName`, `CWorldPhysicsManager__MapGunOrSpawnerTagToIndex`, `CWorldPhysicsManager__AddSpawnerByName`, `DAT_008553f4`, `CUnit__VFunc08_InitAndAddToWorld`, and `CUnit__SetSpawnCooldownState3` as needed. | Spawn path checklist, no runtime spawn claim; completed for the selected training-target family by `world-thing-spawn-spawner-handoff-static-proof.md`. |
| 7 | Object identity boundary | Define what would count as runtime object identity proof later, while keeping this slice static-only. | Stop-condition row for ambiguous names, duplicate names, missing spawners, or packed-vs-loose selection uncertainty. |
| 8 | Mesh/resource bridge | If the selected object has mesh/resource evidence, link `CThing__InitRenderThingFromInitMeshName`, mesh/resource contracts, and AYA/export docs without claiming render output. | Static mesh/resource dependency note. |
| 9 | Runtime separation | Keep mission outcome, AI behavior, spawn side effects, HUD/message/audio output, collision, damage, and visual output outside this slice. | Explicit deferred rows. |
| 10 | Rebuild handoff | Translate the proven static-only bridge into clean-room object-reference/spawn pseudocode only after later proof identifies what was observed. | Static pseudocode with runtime/layout gaps marked. |

## Copied/App-Owned Guardrails

Any later proof execution must:

- Use copied profiles, copied mission scripts, copied resources, copied saves/options, or app-owned artifact roots only.
- Use copied/app-owned only, no runtime object identity claim until a later proof slice selects and observes a bounded target.
- Never mutate the installed Steam game directory or original executable.
- Preserve loose mission-script casing, path spelling, duplicate rows, thing names, and spawner names when building copied-corpus artifacts.
- Record whether a script input is loose copied retail data, packed resource data, a sanitized fixture, or generated app-owned data.
- Keep runtime mission loading, object identity, spawn behavior, AI behavior, collision, damage, input, audio/message/HUD output, and gameplay outcomes as separate claim lanes.
- Keep public notes aggregate and sanitized; do not leak private paths, private assets, memory dumps, or operator-only evidence.
- Stop if proof requires broad mission simulation before the selected child lane is explicit.

## Not Claimed

This plan is a static-to-proof planning artifact only. It does not prove:

- Runtime MissionScript execution.
- Runtime `GetThingRef` behavior.
- Runtime `SpawnThing` behavior.
- Runtime world loading behavior.
- Runtime object identity.
- Runtime object lookup by name.
- Runtime spawner behavior.
- Runtime Unit/BattleEngine spawn behavior.
- Runtime AI activation, pathing, collision, damage, objective, message, HUD, audio, camera, or gameplay outcomes.
- Live loose-MSL loading or packed-resource script selection.
- Exact `IScript__GetThingRef` or `IScript__SpawnThing` handler address proof beyond named command/contract anchors.
- Exact MissionScript descriptor, VM, datatype, opcode, value, stack, object-code, event, world, thing, spawner, Unit, CWorldPhysicsManager, mesh/resource, or object-reference layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Exit Gate For This Planning Slice

This planning slice is complete only when:

- This document and its lore-book mirror match.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `reverse-engineering/binary-analysis/_index.md`, and `reverse-engineering/RE-INDEX.md` point to this plan as complete, to `world-thing-spawn-copied-corpus-schema-proof-plan.md` / `world-thing-spawn-copied-corpus-schema-proof.md` as the completed copied-corpus schema child lane, to `world-thing-spawn-spawner-handoff-static-proof.md` as the completed static spawner handoff child lane, and to `world-thing-spawn-getthingref-object-reference-static-proof.md` as the completed static GetThingRef object-reference child lane.
- MissionScript, MSL, world/mesh, and Unit/BattleEngine source docs point to this plan without changing their static claim boundaries.
- `release/readiness/world_thing_spawn_object_reference_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/world_thing_spawn_object_reference_proof_plan_probe.py --check` passes.
- Static closeout probes still pass without changing `static-reaudit-progress.json` or `static-reaudit-current-risk-ledger.json`.
