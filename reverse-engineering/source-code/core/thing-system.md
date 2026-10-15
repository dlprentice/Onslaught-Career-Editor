# Thing System

> Analysis from thing.cpp/h and InitThing.cpp/h - December 2025

## Overview

The Thing system is the base class hierarchy for ALL game objects in Battle Engine Aquila. This is a **runtime-only** system - Thing objects are NOT serialized to .bes save files.

---

## Class Hierarchy

The Thing system uses a deep inheritance chain from a base monitoring class up through specialized game entities:

```
CMonitor
  └── CThing
        └── CComplexThing
              └── CActor
                    └── CUnit
                          └── CBattleEngine
```

Each level adds capabilities:
- **CMonitor** - Base observer pattern for event handling
- **CThing** - Basic game object with position, flags, and type
- **CComplexThing** - Adds rotation, animation, and scripting
- **CActor** - Game actors with AI and behavior
- **CUnit** - Combat units with health and damage
- **CBattleEngine** - The player-controlled mech

---

## CThing Core Members

The pristine PC retail layout is exactly `0x3c` bytes with ABI alignment 4.
Offsets include both vfptrs and the offset-zero base-chain word; the complete
proof is in the [retail layout recovery](../../binary-analysis/cthing-ccomplexthing-layout-2026-08-13.md).

| Offset | Member | Type | Purpose |
|-------:|--------|------|---------|
| `0x0c` | `mMapWhoEntry` | - | Spatial partitioning registration |
| `0x1c` | `mPos` | `FVector` | World position (x, y, z) |
| `0x2c` | `mFlags` | `short` | `THING_FLAGS` bitmask |
| `0x2e` | `mThingNumber` | `short` | Counter-derived runtime thing number |
| `0x30` | `mRenderThing` | pointer | Visual mesh reference |
| `0x34` | `mThingType` | `ULONG` | Type bitmask (ORed up hierarchy) |
| `0x38` | `mCollisionSeekingThing` | pointer | Collision detection component |

---

## CComplexThing Additional Members

The pristine PC retail layout is exactly `0x7c` bytes including the `CThing`
base, with ABI alignment 4.

| Offset | Member | Type | Purpose |
|-------:|--------|------|---------|
| `0x3c` | `mOrientation` | `FMatrix` | 48-byte orientation/transform matrix |
| `0x6c` | `mAnimation` | pointer | Animation controller |
| `0x70` | `mMotionController` | pointer | Motion controller |
| `0x74` | `mMissionScript` | pointer | Level scripting interface |
| `0x78` | `mName` | pointer | Named object registry entry |

---

## THING_FLAGS Bitmask

Flags stored in `CThing::mFlags` (16-bit short):

| Flag | Value | Purpose |
|------|-------|---------|
| `TF_DECLARED_SHUTDOWN` | 1 | Shutdown has been scheduled |
| `TF_IN_MAP_WHO` | 2 | Registered in spatial partition |
| `TF_DYING` | 4 | Death process has started |
| `TF_DONT_RENDER` | 8 | Invisible but still collidable |
| `TF_INVISIBLE` | 16 | Fully invisible (no render, no collision) |
| `TF_MARKED_OBJECTIVE` | 32 | Marked as mission objective |
| `TF_IS_BIG_THING` | 64 | Optimization flag for large objects |
| `TF_SLIDE` | 128 | Enable sliding on collision |

**Usage Examples:**
```cpp
thing->mFlags |= TF_INVISIBLE;           // Make completely invisible
thing->mFlags |= TF_MARKED_OBJECTIVE;   // Highlight as objective
if (thing->mFlags & TF_DYING) { ... }   // Check if dying
```

---

## Type System (mThingType)

The type system uses a bitmask where types are ORed up the inheritance hierarchy. This allows `IsA()` checks to work efficiently:

### Core Types

- `THING_TYPE_THING` - Base thing type (all entities have this)
- `THING_TYPE_COMPLEX_THING` - Has orientation/animation
- `THING_TYPE_ACTOR` - AI-capable actor
- `THING_TYPE_UNIT` - Combat unit
- `THING_TYPE_BATTLE_ENGINE` - Player mech

### Kill Category Types

