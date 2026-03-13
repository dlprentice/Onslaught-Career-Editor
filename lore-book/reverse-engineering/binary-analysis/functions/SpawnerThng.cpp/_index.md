# SpawnerThng.cpp Functions

> Source File: SpawnerThng.cpp | Binary: BEA.exe
> Debug Path: 0x00632650 (`C:\dev\ONSLAUGHT2\SpawnerThng.cpp`)

## Overview

CSpawnerThng handles the spawning of game objects during gameplay - enemy waves, unit creation, reinforcements, etc. The spawner manages timing, position validation, wave counts, and coordinates with the game's object management system.

## Functions

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x004e3010 | CSpawnerThng__Init | ~800 bytes | Initialize spawner from spawn configuration data |
| 0x004e3330 | CSpawnerThng__Shutdown | ~64 bytes | Clean up spawner, free allocated memory |
| 0x004e3370 | CSpawnerThng__Update | ~896 bytes | Main update loop - manages spawn timing and wave progression |
| 0x004e36c0 | CSpawnerThng__FindSpawnerByName | ~144 bytes | Search spawner list by name string, returns index or -1 |
| 0x004e37f0 | CSpawnerThng__Constructor | ~512 bytes | Constructor - initializes vtable, exception handling, spawn params |
| 0x004e39f0 | CSpawnerThng__ScalarDeletingDestructor | ~32 bytes | MSVC scalar deleting destructor wrapper |
| 0x004e3a10 | CSpawnerThng__Destructor | ~144 bytes | Destructor - cleans up spawned objects, handles exceptions |
| 0x004e3aa0 | CSpawnerThng__CleanupAndDelete | ~32 bytes | Cleanup wrapper, calls destructor then virtual delete |
| 0x004e3ac0 | CSpawnerThng__UpdateSpawnCount | ~416 bytes | Validate and update spawn count, handles spawn modes |
| 0x004e3c60 | CSpawnerThng__DoSpawn | ~816 bytes | Execute spawn - get position, create object, update counters |
| 0x004e3f90 | CSpawnerThng__ProcessSpawnWave | ~1008 bytes | Process spawn wave - collision check, orientation, type mapping |
| 0x004e4430 | CSpawnerThng__IsSpawnComplete | ~80 bytes | Check if spawner has completed all waves |
| 0x004e44d0 | CSpawnerThng__IsSpawnPositionClear | ~176 bytes | Check spawn position for collision (6.0 unit radius) |

**Total: 13 functions identified**

## Vtable Layout (0x005dd190)

```
Offset  Address     Function
0x00    0x004e3010  CSpawnerThng__Init
0x04    0x00405930  (inherited - likely base class)
0x08    0x00405930  (inherited - likely base class)
0x0C    0x004014c0  (inherited)
0x10    0x00401420  (inherited)
0x14    0x004f43d0  (related class method)
0x18    0x004bfc60  (related class method)
...
```

## Key Class Members (from decompilation)

| Offset | Type | Purpose |
|--------|------|---------|
| 0x0468 | char* | Spawner name string (dynamically allocated) |
| 0x007c | ptr | Pointer to parent/owner object |
| 0x0080 | float | Next spawn time |
| 0x0084-0x008c | float[3] | Spawn timing parameters |
| 0x0090 | int | Spawn batch size |
| 0x0094 | int | Total spawn count (waves) |
| 0x0098 | int | Current wave count |
| 0x009c | int | Current batch count |
| 0x00a0 | int | Infinite spawn flag |
| 0x00a4 | int | Active flag |
| 0x00b0 | int | Spawn mode (0 or 1) |

## Key Observations

### Spawn Timing System
- Uses `DAT_00672fd0` as global game time reference
- Timer callback via `FUN_0044b370(3000, ...)` - likely a 3-second timer ID
- Timing controlled by floats at offsets 0x84, 0x88, 0x8c

### Spawn Position Validation
- Grid-based collision check (256x256 grid)
- Proximity check with 6.0 unit radius (36.0 squared distance)
- Object flag filtering: requires 0x10, excludes 0xc4900

### Spawn Type Mapping
Switch in ProcessSpawnWave maps spawn types:
- 10 -> 15
- 11 -> 16
- 12 -> 17
- 13 -> 18
- 14 -> 19

### Error Handling
- "Spawned more than we should be able to!!!" warning at 0x00632690
- Exception frame setup in constructor/destructor

### Linked List Management
- Uses global list at `DAT_008553fc` for spawner iteration
- String comparison for spawner lookup by name

## Related Strings

| Address | String |
|---------|--------|
| 0x00632650 | `C:\dev\ONSLAUGHT2\SpawnerThng.cpp` |
| 0x00632690 | `Spawned more than we should be able to!!!` |

## Related Functions (Not in SpawnerThng.cpp)

- `FUN_0050df80` - Object factory/creation
- `FUN_0050f4b0` - Object type lookup
- `FUN_0050f680` - Object validation
- `CSPtrSet__First`/`CSPtrSet__Next` - List iteration helpers
- `FUN_00511510` - Distance/influence calculation
- `CUnit__GetGridMapByType` - Grid map access by unit type
- `FUN_0044b370` - Timer/scheduler system

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*13 functions mapped from SpawnerThng.cpp debug path reference*
