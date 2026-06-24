# mapwho.cpp - Spatial Partitioning System

Wave1195 current-risk update: Wave1195 (`wave1195-cmaptex-cmapwho-support-tail-current-risk-review`) accounts for `12 CMapTex/CMapWho support-tail score16 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. CMapWho/CMapWhoEntry rows are `CMapWhoEntry__Init`, `CMapWho__SetIteratorFromSectorHead`, `CMapWho__AdvanceIteratorAndGetCurrent`, `CMapWho__IsSectorCoordInBounds`, `CMapWho__SetupNextRadiusLevel`, `CMapWho__DebugDrawSector`, `CMapWho__DebugDraw`, and `CMapWhoEntry__Invalidate`; CMapTex context rows are `CMapTex__Reset`, `CMapTex__DownsampleTexture`, `CMapTex__CopyFromOther`, and `CMapTex__Deserialize`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=12 tags_added=132 missing=0 bad=0`, then `updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=12 tags_added=132 missing=0 bad=0`, then final dry updated=0 skipped=12. No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consult used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; expanded static surface remains `1560/1560 = 100.00%`; Wave1108 current focused accounting is `877/1179 = 74.39%`; current risk candidates: 6166; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 302; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `37 xref rows`, `561 instruction rows`, and `12 decompile rows`. Verified backup: `G:\GhidraBackups\BEA_20260606-200142_post_wave1195_cmaptex_cmapwho_support_tail_current_risk_review_verified`. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference; exact CMapTex/CMapWho/CMapWhoEntry/sector/texture/pixel layouts, exact source-body identity, runtime terrain texture behavior, runtime spatial-query behavior, runtime debug rendering behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1195; wave1195-cmaptex-cmapwho-support-tail-current-risk-review; 877/1179 = 74.39%; 12 CMapTex/CMapWho support-tail score16 current-risk rows; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 302; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=12 skipped=0; comment_only_updated=12; tags_added=132; final dry updated=0 skipped=12; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CMapTex__Reset; CMapTex__DownsampleTexture; CMapTex__CopyFromOther; CMapTex__Deserialize; CMapWhoEntry__Init; CMapWho__SetIteratorFromSectorHead; CMapWho__AdvanceIteratorAndGetCurrent; CMapWho__IsSectorCoordInBounds; CMapWho__SetupNextRadiusLevel; CMapWho__DebugDrawSector; CMapWho__DebugDraw; CMapWhoEntry__Invalidate; 0 / 0 / 0; 6411/6411 = 100.00%; 37 xref rows; 561 instruction rows; 12 decompile rows; G:\GhidraBackups\BEA_20260606-200142_post_wave1195_cmaptex_cmapwho_support_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.

Wave1166 current-risk update: Wave1166 (`wave1166-cmapwho-heightfield-spatial-query-current-risk-review`) re-read `20 CMapWho / CHeightField spatial-query current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. The MapWho rows cover initialization/destruction, radius query setup/iteration, line query setup/iteration, world-to-sector conversion, sorting, and entry position/owner/remove/update helpers; static anchors include `CMapWho__GetFirstEntryWithinRadius`, `CMapWho__GetFirstEntryWithinLine`, `CMapWho__WorldToSector`, `CMapWhoEntry__SetPosition`, `CMapWhoEntry__GetOwner`, and `CHeightField__TraceLineAgainstHeightfield`. Caller context includes `CWorld__FindFirstThingToHitLine` and `CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions`. Accounting is `624/1179 = 52.93%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 555; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; `0 / 0 / 0`; `6411/6411 = 100.00%`; `109 xref rows`; `1651 instruction rows`; focused threshold `15`; not Wave911 reconstruction. Verified backup: `G:\GhidraBackups\BEA_20260606-043614_post_wave1166_cmapwho_heightfield_spatial_query_current_risk_review_verified`. Runtime spatial-query behavior, terrain collision, line-of-sight, auto-aim, HLCollision behavior, debug rendering, exact CMapWho/CMapWhoEntry/sector layouts, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

**Source File:** `C:\dev\ONSLAUGHT2\mapwho.cpp`
**Debug Path Address:** `0x0062db88`
**Analysis Date:** December 2025