These types determine which kill counter increments when an enemy dies:

| Type | Kill Counter | Goodie Unlock Thresholds |
|------|--------------|--------------------------|
| `THING_TYPE_AIR_UNIT` | TK_AIRCRAFT | 25, 50, 75, 100 |
| `THING_TYPE_VEHICLE` | TK_VEHICLES | 100, 200, 300, 400 |
| `THING_TYPE_INFANTRY` | TK_INFANTY | 40, 80, 160 (no standalone 120-based goodie in retail) |
| `THING_TYPE_MECH` | TK_MECHS | 20, 40, 80 (40 unlocks two goodies) |
| `THING_TYPE_EMPLACEMENT` | TK_EMPLACEMENTS | 25, 50 (75 appears in combined unlocks) |

### Type Checking

```cpp
// Example from Player.cpp
if (thing->IsA(THING_TYPE_AIR_UNIT)) {
    // This is an aircraft - increment aircraft kills
}

// CBattleEngine has ALL parent types ORed together:
// THING_TYPE_THING | THING_TYPE_COMPLEX_THING | THING_TYPE_ACTOR |
// THING_TYPE_UNIT | THING_TYPE_BATTLE_ENGINE
```

---

## Kill Tracking Connection

In the Steam build analyzed for this repo, Thing-type kill categories map to retail `.bes` kill counters (true dword view) with base offset **0x23F6** (re-verify offsets for other builds/platforms):

```cpp
// From Player.cpp kill tracking logic
void CPlayer::ThingKilledBy(CThing* thing) {
    if (thing->IsA(THING_TYPE_AIR_UNIT))     mThingsKilled[TK_AIRCRAFT]++;
    if (thing->IsA(THING_TYPE_VEHICLE))      mThingsKilled[TK_VEHICLES]++;
    if (thing->IsA(THING_TYPE_INFANTRY))     mThingsKilled[TK_INFANTY]++;  // typo preserved
    if (thing->IsA(THING_TYPE_MECH))         mThingsKilled[TK_MECHS]++;
    if (thing->IsA(THING_TYPE_EMPLACEMENT))  mThingsKilled[TK_EMPLACEMENTS]++;
}
```

**Kill Counter File Offsets** (from .bes save format):

| Index | Category | File Offset | Array |
|-------|----------|-------------|-------|
| 0 | TK_AIRCRAFT | 0x23F6 | `mKilledThings[0]` |
| 1 | TK_VEHICLES | 0x23FA | `mKilledThings[1]` |
| 2 | TK_EMPLACEMENTS | 0x23FE | `mKilledThings[2]` |
| 3 | TK_INFANTY (typo) | 0x2402 | `mKilledThings[3]` |
| 4 | TK_MECHS | 0x2406 | `mKilledThings[4]` |

Retail encoding (true view): `stored = (meta << 24) | (kills & 0x00FFFFFF)` (preserve `meta` when patching). The historical 4-byte-aligned view makes values appear as `dword >> 16` due to 2-byte misalignment.

---

## Object alignment versus allocator block alignment

`MemoryManager.cpp` contains 16-byte heap-block assertions and rounds requested
allocation sizes to 16-byte boundaries:
```cpp
ASSERT((aSize & 0xf) == 0);
```

That is an allocator contract, not proof that every C++ object has 16-byte ABI
alignment or a size divisible by 16. The released 32-bit layouts above are
aligned to 4 bytes; `CThing` ends at `0x3c`, directly falsifying the prior broad
claim. Individual allocation blocks may still be rounded or aligned to 16.

---

## DECLARE_THING_CLASS Macro

The source code uses a macro to establish the inheritance chain:

```cpp
DECLARE_THING_CLASS(CComplexThing, CThing)    // thing.h:257        — SOURCE
DECLARE_THING_CLASS(CActor, CComplexThing)    // actor.h:13         — SOURCE
DECLARE_THING_CLASS(CUnit, CActor)            // INFERRED — Unit.h is not in the drop
DECLARE_THING_CLASS(CBattleEngine, CUnit)     // BattleEngine.h:72  — SOURCE
```

