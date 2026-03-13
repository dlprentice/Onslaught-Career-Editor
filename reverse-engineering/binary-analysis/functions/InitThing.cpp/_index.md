# InitThing.cpp Functions

> Source File: InitThing.cpp | Binary: BEA.exe
> Debug Path: 0x0062d7b0 (`C:\dev\ONSLAUGHT2\InitThing.cpp`)

## Overview

InitThing.cpp implements the **CInitThing class hierarchy** - initialization data structures used when spawning game objects. These are NOT the game objects themselves (CThing and subclasses), but temporary data holders used during object creation.

**Key Concept:** When loading a level, the game reads object definitions from the level file into CInitThing-derived structures, then uses `SpawnInitThing()` as a factory to create the appropriate type based on Object ID (OID).

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0048c650 | InitThing__CreateThingByType | Factory - creates CInitThing subclass by OID | ~1200 bytes |
| 0x0048dcf0 | CInfluenceMap__Init | Base initializer for influence map objects | ~180 bytes |

## Headless Semantic Wave119 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x00444620 | CExplosionInitThing__SetChildStateAndRefreshSegmentMetric | Writes child-state field (`+0x1c`) across attached entries and refreshes cached segment metric from destroyable-segment helper when attached segment exists. |

## Headless Semantic Wave122 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x00479d10 | CExplosionInitThing__UpdateGroundedVerticalDrift | Terrain-aware drift updater that toggles vertical drift coefficient based on grounded probe result before invoking shared update helper. |

## Object Factory Switch Table (0x0048c650)

The factory function uses a jump table at `0x0048cb44` with byte offsets at `0x0048cb78` to dispatch based on OID:

| Case (OID) | Class Created | Size | VTable | Notes |
|------------|---------------|------|--------|-------|
| 7 | CTreeInitThing | 0x4c0 (1216) | 0x5dc18c | Default "DefaultTree0" |
| 8 | CUnitInitThing | 0x3c0 (960) | 0x5dc1c0 | For OID_CUnit |
| 0xf (15) | CStartInitThing | 0x3c4 (964) | 0x5dbbd0 | For OID_CStart |
| 0x13 (19) | CSpawnerInitThing | 0x5d0 (1488) | 0x5dc1a4 | Unit spawner |
| 0x19 (25) | CUnitInitThing | 0x3c0 (960) | 0x5dc1c0 | For OID_CBuilding |
| 0x1a (26) | CCutsceneInitThing | 0x5bc (1468) | 0x5dc198 | Cutscene triggers |
| 0x1c (28) | CSquadInitThing | 0x4c4 (1220) | 0x5dc1b0 | AI squad init |
| 0x21 (33) | CWallInitThing | 0x4c4 (1220) | 0x5dc180 | Default "wall1" |
| 0x23 (35) | CFeatureInitThing | 0x3c0 (960) | 0x5dc174 | Environmental features |
| 0x24 (36) | CSphereTriggerInitThing | 0x3c0 (960) | 0x5dc15c | Sphere trigger volume |
| 0x27 (39) | CHazardInitThing | 0x3c0 (960) | 0x5dc168 | Hazard zones |
| 0x29 (41) | CStartInitThing | 0x3c4 (964) | 0x5dbbd0 | For OID_CSpawnPoint |
| default | CInitThing | 0x3bc (956) | 0x5dc1cc | Base class |

## Class Hierarchy