> **Queue status (2026-05-26):** Ghidra export-contract closure **6238/6238** (Wave1034: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

The MapWho system is a spatial partitioning data structure used for efficient spatial queries in the game world. It implements a hierarchical quadtree with 5 levels (64x64 down to 4x4 sectors) for fast entity lookup by position or within a radius/line.

The system uses doubly-linked lists at each sector to store entries, allowing O(1) insertion/removal when the sector is known.

## Wave755 mapwho Unwind Continuation (2026-05-23)

Wave755 static read-back (`unwind-continuation-wave755`, `wave755-readback-verified`) hardened `0x005d31c0 Unwind@005d31c0` as a compiler-generated SEH unwind allocation-cleanup callback. DATA scope-table xref `0x0061bef4` points at the body; instruction/decompile evidence calls `OID__FreeObject_Callback` on `*(EBP-0x20)` with mapwho.cpp debug path `0x0062db88`, line token `0x45`, and allocation/type value `0x44`. Verified backup: `G:\GhidraBackups\BEA_20260523-105815_post_wave755_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Wave1034 MapWho Spatial Query Re-Audit (2026-06-01)

Wave1034 (`mapwho-spatial-query-review-wave1034`) re-read the full 25-function `CMapWho` / `CMapWhoEntry` spatial-query cluster originally hardened by Wave428 and Wave429 with no mutation. Fresh exports verified `25` metadata rows, `25` tag rows, `119` xref rows, `1538` body-instruction rows, and `25` decompile rows. Queue closure remains `6238/6238 = 100.00%`; Wave911 focused progress advances to `660/1408 = 46.88%`; expanded static surface progress advances to `889/1493 = 59.54%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260601-054844_post_wave1034_mapwho_spatial_query_review_verified`. Runtime spatial-query behavior, runtime collision/render/tree/AI targeting behavior, concrete `CMapWho` / `CMapWhoEntry` layouts beyond observed offsets, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1034; mapwho-spatial-query-review-wave1034; 0x00491900 CMapWhoEntry__Init; 0x00491d80 CMapWho__SetIteratorFromSectorHead; 0x00491ea0 CMapWho__GetFirstEntryWithinRadius; 0x00492110 CMapWho__GetFirstEntryWithinLine; 0x00492670 CMapWho__WorldToSector; 0x00492860 CMapWho__DebugDrawSector; 0x00492ba0 CMapWhoEntry__SetPosition; 0x00492c90 CMapWhoEntry__GetOwner; 660/1408 = 46.88%; 889/1493 = 59.54%; 500/500 = 100.00%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-054844_post_wave1034_mapwho_spatial_query_review_verified; no mutation.

Wave1034 confirms the current saved MapWho cluster as a central static bridge for broad-phase radius queries, line queries, map/who entry tracking, debug-sector rendering, and dynamic-object spatial lookup. Representative callers include `CBattleEngine__HandleAutoAim`, `CMonitor__Process`, `CSpawnerThng__IsSpawnPositionClear`, `CUnitAI__IsCachedAnchorPointValid`, `CRepairPadAI__VFunc_11_UpdateDockCandidateReader`, `CAirGuide__AcquireNearestTargetReader`, `CWorld__FindFirstThingToHitLine`, `CDXTrees__BuildTreeGeometry`, `CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions`, `CDXEngine__Render`, `CThing__Init`, `CActor__Move`, and `CAtmospheric__Process`.

## Architecture

### Quadtree Structure
- **5 Levels**: Level 0 = 64x64, Level 1 = 32x32, Level 2 = 16x16, Level 3 = 8x8, Level 4 = 4x4
- Each sector contains a doubly-linked list of `CMapWhoEntry` objects
- Objects are placed at the appropriate level based on their radius (larger objects go to coarser levels)

### Key Classes
- **CMapWho**: Main spatial partitioning manager (offset 0x90 holds level pointers)
- **CMapWhoEntry**: Entry in the spatial grid (16 bytes, contains next/prev pointers, sector coords, level)

## Functions (25 tracked total)

### CMapWho Class Methods

| Address | Name | Description |
|---------|------|-------------|
| `0x004919b0` | `CMapWho__Init` | Initialize quadtree structure with 5 levels |
| `0x00491930` | `CMapWho__Destroy` | Free all quadtree memory |
| `0x00491c50` | `CMapWho__GetLevelForRadius` | Determine appropriate quadtree level for object size |
| `0x00491cd0` | `CMapWho__AddEntry` | Add entry to appropriate sector's linked list |
| `0x00491d20` | `CMapWho__RemoveEntry` | Remove entry from its sector's linked list |
| `0x00491df0` | `CMapWho__SetupNextRadiusLevel` | Setup iterator for next quadtree level (radius query) |
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

### Shared Iterator / Sector Helpers

| Address | Name | Description |
|---------|------|-------------|
| `0x00491d80` | `CMapWho__SetIteratorFromSectorHead` | Set the shared iterator current entry from a sector head. Corrected from stale collision-specific ownership in Wave428. |
| `0x00491d90` | `CMapWho__AdvanceIteratorAndGetCurrent` | Advance the shared iterator through entry next links and return the current entry. Corrected from stale collision-specific ownership in Wave428. |
| `0x00491da0` | `CMapWho__IsSectorCoordInBounds` | Validate sector x/y coordinates for level `0..4`. Corrected from broader entry-bounds wording in Wave428. |

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
5. **Source snapshot caveat**: The retail debug path names `C:\dev\ONSLAUGHT2\mapwho.cpp`, but `mapwho.cpp` is absent from the current Stuart source snapshot in this repo. Current Wave428/Wave429 corrections are binary-led static Ghidra evidence, not source-body parity.

## Wave428 Saved Ghidra Correction

Wave428 re-read metadata, decompile, xrefs, instructions, tags, and caller decompile context for twelve adjacent MapWho radius-query targets. It saved corrected signatures/comments/tags for:

- `0x00491900` `CMapWhoEntry__Init`
- `0x00491930` `CMapWho__Destroy`
- `0x004919b0` `CMapWho__Init`
- `0x00491c50` `CMapWho__GetLevelForRadius`
- `0x00491cd0` `CMapWho__AddEntry`
- `0x00491d20` `CMapWho__RemoveEntry`
- `0x00491d80` `CMapWho__SetIteratorFromSectorHead`
- `0x00491d90` `CMapWho__AdvanceIteratorAndGetCurrent`
- `0x00491da0` `CMapWho__IsSectorCoordInBounds`
- `0x00491df0` `CMapWho__SetupNextRadiusLevel`
- `0x00491ea0` `CMapWho__GetFirstEntryWithinRadius`
- `0x00492020` `CMapWho__GetNextEntryWithinRadius`

The correction supersedes the stale `CCollisionSeekingRound` owner on `0x00491d80` and `0x00491d90` because xrefs include collision, dynamic-unit rendering, and tree-geometry callers. Dry/apply/read-back verified `12` metadata rows, `12` tag rows, `62` xref rows, `2652` instruction rows, `12` target decompile exports, and `7` caller decompile exports. Focused probe status is `PASS`.

Runtime spatial-query behavior, exact concrete layouts beyond observed offsets, local variable names/types, exact source-body identity, BEA launch behavior, game patching, and rebuild parity remain open.

## Wave429 Saved Ghidra Correction

Wave429 continued the adjacent MapWho cluster and re-read metadata, decompile, xrefs, instructions, and tags for thirteen line-query and entry-position targets. It saved corrected signatures/comments/tags for:

- `0x00492110` `CMapWho__GetFirstEntryWithinLine`
- `0x004922f0` `CMapWho__SetupLineLevel`
- `0x004924b0` `CMapWho__AdvanceLineIterator`
- `0x004925a0` `CMapWho__GetNextEntryWithinLine`
- `0x00492670` `CMapWho__WorldToSector`
- `0x004926e0` `CMapWho__Sort`
- `0x00492860` `CMapWho__DebugDrawSector`
- `0x00492950` `CMapWho__DebugDraw`
- `0x00492ba0` `CMapWhoEntry__SetPosition`
- `0x00492c60` `CMapWhoEntry__Invalidate`
- `0x00492c70` `CMapWhoEntry__RemoveFromMap`
- `0x00492c90` `CMapWhoEntry__GetOwner`
- `0x00492ca0` `CMapWhoEntry__UpdatePosition`

The correction records `RET 0x20` for the first line-query helper's eight float line-start/line-end arguments, `RET 0xc` for `CMapWho__WorldToSector` and `CMapWhoEntry__SetPosition`, `RET 0x8` for `CMapWho__DebugDrawSector`, and `RET 0x4` for `CMapWhoEntry__UpdatePosition`. A first apply/read-back exposed the Ghidra `__thiscall` hidden-`this` nuance on two `CMapWhoEntry` methods; the script/probe were corrected and rerun serially before final read-back.

Dry/apply/read-back verified `13` metadata rows, `13` tag rows, `57` xref rows, `5473` instruction rows, and `13` target decompile exports. Focused probe status is `PASS`. The refreshed live queue reports `6043` functions, `1717` commented functions, `4326` commentless functions, `1833` undefined signatures, and `1792` `param_N` signatures; the private live Ghidra backup is verified at `G:\GhidraBackups\BEA_20260514_194325_post_wave429_mapwho_line_verified`.

Runtime line-query behavior, runtime entry tracking behavior, runtime debug rendering behavior, exact concrete layouts beyond observed offsets, local variable names/types, exact source-body identity, BEA launch behavior, game patching, and rebuild parity remain open.

## Usage Pattern

```cpp
// Typical usage for finding entities within radius
CMapWhoEntry* entry = mapWho->GetFirstEntryWithinRadius(query0, query1, query2, query3, radius);
while (entry) {
    CThing* thing = entry->GetOwner();
    // Process thing...
    entry = mapWho->GetNextEntryWithinRadius();
}
```

The current retail call shape is `RET 0x14` for the first radius-query helper. The exact semantic labels for the four query fields remain layout/type work; do not read the example as source-body or runtime behavior proof.

## Related Systems

- **CHeightField**: Terrain height queries
- **CThing**: Game objects that contain CMapWhoEntry
- **Collision System**: Uses MapWho for broad-phase collision detection
