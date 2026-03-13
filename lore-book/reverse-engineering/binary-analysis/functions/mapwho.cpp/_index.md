# mapwho.cpp - Spatial Partitioning System

**Source File:** `C:\dev\ONSLAUGHT2\mapwho.cpp`
**Debug Path Address:** `0x0062db88`
**Analysis Date:** December 2025

## Overview

The MapWho system is a spatial partitioning data structure used for efficient spatial queries in the game world. It implements a hierarchical quadtree with 5 levels (64x64 down to 4x4 sectors) for fast entity lookup by position or within a radius/line.

The system uses doubly-linked lists at each sector to store entries, allowing O(1) insertion/removal when the sector is known.

## Architecture

### Quadtree Structure
- **5 Levels**: Level 0 = 64x64, Level 1 = 32x32, Level 2 = 16x16, Level 3 = 8x8, Level 4 = 4x4
- Each sector contains a doubly-linked list of `CMapWhoEntry` objects
- Objects are placed at the appropriate level based on their radius (larger objects go to coarser levels)

### Key Classes
- **CMapWho**: Main spatial partitioning manager (offset 0x90 holds level pointers)
- **CMapWhoEntry**: Entry in the spatial grid (16 bytes, contains next/prev pointers, sector coords, level)

## Functions (22 total)

### CMapWho Class Methods

| Address | Name | Description |
|---------|------|-------------|
| `0x004919b0` | `CMapWho__Init` | Initialize quadtree structure with 5 levels |
| `0x00491930` | `CMapWho__Destroy` | Free all quadtree memory |
| `0x00491c50` | `CMapWho__GetLevelForRadius` | Determine appropriate quadtree level for object size |
| `0x00491cd0` | `CMapWho__AddEntry` | Add entry to appropriate sector's linked list |
| `0x00491d20` | `CMapWho__RemoveEntry` | Remove entry from its sector's linked list |
| `0x00491df0` | `CMapWho__SetupNextLevel` | Setup iterator for next quadtree level (radius query) |
| `0x00491ea0` | `CMapWho__GetFirstEntryWithinRadius` | Begin radius-based spatial query |
| `0x00492020` | `CMapWho__GetNextEntryWithinRadius` | Continue radius-based spatial query |
| `0x00492110` | `CMapWho__GetFirstEntryWithinLine` | Begin line-based spatial query (raycasting) |
| `0x004922f0` | `CMapWho__SetupLineLevel` | Setup iterator for line traversal at current level |
| `0x004924b0` | `CMapWho__AdvanceLineIterator` | Step line iterator to next sector |
| `0x004925a0` | `CMapWho__GetNextEntryWithinLine` | Continue line-based spatial query |
| `0x00492670` | `CMapWho__WorldToSector` | Convert world position to sector coordinates |
| `0x004926e0` | `CMapWho__Sort` | Re-sort entries (moves marked entries to end of list) |
| `0x00492860` | `CMapWho__DebugDrawSector` | Debug visualization of single sector |
| `0x00492950` | `CMapWho__DebugDraw` | Debug visualization of entire quadtree |

### CMapWhoEntry Class Methods

| Address | Name | Description |
|---------|------|-------------|
| `0x00491900` | `CMapWhoEntry__Init` | Initialize entry (zero next/prev pointers) |
| `0x00492ba0` | `CMapWhoEntry__SetPosition` | Set entry position and add to map |
| `0x00492c60` | `CMapWhoEntry__Invalidate` | Mark entry as invalid (level = -1) |
| `0x00492c70` | `CMapWhoEntry__RemoveFromMap` | Remove entry if valid |
| `0x00492c90` | `CMapWhoEntry__GetOwner` | Get owning object (this - 0xC offset) |
| `0x00492ca0` | `CMapWhoEntry__UpdatePosition` | Update position, re-add if sector changed |

## Data Structures

### CMapWho (partial)
```cpp
struct CMapWho {
    // ... other fields ...
    void** mLevelPointers;     // +0x90: Array of 5 level pointers
    int mLevelShifts[5];       // +0x94: Bit shifts for each level (6,5,4,3,2)
    int mLevelWidths[5];       // +0xA8: Grid width at each level
    int mLevelHeights[5];      // +0xBC: Grid height at each level
};
```

### CMapWhoEntry (16 bytes)
```cpp
struct CMapWhoEntry {
    CMapWhoEntry* mNext;    // +0x00: Next in sector list
    CMapWhoEntry* mPrev;    // +0x04: Previous in sector list
    short mSectorX;         // +0x08: Sector X coordinate
    short mSectorY;         // +0x0A: Sector Y coordinate
    int mLevel;             // +0x0C: Quadtree level (-1 = invalid)
};
```

### Sector Entry (8 bytes per sector)
```cpp
struct SectorEntry {
    int reserved;              // +0x00: Unknown/reserved
    CMapWhoEntry* mFirstEntry; // +0x04: Head of linked list
};
```

## Query Algorithms

### Radius Query
1. Calculate bounding box from center + radius
2. Start at finest level that can contain the radius
3. Iterate all sectors within bounding box at current level
4. If no more entries, move to next coarser level
5. Continue until all levels exhausted

### Line Query (Bresenham-style)
1. Calculate line direction and primary axis
2. Determine step counts based on line length vs cell size
3. Walk sectors along line using DDA algorithm
4. At each sector, also check adjacent sectors perpendicular to line
5. Descend through quadtree levels for each position

## Error Messages

| Address | Message |
|---------|---------|
| `0x0062db5c` | "FATAL ERROR: Mapwho construction gone wrong" |
| `0x0062dba8` | "WARNING: Object too big for map who system" |
| `0x0062dbd4` | "WARNING: GetNextEntryWithinRadius not set up" |
| `0x0062dc04` | "WARNING: GetNextEntryWithinLine not set up" |
| `0x0062dc30` | "FATAL ERROR: invalid sector in mapwho sort" |

## Technical Notes

1. **Object Size Limit**: Objects larger than the coarsest level cell size (64 units) trigger a warning
2. **Entry Ownership**: `CMapWhoEntry` is embedded at offset +0x0C in owning object (GetOwner returns `this - 0xC`)
3. **Sort Flag**: Bit 0x2000000 at offset +0x34 of owning object controls sort ordering
4. **Level Selection**: Smaller objects use finer levels for more precise queries; larger objects use coarser levels

## Usage Pattern

```cpp
// Typical usage for finding entities within radius
CMapWhoEntry* entry = mapWho->GetFirstEntryWithinRadius(x, y, z, radius, level);
while (entry) {
    CThing* thing = entry->GetOwner();
    // Process thing...
    entry = mapWho->GetNextEntryWithinRadius();
}
```

## Related Systems

- **CHeightField**: Terrain height queries
- **CThing**: Game objects that contain CMapWhoEntry
- **Collision System**: Uses MapWho for broad-phase collision detection