```
CInitThing (base, 0x3bc bytes)
  |-- mPos (FVector, 12 bytes)
  |-- mOrientation (FMatrix, 36 bytes)
  |-- mYaw, mPitch, mRoll (floats)
  |-- mVelocity (FVector)
  |-- mOrientationType (enum)
  |-- mMeshNo (SINT)
  |-- mInitCST (CInitCSThing - collision setup)
  |-- mAllegiance (enum)
  |-- mTarget (SINT)
  |-- mForceRadius (float)
  |-- mScript[256], mName[256], mSpawnScript[256]
  |-- mActive, mAttachScriptsToUnits (BOOL)
  |-- mSpawnedBy (CUnit*)
  |-- mWaypointPath (EEmitterType)
  |
  +-- CUnitInitThing (+mStats pointer)
  |     +-- CBattleEngineInitThing (+mConfigurationId, mPlaneMode)
  |
  +-- CTreeInitThing (+mTreeTypeComplete, mTreeType[256])
  +-- CSpawnerInitThing (+mAmount, mSquadSize, mDelay, mInitialDelay, mSquadDelay, mSpawnUnit[256], mSpawnerSpawnScript[256])
  +-- CSquadInitThing (+mAmount, mUnitName[256], mMode)
  +-- CWallInitThing (+mLength, mWallType[256], mLife)
  +-- CCutsceneInitThing (+mFile[256], mLinkTo[256])
  +-- CStartInitThing (+mPlaneMode, mPlayerNumber)
  +-- CSphereTriggerInitThing (+mRadius)
  +-- CFeatureInitThing (+mData pointer)
  +-- CHazardInitThing (+mData pointer)
  +-- CRoundInitThing (+mDest, mJumpsPerformed, mRoundData*, mInitialDelay, mLifeSpan)
  +-- CAnimalInitThing (+mType)
  +-- CExplosionInitThing (+mBehaviour*, mColType, mAttachedTo*, mUseAttachedRadius, mAllowVolumetric, mImportant, mOriginator*)
```

## Key Observations

### Factory Pattern
- `SpawnInitThing(SINT inID, BOOL inReportErrors)` in source code
- Binary implementation at 0x0048c650
- Called from `CWorld__LoadWorld` (7 times) and one other function
- Uses memory allocator at 0x9c3df0 (ECX = allocator object)

### Memory Allocation
- Allocation function at `OID__AllocObject` (likely `operator new` with placement)
- Arguments: (size, type=9, debug_file, line_number)
- Type 9 corresponds to `MT_INIT_THING` memory type
- Line numbers in debug strings match source code positions

### Default Values (from source)
- `CTreeInitThing`: mTreeType = "DefaultTree0" (string at 0x62d7a0)
- `CWallInitThing`: mWallType = "wall1" (string at 0x62d798), mLife = 50.0f
- `CStartInitThing`: mPlaneMode = FALSE, mPlayerNumber = 1
- `CSpawnerInitThing`: mAmount = -1, mSquadSize = 1, delays = 0

### Allegiance System (EAllegiance enum)
```cpp
kForsetiAllegiance = 0    // Player faction (blue)
kMuspellAllegiance = 1    // Enemy faction (red)
kNeutralAllegiance = 2    // Neutral (civilians, etc.)
kUndefinedAllegiance = 3
kInvalidAllegiance = 4
kToggleAllegiance = 5     // Switches sides
kIndependentAllegiance = 6
```

### Source Code Mapping
The binary factory matches Stuart's source code `SpawnInitThing()` exactly:
- Same switch cases for OID values
- Same class types created
- Same inheritance via `CInfluenceMap__Init` (appears to be inlined CInitThing constructor + influence map registration)

### Exception Handlers
13 `Unwind@*` functions (0x005d2ff0 - 0x005d30f8) are compiler-generated exception handlers for the factory function, not source-level functions.

## Cross-References

### Callers of InitThing__CreateThingByType (0x0048c650)
| Address | Function | Context |
|---------|----------|---------|
| 0x0050bc92 | CWorld__LoadWorld | Object spawn during level load |
| 0x0050bdd8 | CWorld__LoadWorld | Object spawn during level load |
| 0x0050bfc8 | CWorld__LoadWorld | Object spawn during level load |
| 0x0050c1dd | CWorld__LoadWorld | Object spawn during level load |
| 0x0050c29e | CWorld__LoadWorld | Object spawn during level load |
| 0x0050c9ab | CWorld__LoadWorld | Object spawn during level load |
| 0x0050caac | CWorld__LoadWorld | Object spawn during level load |
| 0x0050dd75 | FUN_0050dcb0 | Unknown context |

## Related Files

- **InitThing.h** - Class declarations, EAllegiance enum, EOrientationType enum
- **Oids.h** - Object ID constants (not in Stuart's source dump)
- **World.cpp** - Level loading, calls this factory
- **thing.cpp** - CThing base class (actual game objects)

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*Source code reference: `references/Onslaught/InitThing.cpp` and `InitThing.h`*