**CORRECTED 2026-07-28 — this section overstated what the macro does, and the
macro's own body is not in the pinned drop.** `grep -rn 'DECLARE_THING_CLASS'`
over `references/Onslaught/` returns exactly three use sites (`thing.h:257`,
`actor.h:13`, `BattleEngine.h:72`) and **no `#define` anywhere**, so the
expansion below is a reconstruction, not source. The `CUnit` line above is
likewise inference: `Unit.h` is not in the drop.

This macro:
1. Defines a `SUPERTYPE` typedef pointing to the parent class — INFERRED
2. Sets up virtual function table inheritance — INFERRED
3. Registers the type in the global type bitmask — INFERRED
4. ~~Creates the `IsA()` type-checking method~~ — **WITHDRAWN 2026-07-28.** It
   does not. `CThing` declares `IsA` exactly once, **non-virtually**, at
   `references/Onslaught/thing.h:174`. Nothing generates a per-class override.

**Expanded Example — INFERRED, not source.** `DECLARE_THING_CLASS`'s definition is
outside the pinned corpus; this block is a reconstruction of what the three use
sites imply, and no part of it has been checked against a macro body:
```cpp
// INFERRED reconstruction of DECLARE_THING_CLASS(CBattleEngine, CUnit).
// The macro body is NOT in references/Onslaught/ — do not cite this as source.
class CBattleEngine : public CUnit {
    typedef CUnit SUPERTYPE;

    // Constructor sets: mThingType = SUPERTYPE::mThingType | THING_TYPE_BATTLE_ENGINE
};
```

The reconstruction previously carried a fifth line inside that class body:

```cpp
    virtual BOOL IsA(ULONG type) {
        return (mThingType & type) != 0;
    }
```

It is withdrawn. The real, and only, declaration is on `CThing`:

```cpp
// references/Onslaught/thing.h:174
const BOOL IsA(EThingType type) const { return (type & mThingType); }
```

Non-virtual; `const` return and const-qualified member; takes `EThingType`, not
`ULONG`; returns the raw masked value rather than a normalised 0/1.
`grep -rn 'virtual.*IsA' references/Onslaught/` finds only the unrelated
`BattleEngine.h:250 virtual BOOL IsAThreat()`. The same withdrawal was applied
the same day to
[`../../quick-reference/source-hierarchy.md`](../../quick-reference/source-hierarchy.md),
which carried the identical wrong signature.

---

## Relevance to Save Editing

**INDIRECT** - Thing objects themselves are purely runtime state and NOT saved to .bes files.

However, understanding the Thing type system is important because:

1. **Kill Categories**: The `THING_TYPE_*` flags determine which kill counter increments when an enemy dies
2. **Goodie Unlocks**: Kill-based goodies (e.g., "Destroy 100 aircraft") depend on correct categorization
3. **Debugging**: Understanding type hierarchy helps trace why certain kills count toward specific categories
4. **Source Code Navigation**: Many gameplay systems reference Thing types - understanding the hierarchy helps navigate the codebase

### What IS Saved (in CCareer)

- Kill counters (`mKilledThings[5]`) - accumulated from Thing type categorization
- Goodie unlock states - triggered by kill thresholds
- Career progression - unlocked by completing objectives (tracked via Thing objective flags)

### What is NOT Saved (Runtime-Only)

- Thing positions, orientations, velocities
- Thing flags (TF_*)
- Object instances (destroyed on level change)
- Animation states, collision data

The Thing system explains **why** kills are categorized the way they are, even though the objects themselves aren't persisted.

---

## Object Initialization System (InitThing.cpp/h)

The InitThing system provides data transfer objects (DTOs) for level loading. **This is completely separate from the career save system.**

### Purpose

`CInitThing` and its subclasses serve as intermediate data structures during level loading:
1. Level files contain serialized `CInitThing` data
2. On load, `CInitThing::Load()` deserializes from binary
3. The data is then passed to `CThing::Init()` to construct actual game objects
4. `CInitThing` objects are discarded after initialization

**Key Point**: This is LEVEL data, NOT career save data.

### Object Types Supported

The `SpawnInitThing()` factory function creates appropriate InitThing subclasses based on object ID:

