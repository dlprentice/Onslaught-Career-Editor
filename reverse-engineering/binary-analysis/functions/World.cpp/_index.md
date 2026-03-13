# world.cpp Functions

> Source File: world.cpp | Binary: BEA.exe | Debug Path: `C:\dev\ONSLAUGHT2\world.cpp`

## Overview

World/level loading and management. Handles loading level data from .aya asset archives. CWorld is the main world/level manager class responsible for deserializing level data, spawning entities, and managing world state.

## Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x0050abc0 | CWorld__CloneScriptObjectCodeByName | Find script object code by name in world registry and clone it |
| 0x0050abb0 | CWorld__ShutdownAndClear_Thunk | Thunk/wrapper to core world teardown routine (`CWorld__ShutdownAndClear`) |
| 0x0050ada0 | CWorld__ShutdownAndClear | Core world teardown and state-clear routine |
| 0x0050ac70 | CWorld__LoadScriptEvents | Load script events from world file buffer |
| 0x0050af70 | CWorld__FindThingByName | Find first world thing by name in world object set |
| 0x0050b010 | CWorld__DispatchHelper_004bc480 | Dispatch wrapper into helper `0x004bc480` |
| 0x0050b020 | CWorld__DispatchHelper_004bc3e0 | Dispatch wrapper into helper `0x004bc3e0` |
| 0x0050b520 | CWorld__LoadWorldFile | Open and load a world file (.wrd) |
| 0x0050b780 | CWorld__DeserializeWorld | Deserialize world data (base/real world positions) |
| 0x0050b9c0 | [CWorld__LoadWorld](./CWorld__LoadWorld.md) | Main world loading entry point |
| 0x0050d4c0 | CWorld__LoadWorldHeader | Load world header and configuration |
| 0x0050d580 | CWorld__InitLODLists | Initialize LOD (Level of Detail) lists |
| 0x0050d680 | CWorld__ReleaseSubObject_AndMaybeFree | Cleanup helper with optional free-on-flag behavior |
| 0x0050d6a0 | CWorld__PushWorldTextSlot | Queue/push a world text entry into first free display slot |
| 0x0050d720 | CWorld__UpdateWorldTextSlotTiming | Update timing/aux state for active world text slot entry |
| 0x0050d7a0 | CWorld__ClearWorldTextSlot | Clear/deactivate world text slot entry by text id |
| 0x0050d7d0 | CWorld__IsMultiplayerMode | Predicate for multiplayer world mode/state values |
| 0x0050d7f0 | CWorld__ClearLinkedObjectPairSet | Clear linked object-pair set and release pair objects |
| 0x0050dcb0 | CWorld__SpawnInitialThings | Spawn initial world things/entities |

## Level Loading Overview

Battle Engine Aquila stores levels in .aya archive files. The World system handles:

1. Parsing .aya archive headers
2. Extracting level geometry, textures, scripts
3. Setting up the game world for play
4. Managing world state during gameplay

## .AYA Archive Format

The AYA format is a proprietary archive containing:

- Level geometry/terrain
- Textures and materials
- MSL mission scripts
- Entity placement data
- Audio cues
- Lighting information

See `reverse-engineering/game-assets/` for detailed AYA format documentation.

## CWorld Class Structure

Based on decompilation analysis, the CWorld class has the following member offsets:

| Offset | Type | Member Name | Notes |
|--------|------|-------------|-------|
| 0x120 | CSPtrSet* | mScriptEvents | List of script event name/code pairs |
| 0x200 | void* | mLODList0 | LOD list for distance 35.0f |
| 0x204 | void* | mLODList1 | LOD list for distance 45.0f |
| 0x208 | void* | mLODList2 | LOD list for distance 60.0f |
| 0x26c | int | mCurrentWorldId | Current loaded world ID |
| 0x270 | int | mBaseWorldId | Base world ID (for linked worlds) |
| 0x274 | int | mRealWorldResource | Resource handle for real world |
| 0x278 | int | mBaseWorldResource | Resource handle for base world |
| 0x27c | int | mUnknown27c | Unknown, set from world header |

## Function Details

### CWorld__LoadScriptEvents (0x0050ac70)

Loads script events from the world file buffer. Iterates through events, allocating:
- CStringDataType for event names
- CScriptEventNB for event code
- Creates name/code pairs and adds them to the script events list

### CWorld__LoadWorldFile (0x0050b520)

Opens a world file and delegates to CWorld__LoadWorld.
- Constructs path: `data\\worlds\\%sworld_%03d.wrd`
- Handles caching of previously loaded worlds
- Uses CChunker for file reading
- Debug strings: "Loading world %d", "Loading base world %d"

### CWorld__DeserializeWorld (0x0050b780)

Deserializes world state from buffer:
- Debug string: "Deserializing world"
- Creates CRelaxedSquad instances
- Loads base world position (if exists)
- Loads real world position
- Uses global squad manager (DAT_0067a748)

### CWorld__LoadWorldHeader (0x0050d4c0)

Reads the world file header:
- Reads configuration data
- Calls BattleEngineConfigurations__Load or BattleEngineConfigurations__Skip
- Version-dependent field handling (version > 1, version > 2)

### CWorld__InitLODLists (0x0050d580)

Initializes three Level of Detail lists with different distance thresholds:
- LOD 0: 35.0f (0x420c0000)
- LOD 1: 45.0f (0x42340000)
- LOD 2: 60.0f (0x42700000)

Allocates 0x2004 bytes per LOD list.

### CWorld__SpawnInitialThings (0x0050dcb0)

Spawns initial world entities:
- Iterates through spawn list (DAT_00855358)
- Looks up squad types by name
- Creates things via CWorldPhysicsManager__CreateThingByType
- Initializes thing positions (256.0f, 256.0f, 0.0f default)

## World File Version History

The LoadWorld function checks version ranges:
- Version < 0x2b (43): Invalid
- Version > 0x32 (50): Invalid
- Valid range: 43-50

Version-specific handling:
- Version < 0x11 (17): Old format, many ReadBytes calls
- Version < 0x14 (20): Single string field
- Version < 0x1c (28): Two string fields
- Version < 0x22 (34): Three string fields
- Version >= 0x2e (46): Additional data fields
- Version >= 0x30 (48): Extra configuration field

## Global Variables

| Address | Type | Purpose |
|---------|------|---------|
| 0x0067a748 | CSquadManager* | Global squad manager |
| 0x0067a07c | void* | Unknown world object |
| 0x0067a078 | void* | Unknown world object |
| 0x00855358 | void* | Spawn list head |
| 0x00855360 | void* | Spawn list iterator |
| 0x008553fc | void** | Squad type list |

## Related Systems

- Script.cpp - MSL mission scripts loaded from .aya
- Career.cpp - Tracks level completion
- Game.cpp - Coordinates world loading
- WorldPhysicsManager.cpp - Creates world entities
- WorldMeshList.cpp - Manages world mesh rendering
- InfluenceMapManager - AI pathfinding data
- WaypointManager.cpp - Waypoint loading

---
*Migrated from ghidra-analysis.md (Dec 2025)*
*Updated Dec 2025: Added 6 new functions from world.cpp xref analysis*
