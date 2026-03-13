# InfluenceMap.cpp - Function Analysis

**Source File**: `C:\dev\ONSLAUGHT2\InfluenceMap.cpp`
**Header File**: `C:\dev\ONSLAUGHT2\InfluenceMap.h`
**Analysis Date**: December 2025
**Status**: Complete

## Overview

The Influence Map system is used for AI decision-making in Battle Engine Aquila. It tracks territorial control by calculating influence values based on unit positions and propagating these values across connected map regions. The system supports two factions (likely player/ally vs enemy) and uses distance-based decay for influence propagation.

## Classes

### CInfluenceMapManager
Singleton manager class that owns and coordinates all influence map regions.

### CInfluenceMap
Individual influence map region (0xC4 = 196 bytes). Stores:
- Position (X, Y at offsets 0x8C, 0x90)
- Influence values for both factions
- Distance metrics to friendly/enemy controlled regions
- Links to neighboring regions

## Functions Summary

| Address | Name | Type | Description |
|---------|------|------|-------------|
| 0x0048b010 | CInfluenceMapManager__Load | Manager | Load influence maps from level file |
| 0x0048b620 | CInfluenceMap__ResetInfluence | Instance | Reset all influence values to defaults |
| 0x0048b660 | CInfluenceMapManager__SkipLoad | Manager | Skip/discard influence map data during load |
| 0x0048b7d0 | CInfluenceMapManager__PropagateDistances | Manager | Propagate distance values across linked regions |
| 0x0048b8e0 | CInfluenceMapManager__Update | Manager | Main update loop - gather unit influence and recalculate |
| 0x0048bf70 | CInfluenceMapManager__DecayInfluence | Manager | Decay temporary influence sources over time |
| 0x0048c000 | CInfluenceMapManager__FindNearestMap | Manager | Find nearest influence map to world coordinates |
| 0x0048c2d0 | CInfluenceMapManager__IsEmpty | Manager | Check if manager has no influence maps |
| 0x0048c2e0 | CInfluenceMap__ScalarDelete | Instance | Destructor wrapper for delete operator |
| 0x0048c300 | CInfluenceMap__Destructor | Instance | Clean up influence map resources |
| 0x0048c390 | CInfluenceMap__RemoveFromList | Instance | Remove from linked list |
| 0x0048c3b0 | CInfluenceMap__CalculateInfluence | Instance | Calculate net influence and control state |
| 0x004ad7f0 | CInfluenceMap__SetTrackedThingAndClearCachedObject | Instance | Battle-engine handoff helper: clears cached object slot (+0x24) and updates tracked thing pointer (+0x14) |
| 0x004d30d0 | CInfluenceMap__AccumulateThingFlags | Instance | Increment per-flag counters from thing bitfield at `thing+0x34` |
| 0x004d39d0 | CInfluenceMap__ResetRuntimeState | Instance | Clear runtime accumulators/cached fields and seed scalar defaults |
| 0x004d3a00 | CInfluenceMap__FreeRuntimeBuffers | Instance | Free runtime cell/object buffers and auxiliary allocations |
| 0x0048dcf0 | CInfluenceMap__Init | Instance | Initialize influence map member variables |

## Detailed Function Analysis

### CInfluenceMapManager__Load (0x0048b010)

**Purpose**: Load influence map data from level file stream.

**Behavior**:
1. Clears existing influence maps (destroys all objects)
2. Displays "Loading influence map" progress message
3. Reads version number (supports version 0 and 1)
4. For each region:
   - Reads position data (X, Y, Z or similar)
   - Allocates CInfluenceMap object (0xC4 bytes)
   - Initializes via CInfluenceMap__Init
   - Adds to linked list
5. Reads link data connecting regions
6. Calls PropagateDistances and DecayInfluence for initial setup

**File Format**:
- Version 0: 3 values per region (X, Y, Z), 2 values per link
- Version 1: 4 values per region, 3 values per link

**Debug Strings**:
- References InfluenceMap.cpp at line 0x46 (70) and 0x74 (116)
- References InfluenceMap.h at line 0x73 (115) for link allocation

---

### CInfluenceMap__ResetInfluence (0x0048b620)

**Purpose**: Reset influence tracking variables to default state.

