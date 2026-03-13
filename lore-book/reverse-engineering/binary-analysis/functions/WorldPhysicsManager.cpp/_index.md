# WorldPhysicsManager.cpp Functions

**Source File:** `C:\dev\ONSLAUGHT2\WorldPhysicsManager.cpp`
**Debug String Address:** `0x0063d798`

## Overview

WorldPhysicsManager handles entity creation and management for the game's physics simulation. This includes creating various game objects like vehicles, weapons, projectiles, characters, and managing their lifecycle through linked lists.

## Functions (38 total)

| Address | Name | Purpose |
|---------|------|---------|
| `0x0050df80` | `CWorldPhysicsManager__CreateThingByType` | Factory method - creates physics objects by type enum |
| `0x0050ef30` | `CCarrier__Destructor` | Carrier destructor body used by vfunc slot-1 wrapper (`CCarrier__VFunc_01_0050ee50`) |
| `0x0050f030` | `CBigAirUnit__Destructor` | Big-air-unit destructor body used by vfunc slot-1 wrapper (`CBigAirUnit__VFunc_01_0050f010`) |
| `0x0050f4b0` | `CWorldPhysicsManager__CreateSquad` | Creates squad objects (relaxed or normal) |
| `0x0050f630` | `CRelaxedSquad__Destructor` | Relaxed-squad destructor body used by vfunc slot-1 wrapper (`CRelaxedSquad__VFunc_01_0050f610`) |
| `0x0050f6d0` | `CWorldPhysicsManager__CreateWeaponByIndex` | Creates weapon objects from weapon list by index |
| `0x0050f7a0` | `CWorldPhysicsManager__CreateProjectile` | Creates projectile objects for weapons |
| `0x0050f8d0` | `CMissile__Destructor` | Missile destructor body used by vfunc slot-1 wrapper (`CMissile__VFunc_01_0050f8b0`) |
| `0x0050f970` | `CWorldPhysicsManager__CreateSpawner` | Creates spawner objects from spawner list |
| `0x0050fa40` | `CWorldPhysicsManager__CreateCharacter` | Creates character objects (handles Gill special case) |
| `0x0050fd90` | `CComponent__Destructor` | Component destructor body used by vfunc slot-1 wrapper (`CComponent__VFunc_01_0050fd70`) |
| `0x0050fe10` | `CGillMHead__Destructor_VFunc01` | GillMHead slot-1 destructor body (`CGillMHead__VFunc_01_0050fd30`) |
| `0x0050fe90` | `CTentacle__Destructor` | Tentacle destructor body used by vfunc slot-1 wrapper (`CTentacle__VFunc_01_0050fd50`) |
| `0x0050ff10` | `CWorldPhysicsManager__CreatePickup` | Creates pickup items |
| `0x0050fff0` | `CExplosion__Destructor` | Explosion destructor body used by vfunc slot-1 wrapper (`CExplosion__VFunc_01_0050ffd0`) |
| `0x00510060` | `CWorldPhysicsManager__CreateEffect` | Creates visual effect objects |
| `0x00510150` | `CWorldPhysicsManager__CreateTrigger` | Creates trigger zone objects |
| `0x00510250` | `CHazard__Destructor` | Hazard destructor body used by vfunc slot-1 wrapper (`CHazard__VFunc_01_00510230`) |
| `0x005102a0` | `CWorldPhysicsManager__InitializeLists` | Initializes 9 entity management linked lists |
| `0x00510520` | `CWorldPhysicsManager__ResolveLoadedDefinitionReferences` | Resolves loaded physics/BattleEngine definition name references to runtime pointers/indices |
| `0x00510740` | `CWorldPhysicsManager__FreeNestedThingSets_6C` | Clears nested set at `+0x6C` for thing/component definition entries and frees child objects |
| `0x00510800` | `CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData` | Full reload path for `data/default_physics.dat` and `data/battle_engine_configuration` |
| `0x00510a90` | `CWorldPhysicsManager__ClearAndFreeAllDefinitionLists` | Drains/frees all definition lists and clears global list heads |
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

## Function Details

### CWorldPhysicsManager__CreateThingByType (0x0050df80)

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

Creates squad AI objects based on squad type parameter:
- Types 0, 3: Creates relaxed squad (size 0xb4)
- Other types: Creates normal squad (size 0x144) via `CSquadNormal__Constructor`

Shows "Thing heap full" error if heap exhausted.

### CWorldPhysicsManager__CreateWeaponByIndex (0x0050f6d0)

Iterates through weapon list at `DAT_008553e8`, finds weapon at specified index, allocates memory (size 0xb0), and initializes weapon object via `FUN_00505e00`.

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

Post-load fixup pass for physics/BattleEngine definition data. Iterates global definition lists and resolves string/id fields into runtime pointers/indices using helper lookup paths.

### CWorldPhysicsManager__FreeNestedThingSets_6C (0x00510740)

Shutdown helper used by `CGame__ShutdownRestartLoop`: iterates Thing/Component definition lists (`DAT_008553fc` and `DAT_00855400`), drains nested set at `entry+0x6C`, and frees each object.

### CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData (0x00510800)

Full WorldPhysicsManager reload path:
- clears and reinitializes definition lists
- loads `data/default_physics.dat`
- rebuilds/loads `CBattleEngineDataManager` entries from `data/battle_engine_configuration`
- repopulates global battle-engine data set (`DAT_006602a0`)

### CWorldPhysicsManager__FreeEntryOwnedPtrs_00_0C_20 (0x00510e60)

Compact helper that frees and zeroes three owned pointers at offsets `+0x00`, `+0x0C`, and `+0x20` on a definition node.

### CWorldPhysicsManager__ClearAndFreeAllDefinitionLists (0x00510a90)

Global teardown path for definition lists. Iterates each global `CSPtrSet` list (`DAT_008553e8` .. `DAT_00855408`), removes entries, dispatches each through the matching per-entry free helper (or object vfunc for spawner nodes), then clears/frees each list container and nulls the global pointers.

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
