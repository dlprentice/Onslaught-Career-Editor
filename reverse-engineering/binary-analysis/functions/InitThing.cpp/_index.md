# InitThing.cpp Functions

> Source File: InitThing.cpp | Binary: BEA.exe
> Debug Path: 0x0062d7b0 (`[maintainer-local-source-export-root]\InitThing.cpp`)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

InitThing.cpp implements the **CInitThing class hierarchy** - initialization data structures used when spawning game objects. These are NOT the game objects themselves (CThing and subclasses), but temporary data holders used during object creation.

**Key Concept:** When loading a level, the game reads object definitions from the level file into CInitThing-derived structures, then uses `SpawnInitThing()` as a factory to create the appropriate type based on Object ID (OID).

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0040e1b0 | CInitThing__CopyFrom | Shared CInitThing vtable slot 0 copy helper | ~210 bytes |
| 0x0040e280 | CInitThing__LoadFromMemBuffer | Base CInitThing version-gated memory-buffer load reader | ~850 bytes |
| 0x004bc510 | CExplosionInitThing__IsGridSegmentBlocked | Packed occupancy line-of-sight/blockage test | read-back documented |
| 0x004bc6d0 | CExplosionInitThing__FindNearestSetBitInOccupancyGrid | Expanding nearest set-bit search in occupancy grid | read-back documented |
| 0x004be970 | CExplosionInitThing__TestBitAtGridCoordPacked | Packed occupancy bit test for one grid coordinate | read-back documented |
| 0x004bed30 | CExplosionInitThing__StepToLowestCostNeighbor8 | Cost-grid eight-neighbor path step helper | read-back documented |
| 0x004beea0 | CExplosionInitThing__SimplifyGridPathByLineOfSight | Path simplifier using occupancy line-of-sight checks | read-back documented |
| 0x0048c650 | InitThing__CreateThingByType | Factory - creates CInitThing subclass by OID | ~1200 bytes |
| 0x0048d8d0 | CSquadInitThing__LoadFromMemBuffer | Squad init load wrapper over CInitThing load state | ~80 bytes |
| 0x0048dcf0 | CInitThing__ctor | Base CInitThing default constructor / initializer | ~180 bytes |

## Wave754 InitThing Factory Unwind Continuation (2026-05-23)

Wave754 static read-back (`unwind-continuation-wave754`, `wave754-readback-verified`) hardened eight InitThing.cpp factory unwind callbacks from `0x005d2ff0 Unwind@005d2ff0` through `0x005d308a Unwind@005d308a` as `void __cdecl Unwind@...(void)`. Evidence includes InitThing.cpp debug path `0x0062d7b0`, DATA scope-table xrefs `0x0061bda4` through `0x0061bddc`, line token `0x09`, and allocation/type values `0x0f`, `0x13`, `0x17`, `0x1b`, `0x1f`, `0x23`, `0x27`, and `0x2b`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-102949_post_wave754_unwind_continuation_verified`. The next commentless high-signal row is `0x005d30a0 Unwind@005d30a0`, which appears to continue the same factory unwind run. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

| Address | Scope-table xref | Static read-back evidence |
| --- | --- | --- |
| `0x005d2ff0` | `0x0061bda4` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x0f`. |
| `0x005d3006` | `0x0061bdac` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x13`. |
| `0x005d301c` | `0x0061bdb4` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x17`. |
| `0x005d3032` | `0x0061bdbc` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x1b`. |
| `0x005d3048` | `0x0061bdc4` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x1f`. |
| `0x005d305e` | `0x0061bdcc` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x23`. |
| `0x005d3074` | `0x0061bdd4` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x27`. |
| `0x005d308a` | `0x0061bddc` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x2b`. |

## Wave755 InitThing Factory Continuation (2026-05-23)

Wave755 static read-back (`unwind-continuation-wave755`, `wave755-readback-verified`) hardened the next five InitThing.cpp factory unwind callbacks from `0x005d30a0 Unwind@005d30a0` through `0x005d30f8 Unwind@005d30f8` as `void __cdecl Unwind@...(void)`. Evidence includes InitThing.cpp debug path `0x0062d7b0`, DATA scope-table xrefs `0x0061bde4` through `0x0061be04`, line token `0x09`, and allocation/type values `0x2f`, `0x33`, `0x37`, `0x3b`, and `0x3f`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-105815_post_wave755_unwind_continuation_verified`. The next commentless high-signal row is `0x005d3392 Unwind@005d3392` after Wave755. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