**Behavior**:
Sets member variables at offsets:
- 0x9C = 0 (faction 0 current influence)
- 0xA0 = 0 (faction 0 accumulated influence)
- 0xA4 = 0 (faction 1 current influence)
- 0xA8 = 0 (faction 1 accumulated influence)
- 0xB8 = 0 (net influence ratio)
- 0xAC = 99999 (distance to faction 0 controlled region)
- 0xB0 = 99999 (distance to faction 1 controlled region)

**Calling Convention**: thiscall (ECX = this pointer)

---

### CInfluenceMapManager__SkipLoad (0x0048b660)

**Purpose**: Read and discard influence map data without creating objects.

**Behavior**: Reads the same data as Load but doesn't allocate or store anything. Used when influence maps aren't needed.

---

### CInfluenceMapManager__PropagateDistances (0x0048b7d0)

**Purpose**: Propagate distance-to-controlled-region values across the graph.

**Behavior**:
1. Calls CalculateInfluence(1) on all maps to initialize
2. Iterates 20 times (0x14 iterations):
   - For each map, examines neighbors
   - Updates distance values: `myDist = min(myDist, neighborDist + 1)`
   - Propagates both faction 0 distance (0xB0) and faction 1 distance (0xAC)
3. Schedules periodic callback (event 0x3E9 = 1001)

---

### CInfluenceMapManager__Update (0x0048b8e0)

**Purpose**: Main influence map update - called periodically to recalculate influence.

**Behavior**:
1. Resets all influence values via ResetInfluence
2. Iterates through game units (via FUN_00409760/FUN_00409780)
3. For each unit:
   - Checks unit flags to determine faction
   - Finds nearest influence map region
   - Adds unit's influence value to that region
4. Processes temporary influence sources
5. Propagates influence to empty regions (10 iterations, 0.1 decay factor)
6. Recalculates distances (20 iterations)
7. Calls CalculateInfluence on all regions
8. Schedules next update (event 1000)

**Unit Classification**:
- Flag 0x10: Skip unit
- Flag 0x20000000: Faction 1 (enemy)
- Flag 0x88400 mask: Additional exclusion criteria

---

### CInfluenceMapManager__DecayInfluence (0x0048bf70)

**Purpose**: Decay temporary influence sources over time.

**Behavior**:
1. Iterates through temporary influence list (at offset 0x18)
2. Decrements influence value by 0.2 each call
3. Removes sources when value reaches 0
4. Schedules next decay callback (event 0x3EA = 1002)

---

### CInfluenceMapManager__FindNearestMap (0x0048c000)

**Purpose**: Find the influence map region closest to given world coordinates.

**Parameters**:
- param_1 (float): X coordinate
- param_2 (float): Y coordinate
- param_3, param_4: Additional data stored in result

**Returns**: Allocates and returns a 12-byte result structure containing:
- [0]: Pointer to nearest CInfluenceMap
- [1]: param_3
- [2]: param_4

**Algorithm**:
Uses Manhattan distance: `|x - mapX| + |y - mapY| - radius`
- If distance < 0, point is inside region (immediate match)
- Otherwise tracks closest region

---

### CInfluenceMapManager__IsEmpty (0x0048c2d0)

**Purpose**: Check if the manager has no loaded influence maps.

**Returns**: true if count at offset 0x14 is less than 1

---

### CInfluenceMap__ScalarDelete (0x0048c2e0)

**Purpose**: Destructor wrapper called by delete operator.

**Behavior**: Calls Destructor, then conditionally frees memory.

---

### CInfluenceMap__Destructor (0x0048c300)

**Purpose**: Clean up influence map object.

**Behavior**: Calls cleanup functions for linked list and member data.

---

### CInfluenceMap__RemoveFromList (0x0048c390)

**Purpose**: Remove this influence map from the manager's linked list.

**Parameters**:
- param_1: Context/list pointer

**Behavior**: Sets flag at offset 0x70 to -1, clears bit in flags at offset 0x2C.

---

### CInfluenceMap__CalculateInfluence (0x0048c3b0)

**Purpose**: Calculate net influence value and determine control state.

**Parameters**:
- param_1 (int): If 0, set immediately; if 1, interpolate gradually

**Behavior**:
1. Calculates total influence: `faction0 + faction1`
2. If total > 0:
   - Net ratio = `(faction0 - faction1) / total`
   - Range: -1.0 (faction 1 control) to +1.0 (faction 0 control)