| Object ID | InitThing Class | Purpose |
|-----------|-----------------|---------|
| `OID_CUnit`, `OID_CBuilding` | `CUnitInitThing` | Combat units, structures |
| `OID_CSquad` | `CSquadInitThing` | AI squad groups |
| `OID_CSpawnerThing` | `CSpawnerInitThing` | Enemy spawners |
| `OID_CCutscene` | `CCutsceneInitThing` | Cinematic triggers |
| `OID_CStart`, `OID_CSpawnPoint` | `CStartInitThing` | Player spawn points |
| `OID_CTree` | `CTreeInitThing` | Vegetation objects |
| `OID_CWall` | `CWallInitThing` | Collision barriers |
| `OID_CFeature` | `CFeatureInitThing` | Static world features |
| `OID_CHazard` | `CHazardInitThing` | Environmental hazards |
| `OID_CSphereTrigger` | `CSphereTriggerInitThing` | Trigger volumes |

### Dual Serialization Paths

The system supports two serialization modes:

| Build Type | Serialization Class | Format |
|------------|---------------------|--------|
| `EDITORBUILD` | `CArchive` (MFC) | Human-editable (editor) |
| Runtime | `CMEMBUFFER` | Binary (level files) |

```cpp
#ifdef EDITORBUILD
void CInitThing::Serialize(CArchive& ar) {
    // MFC archive serialization for editor
}
#endif

void CInitThing::Load(CMEMBUFFER* buf) {
    // Binary level file loading for runtime
}
```

### Version History

The format has at least **46 documented versions** with backwards compatibility:

```cpp
// Conceptual version evolution
if (version < 12) { /* Handle legacy field layout */ }
if (version >= 25) { /* Load new field added in v25 */ }
if (version >= 46) { /* Current format */ }
```

Each version adds new fields while maintaining ability to load older level files.

### Memory Allocation

InitThing objects use dedicated memory pool:

```cpp
// From MemoryManager.cpp
MT_INIT_THING  // Memory type for InitThing allocations
mThingHeap     // Heap used for thing-related memory
```

This segregates initialization data from persistent game object memory.

### Data Flow: Level File → Game Object

```
Level File (binary)
    │
    ▼
CMEMBUFFER::Load()
    │
    ▼
SpawnInitThing(objectID)
    │
    ├── Creates appropriate CInitThing subclass
    │
    ▼
CInitThing::Load(buffer)
    │
    ├── Deserializes position, rotation, properties
    │
    ▼
CThing::Init(pInitThing)
    │
    ├── Constructs actual game object
    │
    ▼
Game Object (in world)
    │
    ▼
CInitThing deleted (no longer needed)
```

### Comparison: InitThing vs Career System

| Aspect | InitThing System | Career System |
|--------|------------------|---------------|
| **Purpose** | Level object initialization | Player progress persistence |
| **Data Source** | Level files (`.aya`) | Save files (`.bes`) |
| **Lifetime** | Transient (load-time only) | Persistent (saved to disk) |
| **Structs** | `CInitThing` subclasses | `CCareerNode`, `CCareerNodeLink`, `CGoodie` |
| **Serialization** | `CMEMBUFFER` / `CArchive` | Direct `memcpy` |
| **Versioning** | 46+ format versions | Single version word (`0x4BD1`) (often *looks* like `0x00004BD1` in dword-aligned hex views) |

**Bottom Line**: InitThing is for loading level geometry and objects at runtime. Career saves store player progression, ranks, kills, and unlocks. These are completely independent systems.

---

## Files Analyzed

| File | Purpose |
|------|---------|
| `thing.cpp` | CThing/CComplexThing implementation |
| `thing.h` | Class definitions, THING_FLAGS enum, type constants |
| `InitThing.cpp` | InitThing implementation, `SpawnInitThing()` factory |
| `InitThing.h` | Class hierarchy, object IDs |
| `Player.cpp` | Kill tracking implementation (references Thing types) |
| `Career.h` | Kill counter array definition (`mKilledThings[5]`) |

---

## See Also

- [actor-system.md](actor-system.md) - Movement and physics built on CThing
- [../gameplay/game-system.md](../gameplay/game-system.md) - Kill tracking integration
- [../../save-file/save-format.md](../../save-file/save-format.md) - Kill counter file structure

---

*Last updated: December 2025*
