# WorldPhysicsManager.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x0042f5f0` → `WeaponDefinition__CreateAndRegisterByName` (was `CWeapon__CreateAndRegisterByName`); `0x004309e0` → `ExplosionDefinition__CreateAndRegisterByName` (was `CExplosion__CreateAndRegisterByName`); `0x004d8410` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

**Source File:** `[maintainer-local-source-export-root]\WorldPhysicsManager.cpp`
**Debug String Address:** `0x0063d798`

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6246/6246** (Wave1073: every exported function commented with clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

WorldPhysicsManager handles entity creation and management for the game's physics simulation. This includes creating various game objects like vehicles, weapons, projectiles, characters, and managing their lifecycle through linked lists.

Wave905 static review (`mesh-motion-world-particle-static-review-wave905`) records a `static-coherent mesh/motion/world/particle core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only): `506` rows across `41` families, including `CMeshPart` `54`, `CMesh` `40`, `CWorld` `38`, `CWorldPhysicsManager` `32`, `CThing` `28`, `CParticleManager` `23`, and `CMeshCollisionVolume` `21`; anchors include `CThing__InitRenderThingFromInitMeshName`, `CMesh__LoadByNameWithStatus`, `CMeshPart__PopulatePoseCacheRecursive`, `CWorld__InitOccupancyBitplanes`, `CWorldPhysicsManager__CreateThingByType`, `CParticleManager__Update`, `CParticleSet__LoadFromArchive`, and `CParticleDescriptor__Load`; mesh bridge counts include `213/213` loose meshes, `139/139` embedded meshes, and `352/352` model material/texture-binding rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`.

Wave1073 static re-audit (cworld-load-tail-review-wave1073) re-read `0x0050df80 CWorldPhysicsManager__CreateThingByType` with no mutation, alongside context rows including `0x0050f4b0 CWorldPhysicsManager__CreateSquad`, `0x00510060 CWorldPhysicsManager__CreateEffect`, and `0x00510150 CWorldPhysicsManager__CreateTrigger`. Fresh xrefs keep CreateThingByType tied to `CWorld__LoadWorld`, `CWorld__SpawnInitialThings`, `CSpawnerThng__ProcessSpawnWave`, `CSquad__Init`, `CWingmanStart__VFunc_09_0050a3a0`, and raw script/create neighborhoods. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified`. Runtime spawn/factory behavior, exact definition-type enum/layout identity, raw-boundary identities, and rebuild parity remain separate proof. Probe token anchor: Wave1073; cworld-load-tail-review-wave1073; 0x0050a870 CWorld__ClearSetArrays; 0x0050ac70 CWorld__LoadScriptEvents; 0x0050b520 CWorld__LoadWorldFile; 0x0050d6a0 CWorld__PushWorldTextSlot; 0x0050d9e0 CWorldMeshList__Add; 0x0050dcb0 CWorld__SpawnInitialThings; 0x0050df80 CWorldPhysicsManager__CreateThingByType; 0x00537c40; 0x004dfa47; 812/1408 = 57.67%; 1357/1560 = 86.99%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified; read-only review.

Wave846 WorldPhysics load/resolve note: `0x00510520 CWorldPhysicsManager__ResolveLoadedDefinitionReferences`, `0x00510740 CWorldPhysicsManager__FreeNestedThingSets_6C`, `0x00510800 CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData`, and `0x00510a90 CWorldPhysicsManager__ClearAndFreeAllDefinitionLists` are now saved as no-argument `void __cdecl ... (void)` signatures with the `worldphysics-load-resolve-wave846` and `wave846-readback-verified` tags. Static evidence ties the four rows to caller sites `0x0046cdd7`, `0x0046cc61`, `0x004f0092`, `0x004f00e0`, and reload-internal call `0x0051081e`; definition-list globals `DAT_008553e8` through `DAT_00855408`; `DAT_006602a0`; `data/default_physics.dat`; and `data/battle_engine_configuration`. Post-Wave846 strict proxy is `5673/6098 = 93.03%`; next raw commentless row is `0x00512040 CLTShell__InitUnhandledExceptionLogFile`; verified backup is `[maintainer-local-ghidra-backup-root]\BEA_20260525-060333_post_wave846_worldphysics_load_resolve_verified`. Exact source method identity, exact definition-list/entry/`CBattleEngineData` schemas, runtime load/resolve/shutdown/reload behavior, BEA patching, and rebuild parity remain deferred.

Wave845 CSpawner Type Allowed note: related spawner predicate `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed` is now saved as `bool __cdecl CSpawnerThng__IsSpawnTypeAllowed(int spawn_type)` with the `spawner-type-allowed-wave845` and `wave845-readback-verified` tags. This complements the later name-based allowlist `0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName`: `CSpawnerThng__Init` at `0x004e32cc` and `CSpawnerThng__Constructor` at `0x004e39b2` both push the definition type enum from `+0xe0`, call the compact predicate, and test `EAX`; the predicate dispatches through `0x0050f6a4/0x0050f6ac`, returns false for `4 through 0x14 and 0x16 through 0x18`, and leaves the next raw commentless row at `0x00510520 CWorldPhysicsManager__ResolveLoadedDefinitionReferences`. Post-Wave845 strict proxy is `5669/6098 = 92.96%`; verified backup is `[maintainer-local-ghidra-backup-root]\BEA_20260525-053251_post_wave845_spawner_type_allowed_verified`. Exact enum names, source method identity, concrete spawner/definition field meanings, runtime spawn admission behavior, BEA patching, and rebuild parity remain deferred.

Wave941 missile linked-object dispatch note: `missile-linked-object-dispatch-review-wave941` re-reviewed the projectile factory/missile lifecycle join around `0x0050f7a0 CWorldPhysicsManager__CreateProjectile`, `0x004baae0 CMissile__Init`, `0x004bac10 CMissile__DispatchLinkedObjectVFunc68AndPostHook`, `0x0050f8b0 CMissile__scalar_deleting_dtor`, `0x0050f8d0 CMissile__Destructor`, `0x004d8410 CRound__Init`, and `0x00452da0 SharedVFunc__NoOp_Ret08`. Vtable anchors `0x005e3ba4`, `0x005e3ba8`, `0x005e3bc8`, `0x005e3cb8`, `0x005e3cc0`, `0x005de82c`, and `0x005de850` preserve the missile-style projectile path and CRound base join. The review was read-only: no mutation, no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change. Wave911 focused re-audit progress after Wave941 is `179/1408 = 12.71%`; export-contract closure remains `6113/6113 = 100.00%`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260528-034712_post_wave941_missile_linked_object_dispatch_review_verified`.

Probe token anchor: Wave941; `missile-linked-object-dispatch-review-wave941`; `0x004baae0 CMissile__Init`; `0x004bac10 CMissile__DispatchLinkedObjectVFunc68AndPostHook`; `0x0050f8b0 CMissile__scalar_deleting_dtor`; `0x0050f8d0 CMissile__Destructor`; `0x0050f7a0 CWorldPhysicsManager__CreateProjectile`; `0x004d8410 CRound__Init`; `0x00452da0 SharedVFunc__NoOp_Ret08`; `0x005e3ba4`; `0x005e3ba8`; `0x005e3bc8`; `0x005e3cb8`; `0x005e3cc0`; `0x005de82c`; `0x005de850`; read-only review; `179/1408 = 12.71%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-034712_post_wave941_missile_linked_object_dispatch_review_verified`.

## Functions (69 total)

| Address | Name | Purpose |
|---------|------|---------|
| `0x00505e00` | `CWeapon__ctor_base` | Weapon constructor body called by `CWorldPhysicsManager__CreateWeaponByIndex` |
| `0x00505f90` | `CWeapon__DetachFromSetAndShutdownMonitor` | Weapon teardown helper called by `CWeapon__scalar_deleting_dtor` |
| `0x0050df80` | `CWorldPhysicsManager__CreateThingByType` | Factory method - creates physics objects by type enum |
| `0x0050ed60` | `CBomber__scalar_deleting_dtor` | Wave557 CBomber primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050ed80` | `CBigAirUnit__ctor_base` | Wave557 big-air-unit constructor-base helper called by `CWorldPhysicsManager__CreateThingByType` |
| `0x0050ee10` | `CGroundAttackAircraft__scalar_deleting_dtor` | Wave557 ground-attack-aircraft primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050ee30` | `CInfantryUnit__scalar_deleting_dtor` | Wave557 infantry-unit primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050ee50` | `CCarrier__scalar_deleting_dtor` | Wave557 carrier primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050ee70` | `CDropship__scalar_deleting_dtor` | Wave557 dropship primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050eeb0` | `CPlane__scalar_deleting_dtor` | Wave557 plane primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050eed0` | `CDiveBomber__scalar_deleting_dtor` | Wave557 dive-bomber primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050eef0` | `CCarver__scalar_deleting_dtor` | Wave557 Carver primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050ef10` | `CFenrir__scalar_deleting_dtor` | Wave557 Fenrir primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050ef30` | `CCarrier__Destructor` | Wave557 carrier destructor body used by `CCarrier__scalar_deleting_dtor` |
| `0x0050efa0` | `CBomber__ClearPtrSetsRemoveFromGlobalListAndDestruct` | Wave557 CBomber destructor body used by `CBomber__scalar_deleting_dtor` |
| `0x0050f010` | `CBigAirUnit__scalar_deleting_dtor` | Wave557 big-air-unit primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050f030` | `CBigAirUnit__Destructor` | Wave557 big-air-unit destructor body used by `CBigAirUnit__scalar_deleting_dtor` |
| `0x0050f0a0` | `CAirUnit__ctor_base` | Wave557 aircraft constructor-base helper called by multiple factory variants |
| `0x0050f130` | `CGroundAttackAircraft__Destructor_VFunc01` | Wave557 ground-attack-aircraft destructor body used by its scalar-deleting wrapper |
| `0x0050f1a0` | `CInfantryUnit__Destructor_VFunc01` | Wave557 infantry-unit destructor body used by its scalar-deleting wrapper |
| `0x0050f1f0` | `CDropship__Destructor_VFunc01` | Wave557 dropship destructor body used by its scalar-deleting wrapper |
| `0x0050f260` | `CPlane__Destructor_VFunc01` | Wave557 plane destructor body used by its scalar-deleting wrapper |
| `0x0050f2d0` | `CDiveBomber__Destructor_VFunc01` | Wave557 dive-bomber destructor body used by its scalar-deleting wrapper |
| `0x0050f340` | `CCarver__Destructor_VFunc01` | Wave557 Carver destructor body used by its scalar-deleting wrapper |
| `0x0050f3b0` | `CFenrir__Destructor_VFunc01` | Wave557 Fenrir destructor body used by its scalar-deleting wrapper |
| `0x0050f420` | `CAirUnit__scalar_deleting_dtor` | Wave557 CAirUnit base vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050f440` | `CAirUnit__ClearPtrSetsRemoveFromGlobalListAndDestruct` | Wave557 CAirUnit destructor body used by `CAirUnit__scalar_deleting_dtor` |
| `0x0050f4b0` | `CWorldPhysicsManager__CreateSquad` | Wave557 one-argument squad factory signature; creates relaxed/normal squad objects by `squad_type` |
| `0x0050f610` | `CRelaxedSquad__scalar_deleting_dtor` | Wave558 relaxed-squad primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050f630` | `CRelaxedSquad__Destructor` | Wave558 relaxed-squad destructor body used by `CRelaxedSquad__scalar_deleting_dtor` |
| `0x0050f6d0` | `CWorldPhysicsManager__CreateWeaponByIndex` | Wave558 two-argument weapon factory: `weapon_index`, `create_context` |
| `0x0050f7a0` | `CWorldPhysicsManager__CreateProjectile` | Wave558 one-definition projectile/round factory |
| `0x0050f8b0` | `CMissile__scalar_deleting_dtor` | Wave558 missile primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050f8d0` | `CMissile__Destructor` | Wave558 missile destructor body used by `CMissile__scalar_deleting_dtor` |
| `0x0050f970` | `CWorldPhysicsManager__CreateSpawner` | Wave558 two-argument spawner factory: `spawner_index`, `spawn_context` |
| `0x0050fa40` | `CWorldPhysicsManager__CreateCharacter` | Wave558 one-argument component/character factory, including `Gill_M_Head` special case |
| `0x0050fd30` | `CGillMHead__scalar_deleting_dtor` | Wave558 GillMHead primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050fd50` | `CTentacle__scalar_deleting_dtor` | Wave558 tentacle primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050fd70` | `CComponent__scalar_deleting_dtor` | Wave558 component primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050fd90` | `CComponent__Destructor` | Wave558 component destructor body used by `CComponent__scalar_deleting_dtor` |
| `0x0050fe10` | `CGillMHead__Destructor_VFunc01` | Wave558 GillMHead slot-1 destructor body used by `CGillMHead__scalar_deleting_dtor` |
| `0x0050fe90` | `CTentacle__Destructor` | Wave558 tentacle destructor body used by `CTentacle__scalar_deleting_dtor` |
| `0x0050ff10` | `CWorldPhysicsManager__CreatePickup` | Wave558 one-argument pickup factory |
| `0x0050ffd0` | `CExplosion__scalar_deleting_dtor` | Wave558 explosion primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x0050fff0` | `CExplosion__Destructor` | Wave558 explosion destructor body used by `CExplosion__scalar_deleting_dtor` |
| `0x00510060` | `CWorldPhysicsManager__CreateEffect` | Wave558 one-argument visual-effect factory |
| `0x00510150` | `CWorldPhysicsManager__CreateTrigger` | Wave558 one-argument trigger-zone factory |
| `0x00510230` | `CHazard__scalar_deleting_dtor` | Wave558 hazard primary vtable slot-1 scalar-deleting destructor wrapper |
| `0x00510250` | `CHazard__Destructor` | Wave558 hazard destructor body used by `CHazard__scalar_deleting_dtor` |
| `0x005102a0` | `CWorldPhysicsManager__InitializeLists` | Wave558 no-argument initializer for nine 0x10 CSPtrSet definition lists |
| `0x00510520` | `CWorldPhysicsManager__ResolveLoadedDefinitionReferences` | Wave846 `void __cdecl` post-load reference resolver for loaded definition lists |
| `0x00510740` | `CWorldPhysicsManager__FreeNestedThingSets_6C` | Wave846 `void __cdecl` nested `+0x6c` set drain for thing/component definitions |
| `0x00510800` | `CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData` | Wave846 `void __cdecl` reload path for `data/default_physics.dat` and `data/battle_engine_configuration` |
| `0x00510a90` | `CWorldPhysicsManager__ClearAndFreeAllDefinitionLists` | Wave846 `void __cdecl` global definition-list and BattleEngineData teardown |
| `0x00510e60` | `CWorldPhysicsManager__FreeEntryOwnedPtrs_00_0C_20` | Frees/zeroes three owned pointers at offsets `+0x00`, `+0x0C`, and `+0x20` |
| `0x00510eb0` | `CWorldPhysicsManager__FreeRoundStatement` | Frees one round-statement entry and owned pointers |
| `0x00510f10` | `CWorldPhysicsManager__FreeWeaponModeStatement` | Frees one weapon-mode statement entry (including embedded sets) |
| `0x00511040` | `CWorldPhysicsManager__FreeWeaponStatement` | Frees one weapon-statement entry |
| `0x00511070` | `CWorldPhysicsManager__FreeTagDefinitionEntry` | Frees one DAT_008553f8 tag-definition entry |
| `0x005110f0` | `CWorldPhysicsManager__FreeThingOrComponentDefinitionEntry` | Frees one thing/component definition entry |
| `0x005113a0` | `CWorldPhysicsManager__ClearEntryWorkSets_40_50` | Clears embedded work sets on definition nodes (`+0x40`/`+0x50`) |
| `0x00511440` | `CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName` | Name-based allowlist gate used by `CSpawnerThng__ProcessSpawnWave` before spawn |
| `0x005115b0` | `CWorldPhysicsManager__MapGunOrSpawnerTagToIndex` | Maps `GunA..GunI` and `SpawnerA..SpawnerE` tags to compact IDs |
| `0x00511720` | `CWorldPhysicsManager__ResolveTagListNameToIndex_E8` | Resolves DAT_008553f8 name to index and stores at field `+0xE8` |
| `0x005117c0` | `CWorldPhysicsManager__ResolveTagListNameToIndex_EC` | Resolves DAT_008553f8 name to index and stores at field `+0xEC` |
| `0x00511860` | `CWorldPhysicsManager__ResolveTagListNameToIndex_F0` | Resolves DAT_008553f8 name to index and stores at field `+0xF0` |
| `0x00511900` | `CWorldPhysicsManager__AddComponentByName` | Adds component to list by name lookup |
| `0x005119e0` | `CWorldPhysicsManager__AddWeaponByName` | Adds weapon to list by name lookup |
| `0x00511ad0` | `CWorldPhysicsManager__AddSpawnerByName` | Adds spawner to list by name lookup |

## Wave747 WorldPhysicsManager.h unwind continuation callbacks

Wave747 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the WorldPhysicsManager/CPhysicsScript-adjacent cleanup callbacks at `0x005d1cd9 Unwind@005d1cd9`, `0x005d1ce4 Unwind@005d1ce4`, `0x005d1d20 Unwind@005d1d20`, `0x005d1d70 Unwind@005d1d70`, `0x005d1dc0 Unwind@005d1dc0`, `0x005d1e10 Unwind@005d1e10`, `0x005d1e29 Unwind@005d1e29`, `0x005d1e34 Unwind@005d1e34`, `0x005d1e3f Unwind@005d1e3f`, `0x005d1e4a Unwind@005d1e4a`, `0x005d1e80 Unwind@005d1e80`, and `0x005d1ed0 Unwind@005d1ed0`. The free-object rows use WorldPhysicsManager.h debug path `0x00625850`, lines `0xe`, `0x3e`, `0x3f`, `0x40`, and `0x41`, memtypes `0x94e`, `0x963`, `0x96a`, `0x978`, `0x97f`, and `0x986`, with DATA scope-table xrefs `0x0061ab94`, `0x0061abe4`, `0x0061ac34`, `0x0061ac84`, `0x0061acf4`, and `0x0061ad44`; the embedded-set rows call `CSPtrSet__Clear` on fields `+0x3c`, `+0x4c`, `+0x5c`, and `+0x6c`.

The same `unwind-continuation-wave747` tranche spans `0x005d1cd9 Unwind@005d1cd9` through `0x005d1fc0 Unwind@005d1fc0`, uses the `wave747-readback-verified` tag, and has verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260522-180520_post_wave747_unwind_continuation_verified`. The next high-signal queue head is `0x005d1fc8 Unwind@005d1fc8`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`. Exact parent source-body identity, runtime world-physics cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave746 WorldPhysicsManager.h unwind continuation callbacks

Wave746 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the WorldPhysicsManager/CPhysicsScript-adjacent cleanup callbacks at `0x005d1c00 Unwind@005d1c00`, `0x005d1c19 Unwind@005d1c19`, `0x005d1c24 Unwind@005d1c24`, `0x005d1c2f Unwind@005d1c2f`, `0x005d1c3a Unwind@005d1c3a`, `0x005d1c70 Unwind@005d1c70`, and `0x005d1cc0 Unwind@005d1cc0`. The free-object rows use WorldPhysicsManager.h debug path `0x00625850`, lines `0xf`, `0x3d`, and `0x3c`, memtypes `0x971`, `0x95c`, and `0x955`, with DATA scope-table xrefs `0x0061aa74`, `0x0061aae4`, and `0x0061ab34`; the embedded-set rows call `CSPtrSet__Clear` on fields `+0x3c`, `+0x4c`, `+0x5c`, and `+0x6c`.

The same `unwind-continuation-wave746` tranche spans `0x005d1aa3 Unwind@005d1aa3` through `0x005d1cc0 Unwind@005d1cc0`, uses the `wave746-readback-verified` tag, and has verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260522-173500_post_wave746_unwind_continuation_verified`. The next high-signal queue head is `0x005d1cd9 Unwind@005d1cd9`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`. Exact parent source-body identity, runtime world-physics cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Function Details

### CWorldPhysicsManager__CreateThingByType (0x0050df80)

Wave556 saved this as:

```c
void * __cdecl CWorldPhysicsManager__CreateThingByType(int thing_type_index)
```

The saved signature is based on callsites in `CWorld__LoadWorld`, `CWorld__SpawnInitialThings`, `CSpawnerThng`, `CSquad`, and script/create paths that pass one definition index. The body walks the thing-definition list at `DAT_008553fc` to the requested index, switches on the definition type enum at offset `+0xe0`, allocates the matching runtime object, installs class vtables, and returns the created object or null on heap/type failure.

This is static retail-binary evidence only. Exact type enum names, object layouts, constructor side effects, runtime spawn behavior, BEA launch, patching, and rebuild parity remain unproven.

Large factory function with a switch statement handling ~26 different entity types (cases 0-25). Creates various physics objects based on type enum stored at offset `+0xe0` of the input object. Each case allocates memory via `OID__AllocObject`, initializes the object, and sets up vtable pointers.

**Type mapping (partial):**
- Case 0: Basic physics thing (size 0x26c)
- Case 1, 8: Large physics objects (size 0x288)
- Case 2: Medium object (size 0x264)
- Case 3: Object with kill tracking (size 0x278)
- Case 9: Movable object (size 0x27c)
- Case 10: Complex object (size 0x288)
- ...

**Heap check:** Only runs if `DAT_009c51f0 > 0x27ff` (heap has sufficient space)

### CWorldPhysicsManager__CreateSquad (0x0050f4b0)

Wave557 saved this as:

```c
void * __cdecl CWorldPhysicsManager__CreateSquad(int squad_type)
```

Creates squad AI objects based on one squad type parameter:
- Types 0, 3: Creates relaxed squad (size 0xb4)
- Other types: Creates normal squad (size 0x144) via `CSquadNormal__Constructor`

Shows "Thing heap full" error if heap exhausted.

Static evidence: `CWorld__LoadWorld` and `CSpawnerThng__Update` callsites pass one stack value; the body switches on `squad_type`, allocates either a `0xb4` CSquad-style object or a `0x144` CSquadNormal object, and returns null on heap/type rejects. Exact enum names, concrete squad layouts, runtime squad behavior, BEA launch, patching, and rebuild parity remain unproven.

### WorldPhysicsManager Factory Tail / Lifecycle Cluster (0x0050f610 - 0x005102a0)

Wave558 hardened 22 adjacent targets after the squad factory. The seven primary vtable slot-1 wrappers now use scalar-deleting destructor names and delete-flag signatures:

- `CRelaxedSquad__scalar_deleting_dtor`
- `CMissile__scalar_deleting_dtor`
- `CGillMHead__scalar_deleting_dtor`
- `CTentacle__scalar_deleting_dtor`
- `CComponent__scalar_deleting_dtor`
- `CExplosion__scalar_deleting_dtor`
- `CHazard__scalar_deleting_dtor`

The saved factory signatures are:

```c
void * __cdecl CWorldPhysicsManager__CreateWeaponByIndex(int weapon_index, int create_context)
void * __cdecl CWorldPhysicsManager__CreateProjectile(void * round_definition)
void * __cdecl CWorldPhysicsManager__CreateSpawner(int spawner_index, void * spawn_context)
void * __cdecl CWorldPhysicsManager__CreateCharacter(int component_index)
void * __cdecl CWorldPhysicsManager__CreatePickup(int pickup_type)
void * __cdecl CWorldPhysicsManager__CreateEffect(int effect_type)
void * __cdecl CWorldPhysicsManager__CreateTrigger(int trigger_type)
void __cdecl CWorldPhysicsManager__InitializeLists(void)
```

Static evidence: xrefs show weapon creation from `CUnit__Init` and BattleEngine reset paths, projectile creation from `ProjectileBurst__SpawnFromCurrentPreset` and `CRound__SpawnConfiguredProjectile`, spawner/character creation from `CUnit__Init`, pickup creation from unit/volume/feature/projectile paths, effect/trigger creation from `CWorld__LoadWorld`, and list initialization from `CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData`. `InitializeLists` allocates nine 0x10 CSPtrSet containers and stores them in `DAT_008553e8` through `DAT_00855408`.

This is static retail-binary evidence only. Exact definition schemas, concrete object layouts, source method identities, runtime factory behavior, BEA launch, patching, and rebuild parity remain unproven.

### WorldPhysicsManager Cleanup / Resolve / Add-By-Name Cluster (0x00510e60 - 0x00511ad0)

Wave559 hardened the WorldPhysicsManager cleanup/resolve tranche: 15 adjacent cleanup, resolve, and add-by-name targets after the definition-list reload/teardown path. The first seven helpers are per-entry cleanup routines called by `CWorldPhysicsManager__ClearAndFreeAllDefinitionLists` after list unlink:

- `CWorldPhysicsManager__FreeEntryOwnedPtrs_00_0C_20`
- `CWorldPhysicsManager__FreeRoundStatement`
- `CWorldPhysicsManager__FreeWeaponModeStatement`
- `CWorldPhysicsManager__FreeWeaponStatement`
- `CWorldPhysicsManager__FreeTagDefinitionEntry`
- `CWorldPhysicsManager__FreeThingOrComponentDefinitionEntry`
- `CWorldPhysicsManager__ClearEntryWorkSets_40_50`

Wave559 also recovered the string/tag signatures:

```c
int __cdecl CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName(char * thing_name)
int __cdecl CWorldPhysicsManager__MapGunOrSpawnerTagToIndex(char * tag_name)
void __thiscall CWorldPhysicsManager__ResolveTagListNameToIndex_E8(void * this, char * tag_name)
void __thiscall CWorldPhysicsManager__ResolveTagListNameToIndex_EC(void * this, char * tag_name)
void __thiscall CWorldPhysicsManager__ResolveTagListNameToIndex_F0(void * this, char * tag_name)
void __thiscall CWorldPhysicsManager__AddComponentByName(void * this, int link_value, char * component_name)
void __thiscall CWorldPhysicsManager__AddWeaponByName(void * this, char * weapon_name, char * tag_name, int link_value)
void __thiscall CWorldPhysicsManager__AddSpawnerByName(void * this, char * spawner_name, char * tag_name, int link_value)
```

Static evidence: focused callsite instructions show the three `ResolveTagListNameToIndex_*` helpers receive one stack name pointer plus ECX destination object, so the previous extra Ghidra stack parameter was phantom. `AddComponentByName` appends an 8-byte index/link record to `this+0x5c`; `AddWeaponByName` and `AddSpawnerByName` append 0x0c-byte records to `this+0x3c` and `this+0x4c` after mapping `GunA..GunI` / `SpawnerA..SpawnerE` tags through `CWorldPhysicsManager__MapGunOrSpawnerTagToIndex`.

This is static retail-binary evidence only. Exact definition schemas, concrete owner/list layouts, source method identities, runtime cleanup/resolve/add-by-name behavior, BEA launch, patching, and rebuild parity remain unproven.

### Air-Unit Lifecycle Cluster (0x0050ed60 - 0x0050f440)

Wave557 hardened a 25-target adjacent lifecycle/factory tranche. The scalar-deleting destructor wrappers at `0x0050ed60`, `0x0050ee10`, `0x0050ee30`, `0x0050ee50`, `0x0050ee70`, `0x0050eeb0`, `0x0050eed0`, `0x0050eef0`, `0x0050ef10`, `0x0050f010`, and `0x0050f420` are backed by primary vtable slot-1 read-back and `RET 0x4` delete-flag cleanup. The destructor bodies clear owned pointer sets and remove global-list nodes before tailing into `CUnit__dtor_base`; the infantry body uses the observed `this+0x270` list node rather than the aircraft `this+0x250` plus pointer-set pair.

The constructor-base helpers `CBigAirUnit__ctor_base` and `CAirUnit__ctor_base` are called from `CWorldPhysicsManager__CreateThingByType`, call `CUnit__ctor_base`, initialize global-list/pointer-set state, install their class tables, and return `this`. These are static retail-binary facts only; exact source constructor/destructor names, class layouts, runtime spawn/destruction behavior, BEA launch, patching, and rebuild parity remain unproven.

### CWorldPhysicsManager__CreateWeaponByIndex (0x0050f6d0)

Iterates through weapon list at `DAT_008553e8`, finds weapon at specified index, allocates memory (size 0xb0), and initializes weapon object via `CWeapon__ctor_base`.

### CWeapon__ctor_base (0x00505e00)

Wave550 corrected the old `CEquipment__ctor_like_00505e00` label to `void * __thiscall CWeapon__ctor_base(void * this, void * weapon_data, int create_context)`. `CreateWeaponByIndex` pushes the caller context/type value and selected weapon data, moves the allocation into `ECX`, and calls this constructor; `RET 0x8` proves two explicit stack arguments after `this`.

Static evidence: the body installs transient table `0x005d8824`, then CWeapon table `0x005dfc94`, initializes the embedded two-node array at `+0x14`, stores `weapon_data` at `+0xa4`, stores the second caller value at `+0xa8`, seeds a zero-Euler `Mat34` into `+0x30`, initializes distance/profile state, selects an initial `DAT_008553ec` profile entry through the weapon data table, and returns `this`.

This is static constructor evidence only. Exact source constructor name, concrete `CWeapon`/`CEquipment` layout, runtime weapon behavior, and rebuild parity remain unproven.

### CWeapon__DetachFromSetAndShutdownMonitor (0x00505f90)

Wave550 hardened this helper to `void __fastcall CWeapon__DetachFromSetAndShutdownMonitor(void * this)`. It is called by `CWeapon__scalar_deleting_dtor`; the body checks the embedded set/list cell at `+0x2c`, removes `this+0x2c` from its owner set when linked, destroys the two `+0x14` global-list nodes with `CParticleManager__RemoveFromGlobalList_Thunk`, then calls `CMonitor__Shutdown(this)`.

This is static teardown evidence only. Complete destructor side effects, concrete layout, runtime teardown behavior, and rebuild parity remain unproven.

### CWeapon__AdvanceChargeProgressIfAnySlotAssigned (0x005068f0)

Wave552 corrected the stale `CEngine__AdvanceProgressIfAnySlotAssigned` label to `void __fastcall CWeapon__AdvanceChargeProgressIfAnySlotAssigned(void * weapon)`. The checked callers are `CGeneralVolume__DispatchMode3BurstProgressAndSpawn` and `CBattleEngineWalkerPart__ChargeWeapon`; both pass the current weapon/current-entry pointer in `ECX`.

Static evidence: the body loads `weapon +0xa4` weapon-data, scans assigned-slot dwords at `+0x10..+0x1c` for any value other than `-1`, and when `weapon +0x60` is below `DAT_005db358`, adds `weapon-data +0x08` into `weapon +0x60`.

Wave1027 (`battleengine-walkerpart-weapon-spine-review-wave1027`) re-read `0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned` and `0x00506930 CWeapon__HandleFireBurstEvent` as WalkerPart weapon-spine context with no mutation. The pass tied those CWeapon context rows to `0x00413cf0 CBattleEngineWalkerPart__ChargeWeapon`, `0x00413cc0 CBattleEngineWalkerPart__FireWeapon`, `0x00414030 CBattleEngineWalkerPart__GetCurrentWeapon`, `0x004140d0 CBattleEngineWalkerPart__WeaponFired`, and `0x004145f0 CBattleEngineWalkerPart__GetCurrentWeaponZoomMode`; queue closure remains `6238/6238 = 100.00%`, Wave911 focused progress is `600/1408 = 42.61%`, expanded static surface progress is `829/1493 = 55.53%`, and verified backup is `[maintainer-local-ghidra-backup-root]\BEA_20260601-014543_post_wave1027_battleengine_walkerpart_weapon_spine_review_verified`.

This is static retail evidence only. Exact source method identity, concrete `CWeapon`/weapon-data layout, runtime charge/fire behavior, stealth behavior, and rebuild parity remain unproven.

### CWorldPhysicsManager__CreateProjectile (0x0050f7a0)

Creates projectile objects (size 0x134) for weapons. Handles two cases based on value at offset `+0x70`:
- If zero: Creates standard projectile
- If non-zero: Creates projectile with special initialization

**Heap check:** Requires `DAT_009c51f0 > 0x31fff` (more memory needed for projectiles)

### CWorldPhysicsManager__CreateSpawner (0x0050f970)

Iterates through spawner list at `DAT_008553f4`, finds spawner at specified index, allocates memory (size 0x3f8), and creates via `CSpawnerThng__Constructor`.

### CWorldPhysicsManager__CreateCharacter (0x0050fa40)

Creates character entities. Has special handling for "Gill_M_Head" (main character):
- If name matches "Gill_M_Head": Creates player character (size 0x2c0)
- If has value at offset +300: Creates complex character (size 0x310)
- Otherwise: Creates simple character (size 0x2c0)

Iterates through component list at `DAT_00855400`.

### CWorldPhysicsManager__CreatePickup (0x0050ff10)

Creates pickup item objects (size 0x94). Sets up pickup with vtable at `PTR_LAB_005e4454`.

**Heap check:** Requires `DAT_009c51f0 > 0x31fff`

### CWorldPhysicsManager__CreateEffect (0x00510060)

Creates visual effect objects (size 0xf4). Sets up effect with vtable at `PTR_FUN_005e45e0`.

### CWorldPhysicsManager__CreateTrigger (0x00510150)

Creates trigger zone objects (size 0x88). Triggers are used for scripted events and area detection. Sets up with vtable at `PTR_FUN_005e477c`.

### CCarrier__Destructor / CBigAirUnit__Destructor / CRelaxedSquad__Destructor / CMissile__Destructor / CComponent__Destructor / CGillMHead__Destructor_VFunc01 / CTentacle__Destructor / CExplosion__Destructor / CHazard__Destructor

These nine functions are class-owned slot-1 destructor bodies recovered from xref ownership of `*_VFunc_01_*` wrappers. They perform class-specific cleanup (set removals, owned pointer release, and base dtor dispatch) before returning.

### CWorldPhysicsManager__InitializeLists (0x005102a0)

Initializes 9 global linked lists used for entity management:
- `DAT_008553e8` - Weapons list
- `DAT_008553ec` - Unknown list 1
- `DAT_008553f0` - Unknown list 2
- `DAT_008553f4` - Spawners list
- `DAT_008553f8` - Unknown list 3
- `DAT_008553fc` - Things list (used by CreateThingByType)
- `DAT_00855400` - Components list
- `DAT_00855404` - Unknown list 4
- `DAT_00855408` - Unknown list 5

Each list is allocated 0x10 bytes and initialized via `CSPtrSet__Init`.

### CWorldPhysicsManager__ResolveLoadedDefinitionReferences (0x00510520)

Wave846 saved signature:

```c
void __cdecl CWorldPhysicsManager__ResolveLoadedDefinitionReferences(void)
```

Post-load fixup pass for physics/BattleEngine definition data. Iterates global definition lists and resolves string/id fields into runtime pointers/indices using helper lookup paths.

Wave560 split three generic resolver labels into list-specific helpers:

- `CWorldPhysicsManager__ResolveWeaponModeStatementRefs` (`0x00511ca0`) is called while iterating `DAT_008553ec`; it resolves node names at `+0x1c/+0x20` and sound-effect names at `+0x24/+0x28/+0x2c`.
- `CWorldPhysicsManager__ResolveTagDefinitionRefs` (`0x00511d20`) is called while iterating `DAT_008553f8`; it resolves node names at `+0x18..+0x24` and sound-effect names at `+0x28/+0x2c`.
- `CWorldPhysicsManager__ResolveThingOrComponentDefinitionRefs` (`0x00511db0`) is called for both `DAT_008553fc` thing definitions and `DAT_00855400` component definitions; it resolves many node-name fields from `+0x7c..+0xa4` plus sound-effect names at `+0xa8/+0xac`.

Wave846 static read-back ties this row to caller `0x0046cdd7 CGame__LoadResources`, with no pushed arguments or ECX receiver setup. The body iterates `DAT_008553ec`, `DAT_008553f0`, `DAT_008553f8`, `DAT_008553fc`, `DAT_00855400`, `DAT_00855404`, and `DAT_00855408`, including particle-set lookups through `CParticleSet__FindByNameAndTrackLinkSlot` and sound-effect lookups through `CSoundManager__GetEffectByName`.

The queue-tail reference resolver tranche is static saved-Ghidra evidence only. Exact definition schemas, source method identities, concrete layouts, runtime resolve behavior, BEA launch, patching, and rebuild parity remain unproven.

### CWorldPhysicsManager__FreeNestedThingSets_6C (0x00510740)

Wave846 saved signature:

```c
void __cdecl CWorldPhysicsManager__FreeNestedThingSets_6C(void)
```

Shutdown helper used by `CGame__ShutdownRestartLoop` at caller `0x0046cc61`: iterates Thing/Component definition lists (`DAT_008553fc` and `DAT_00855400`), drains nested set at `entry+0x6C`, and frees each object. The caller-site evidence shows no pushed arguments or ECX receiver setup.

### CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData (0x00510800)

Wave846 saved signature:

```c
void __cdecl CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData(void)
```

Full WorldPhysicsManager reload path:
- clears and reinitializes definition lists
- loads `data/default_physics.dat`
- rebuilds/loads `CBattleEngineDataManager` entries from `data/battle_engine_configuration`
- repopulates global battle-engine data set (`DAT_006602a0`)

Wave846 static read-back ties this row to `0x004f0092 CLTShell__InitializeRuntimeAndLoadCoreResources`, with no pushed arguments or ECX receiver setup. It calls `CWorldPhysicsManager__ClearAndFreeAllDefinitionLists` at `0x0051081e`, then `CWorldPhysicsManager__InitializeLists`, and handles both the default physics script load and the replacement BattleEngineData load path.

### CWorldPhysicsManager__FreeEntryOwnedPtrs_00_0C_20 (0x00510e60)

Compact helper that frees and zeroes three owned pointers at offsets `+0x00`, `+0x0C`, and `+0x20` on a definition node.

### CWorldPhysicsManager__ClearAndFreeAllDefinitionLists (0x00510a90)

Wave846 saved signature:

```c
void __cdecl CWorldPhysicsManager__ClearAndFreeAllDefinitionLists(void)
```

Global teardown path for definition lists. Iterates each global `CSPtrSet` list (`DAT_008553e8` .. `DAT_00855408`), removes entries, dispatches each through the matching per-entry free helper (or object vfunc for spawner nodes), then clears/frees each list container and nulls the global pointers.

Wave846 static read-back ties this row to `0x004f00e0 CLTShell__ShutdownRuntimeAndReleaseResources` and reload-internal call `0x0051081e`, both with no pushed arguments or ECX receiver setup. The body first drains `DAT_006602a0` BattleEngineData entries, then uses the Wave559 cleanup helpers and direct `DAT_00855408` owned-pointer frees before final list-container cleanup.

### CWorldPhysicsManager__FreeRoundStatement (0x00510eb0)

Per-entry cleanup helper for round statements (list `DAT_008553f0`). Frees owned pointers at offsets `+0x08..+0x18` and zeroes those fields.

### CWorldPhysicsManager__FreeWeaponModeStatement (0x00510f10)

Per-entry cleanup helper for weapon-mode statements (list `DAT_008553ec`). Removes/frees linked-set nodes, releases owned pointers, then clears embedded `CSPtrSet` members.

### CWorldPhysicsManager__FreeWeaponStatement (0x00511040)

Per-entry cleanup helper for weapon statements (list `DAT_008553e8`). Releases two owned pointers and zeroes the fields.

### CWorldPhysicsManager__FreeThingOrComponentDefinitionEntry (0x005110f0)

Shared cleanup helper used by both the things list (`DAT_008553fc`) and components list (`DAT_00855400`). Frees many owned pointers and embedded set/list members, then clears the set heads.

### CWorldPhysicsManager__FreeTagDefinitionEntry (0x00511070)

Per-entry cleanup helper for nodes in `DAT_008553f8` (tag-definition list). Releases owned pointers (`+0x18..+0x30`) and zeroes those fields.

### CWorldPhysicsManager__ClearEntryWorkSets_40_50 (0x005113a0)

Helper that clears two embedded `CSPtrSet` working sets on definition nodes (`node+0x40` and `node+0x50`).

### CWorldPhysicsManager__MapGunOrSpawnerTagToIndex (0x005115b0)

Maps textual script tags to compact IDs used by add-by-name pipelines:
- `GunA..GunI` -> `1..9`
- `SpawnerA..SpawnerE` -> `10..14`

This mapper is consumed by both `CWorldPhysicsManager__AddWeaponByName` and `CWorldPhysicsManager__AddSpawnerByName`.

### CWorldPhysicsManager__ResolveTagListNameToIndex_E8/EC/F0 (0x00511720 / 0x005117c0 / 0x00511860)

Three sibling helpers with identical search logic:
- iterate `DAT_008553f8`
- compare requested name against `entry+0x30`
- store resolved index into `this+0xE8`, `this+0xEC`, or `this+0xF0`
- write `-1` when no match is found

### CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName (0x00511440)

Allowlist gate called by `CSpawnerThng__ProcessSpawnWave`: finds a definition node by name in `DAT_008553fc`, checks its type enum (`entry+0xE0`), and returns true only for allowed spawnable categories.

### CWorldPhysicsManager__AddComponentByName (0x00511900)

Searches component list (`DAT_00855400`) for component by name string, allocates 8-byte struct to store index, and adds to tail of list via `CSPtrSet__AddToTail`. Logs warning if component not found.

### CWorldPhysicsManager__AddWeaponByName (0x005119e0)

Searches weapon list (`DAT_008553e8`) for weapon by name string, allocates 0xc-byte struct, and adds to list. Logs "Weapon '%s' not found" if lookup fails.

### CWorldPhysicsManager__AddSpawnerByName (0x00511ad0)

Searches spawner list (`DAT_008553f4`) for spawner by name string, allocates 0xc-byte struct, and adds to list. Logs "Spawner '%s' not found" if lookup fails.

## Global Variables

| Address | Name | Purpose |
|---------|------|---------|
| `0x009c51f0` | Heap remaining | Checked before allocations |
| `0x008553e8` | Weapons list head | Linked list of weapon definitions / weapon-statement entries (`CWeaponStatement__Create`) |
| `0x008553ec` | Weapon-mode statement list | Populated by `CWeaponModeStatement__Create` (`0x0042fa80`) |
| `0x008553f0` | Round statement list | Populated by `CRoundStatement__Create` (`0x0042ffa0`) |
| `0x008553f4` | Spawners list head | Linked list of spawner definitions |
| `0x008553f8` | Entity list 3 | List searched by name (`entry+0x30`) in tag-index resolve helpers; likely gun/spawner tag definition entries |
| `0x008553fc` | Things list head | Main physics objects list |
| `0x00855400` | Components list head | Character components |
| `0x00855404` | Entity list 4 | Unknown entity type |
| `0x00855408` | Entity list 5 | Unknown entity type |

## Memory Allocation

All allocations use `OID__AllocObject(size, type, filename, line)`:
- Parameter 1: Allocation size in bytes
- Parameter 2: Allocation type/category
- Parameter 3: Source filename for debugging
- Parameter 4: Source line number

## Related Source Files

- `Career.cpp` - Uses physics manager for level loading
- `Player.cpp` - Player character created through this system
- `BattleEngine.cpp` - Battle engine uses spawners and weapons