3. If total == 0:
   - Sums neighbor influence values
   - Sets control state based on neighbor majority
4. Control states at offset 0xBC:
   - 0 = Neutral
   - 1 = Faction 1 controlled
   - 2 = Faction 0 controlled
5. Interpolates value changes at 0.05 per update when param_1 != 0

**Member Offsets**:
- 0x9C: Faction 0 influence
- 0xA4: Faction 1 influence
- 0xB4: Current displayed influence ratio
- 0xB8: Target influence ratio
- 0xBC: Control state enum

---

### CInfluenceMap__Init (0x0048dcf0)

**Purpose**: Initialize a newly allocated CInfluenceMap object.

**Behavior**:
1. Copies 12 dwords (48 bytes) from template at 0x0067a790
2. Initializes member variables to default values
3. Sets vtable pointer to PTR_FUN_005dc1cc

---

### CInfluenceMap__AccumulateThingFlags (0x004d30d0)

**Purpose**: Increment influence counters from a tracked thing's flags.

**Behavior**:
- Reads `thing->flags` at `thing+0x34`.
- Increments internal counters when bits are set (`0x400`, `0x20000`, `0x40000`, `0x4000`, `0x800`).

---

### CInfluenceMap__ResetRuntimeState (0x004d39d0)

**Purpose**: Reset runtime influence-map working fields.

**Behavior**:
- Clears multiple accumulator/cached slots.
- Seeds scalar at `+0x50` to `1.0f`.

---

### CInfluenceMap__FreeRuntimeBuffers (0x004d3a00)

**Purpose**: Release runtime buffers and owned object sets.

**Behavior**:
- Frees per-cell pointer arrays and nested objects.
- Frees auxiliary allocations (`+0x80`, `+0x84`, `+0x98`) when present.
- Cleans runtime grids and patch buffers.
4. Clears string buffers at offsets 0xAC, 0x1AC, 0x2AC

**Calling Convention**: thiscall (ECX = this pointer)

## CInfluenceMap Structure (Partial)

```cpp
struct CInfluenceMap {
    /* 0x00 */ void* vtable;
    /* 0x04 */ // ... base class data
    /* 0x7C */ CInfluenceMap** neighbors;      // Linked list of neighbors
    /* 0x84 */ CInfluenceMap** neighborIter;   // Iterator for neighbors
    /* 0x8C */ float posX;                     // World X position
    /* 0x90 */ float posY;                     // World Y position
    /* 0x94 */ float posZ;                     // World Z position (or radius)
    /* 0x98 */ int   unknown98;
    /* 0x9C */ float faction0Influence;        // Current faction 0 influence
    /* 0xA0 */ float faction0Accumulated;      // Accumulated faction 0 influence
    /* 0xA4 */ float faction1Influence;        // Current faction 1 influence
    /* 0xA8 */ float faction1Accumulated;      // Accumulated faction 1 influence
    /* 0xAC */ int   distToFaction1;           // Steps to nearest faction 1 region
    /* 0xB0 */ int   distToFaction0;           // Steps to nearest faction 0 region
    /* 0xB4 */ float displayedInfluence;       // Smoothed influence for display
    /* 0xB8 */ float targetInfluence;          // Target influence ratio (-1 to 1)
    /* 0xBC */ int   controlState;             // 0=neutral, 1=faction1, 2=faction0
    // ... more fields up to 0xC4
};
```

## Event IDs

| ID | Hex | Purpose |
|----|-----|---------|
| 1000 | 0x3E8 | Main update callback |
| 1001 | 0x3E9 | Distance propagation callback |
| 1002 | 0x3EA | Influence decay callback |

## Global Data

| Address | Type | Purpose |
|---------|------|---------|
| 0x0067a748 | CInfluenceMapManager* | Global manager instance |
| 0x0067a790 | byte[48] | Default initialization template |
| 0x00672fd0 | float | Current game time |

## Related Files

- `InfluenceMap.h` - Header with class declarations and inline templates
- References allocation at line 0x73 (115) for link structures

## Notes

1. The influence system uses a graph structure where regions are connected by links
2. Distance propagation uses iterative relaxation (20 passes ensures convergence)
3. Influence values decay over time for temporary sources
4. The system distinguishes between two factions using bit flags on units
5. Manhattan distance is used for spatial queries (efficient for grid-like layouts)