| Address | Scope-table xref | Static read-back evidence |
| --- | --- | --- |
| `0x005d30a0` | `0x0061bde4` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x2f`. |
| `0x005d30b6` | `0x0061bdec` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x33`. |
| `0x005d30cc` | `0x0061bdf4` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x37`. |
| `0x005d30e2` | `0x0061bdfc` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x3b`. |
| `0x005d30f8` | `0x0061be04` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x3f`. |

## Wave457 ExplosionInitThing Pathfinding Corrections (2026-05-16)

Wave457 saved signature/comment/tag corrections for five CExplosionInitThing pathfinding helpers tied to the world occupancy bitplanes:

| Address | Current saved Ghidra state | Evidence summary |
| --- | --- | --- |
| `0x004bc510` | `CExplosionInitThing__IsGridSegmentBlocked(void * this, int start_grid_x, uint start_grid_y, int end_grid_x, uint end_grid_y)` | `RET 0x10` proves four stack coordinates after `this`; the stale float parameter was a register artifact. |
| `0x004bc6d0` | `CExplosionInitThing__FindNearestSetBitInOccupancyGrid(void * this, int * inout_grid_x, int * inout_grid_y)` | `RET 0x8` proves two inout coordinate pointers after `this`; the stale third pointer was a register artifact. |
| `0x004be970` | `CExplosionInitThing__TestBitAtGridCoordPacked(void * this, int grid_x, uint grid_y)` | `RET 0x8` proves grid-x/grid-y only and returns the packed bit mask result. |
| `0x004bed30` | `CExplosionInitThing__StepToLowestCostNeighbor8(int * inout_grid_x, int * inout_grid_y)` | Reads the `DAT_00809dc0` cost field and writes the lowest-cost neighbor back to the inout coordinate pointers. |
| `0x004beea0` | `CExplosionInitThing__SimplifyGridPathByLineOfSight(void * this, void * bitplane_base)` | `RET 0x4` proves only the bitplane pointer after `this`; it uses `path+0x0c` count and `path+0x10/+0x18` coordinate arrays. |

This is static saved-Ghidra evidence only. Runtime pathfinding behavior, concrete path/occupancy layouts, exact source identities, and rebuild parity remain unproven.

## Wave424 InitThing Load Signature Correction (2026-05-14)

Wave424 hardened `0x0040e280` as `CInitThing__LoadFromMemBuffer` with signature `void __thiscall CInitThing__LoadFromMemBuffer(void * this, int version, void * mem_buffer)`. Static retail evidence reads the first stack argument as a 16-bit version, branches on source-aligned `CInitThing::Load(short inVersion, CMEMBUFFER &inFile)` version thresholds, calls `CDXMemBuffer__Read`, fills base transform/orientation fields, reads script/name/spawn-script strings at `+0xac/+0x1ac/+0x2ac`, and reads active/attach flags at `+0x3ac/+0x3b0`.

This pass preserves the existing function boundary and name while correcting generic `param_1` / `param_2` signature debt and refreshing proof-boundary tags/comments. It is static saved-Ghidra evidence only. It does not prove runtime level loading, full class layouts, exact local-variable types, exact `CMEMBUFFER` layout, or rebuild parity.

## Wave419 InitThing Correction (2026-05-14)

Wave419 corrected the older over-specific `CInfluenceMap__Init` label at `0x0048dcf0`. Fresh metadata, decompile, instruction, xref, vtable, and Stuart-source comparison show this body is the shared `CInitThing` default constructor used by the InitThing factory and subclass construction paths, not an InfluenceMap-specific initializer.

The same pass hardened three adjacent InitThing records:

- `0x0040e1b0` is saved as `CInitThing__CopyFrom`, the base vtable slot 0 copy helper for transform, orientation, script/name/spawn-script arrays, and tail fields.
- `0x0040e280` is saved as `CInitThing__LoadFromMemBuffer`, the base version-gated memory-buffer reader used by derived load wrappers.
- `0x0048c650` remains `InitThing__CreateThingByType`, with a one-argument retail signature around the source-aligned `SpawnInitThing` object-id factory.
- `0x0048d8d0` is saved as `CSquadInitThing__LoadFromMemBuffer`, chaining through `CInitThing__LoadFromMemBuffer` and reading squad amount/mode state.
- `0x0048dcf0` is saved as `CInitThing__ctor`, seeding base defaults and installing the base vtable at `0x005dc1cc`.

This is static saved-Ghidra evidence only. It does not prove runtime level loading, complete class layouts, exact local-variable types, or rebuild parity.

## Headless Semantic Wave119 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x00444620 | Superseded: CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric | Wave 351 corrected the older `CExplosionInitThing` owner label. Current saved Ghidra evidence places this body in the destructable controller cluster as a bulk active-flag setter plus cached active-value refresh. |

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
- Binary implementation at 0x0048c650; the checked retail signature currently exposes the object-id argument, not a separately observed report-errors flag
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
The binary factory strongly aligns with Stuart's source code `SpawnInitThing()`:
- Same checked switch cases for OID values
- Same class types created
- Same MT_INIT_THING allocation context and debug-path/line-number evidence
- Subclass setup calls the shared `CInitThing__ctor` before installing subclass vtables/defaults

The current saved `CSquadInitThing__LoadFromMemBuffer` label aligns with source `CSquadInitThing::Load`, including the base `CInitThing::Load` call and version-gated squad mode load.

### Exception Handlers
13 `Unwind@*` functions (0x005d2ff0 - 0x005d30f8) are compiler-generated exception handlers for the factory function, not source-level functions. Wave754 hardened the first eight (`0x005d2ff0` through `0x005d308a`) as saved static Ghidra metadata only; `0x005d30a0 Unwind@005d30a0` remains the next high-signal row.

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
