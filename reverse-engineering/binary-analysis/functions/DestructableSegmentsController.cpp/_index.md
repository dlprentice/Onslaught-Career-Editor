# DestructableSegmentsController.cpp

> Destructible object segment management from BEA.exe

**Debug Path**: `C:\dev\ONSLAUGHT2\DestructableSegmentsController.cpp` (0x006287b4)

## Overview

This source file implements the destruction system for segmented objects (buildings, structures). It manages hierarchical segments that can be individually damaged and destroyed, with parent-child relationships determining destruction propagation.

## Functions

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x00444660 | CDestructableSegmentsController__Init | RENAMED | Initialize controller, allocate segment tracking |
| 0x004449c0 | CDestructableSegmentsController__CreateSegment | RENAMED | Factory for segment types (0-3) |
| 0x00444c10 | CDestructableSegmentsController__ProcessNode | RENAMED | Recursive node processor, determines segment types |
| 0x00443480 | CDestructableSegment__InitPrimary | RENAMED | Initialize primary/core segment |
| 0x004425a0 | CDestructableSegment__Init | RENAMED | Base segment initialization |
| 0x00442700 | CDestructableSegment__Register | RENAMED | Register segment with monitor system |
| 0x00442900 | CDestructableSegment__GetTotalHealth | RENAMED | Recursively calculate total health of segment tree |

## Details

### CDestructableSegmentsController__Init (0x00444660)

- **Purpose**: Initialize the destructible segments controller for a building/structure
- **Xref**: Found via debug path at 0x006287b4 (lines 0x184, 0x1a8)
- **Behavior**:
  - Checks if mesh exists for building, warns if not
  - Allocates segment tracking array based on mesh segment count
  - Iterates through "component" named mesh parts
  - Creates segment handlers for each component
  - Sets up monitor system for damage tracking
  - Calculates initial total health value
- **Warning strings**:
  - "Warning: No mesh for building" (0x006287ec)
  - "Warning: %s only has Primary component" (0x00628768)
  - "Warning: %s Can't find mesh part" (0x006286c0)
  - "Warning: %s Can't find segment" (0x00628714)
  - "ERROR: no behavour for unit" (0x006286a4)

### CDestructableSegmentsController__CreateSegment (0x004449c0)

- **Purpose**: Factory function to create different types of destructible segments
- **Xref**: Found via debug path at 0x006287b4 (lines 0x1e3, 0x1e8, 0x1ed, 0x1f2)
- **Parameters**:
  - param_1: Segment type (0-3)
  - param_2: Mesh/component data pointer
  - param_3: Parent segment (or NULL for root)
  - param_4: Health/scale value
- **Segment Types**:
  - Type 0: Primary component (0x50 bytes, vtable 0x005db06c)
  - Type 1: Standard segment (0x48 bytes, vtable 0x005db148)
  - Type 2: Leaf segment (0x54 bytes, vtable 0x005db114)
  - Type 3: End segment (0x54 bytes, vtable 0x005db0e0)
- **Warning strings**:
  - "WARNING: unknown Destroyable segment type" (0x00628890)

### CDestructableSegmentsController__ProcessNode (0x00444c10)

- **Purpose**: Recursively process mesh nodes to build segment hierarchy
- **Behavior**:
  - Traverses mesh hierarchy recursively
  - Determines segment type based on node name prefixes:
    - "CORE" prefix -> Type 0 (primary)
    - Has children -> Type 1 (standard)
    - "LE"/"LN" prefix -> Type 3 (end segment)
    - Otherwise -> Type 2 (leaf segment)
  - Links parent-child segment relationships
  - Accumulates health values up the tree
- **Warning strings**:
  - "Woops: %s Looks like you forgot..." (0x006288fc)
  - "WARNING: %s found second start component" (0x00628934)
  - "Warning: %s Child of CORE1 was..." (0x006288bc)

### CDestructableSegment__InitPrimary (0x00443480)

- **Purpose**: Initialize a primary (core) segment with extra tracking data
- **Behavior**:
  - Calls base CDestructableSegment__Init
  - Initializes additional fields at offsets 0x44-0x4c
  - Sets component index at offset 0x40
  - Sets vtable to 0x005db06c

### CDestructableSegment__Init (0x004425a0)

- **Purpose**: Base initialization for all segment types
- **Behavior**:
  - Sets up initial vtable (0x005d92d4, then 0x005db02c)
  - Initializes health multipliers (1.0, 1.0, -1.0 at offsets 0x0c-0x14)
  - Sets active flag at offset 0x1c
  - Registers with monitor system
  - Stores parent reference and health value

### CDestructableSegment__Register (0x00442700)

- **Purpose**: Register segment with the global monitor/tracking system
- **Behavior**: Wrapper around CSPtrSet__AddToHead (monitor registration)

### CDestructableSegment__GetTotalHealth (0x00442900)

- **Purpose**: Calculate total health of segment and all children recursively
- **Behavior**:
  - If segment is active and not destroyed, adds own health
  - Recursively traverses child list (offset 0x24)
  - Sums health values from entire subtree
  - Returns total as float

## Segment Hierarchy

```
CDestructableSegmentsController (this)
  +0x04: segment_array*     - Array of segment pointers
  +0x08: segment_count      - Number of segments
  +0x0c: root_segment*      - Root/primary segment
  +0x10: unit_data*         - Parent unit reference
  +0x18: total_health       - Cached total health
  +0x1c: health_scale       - Health scaling factor
  +0x20: component_count    - Number of components found

CDestructableSegment (base class)
  +0x00: vtable*
  +0x04: flags
  +0x08: segment_index
  +0x0c: health_mult_x (1.0)
  +0x10: health_mult_y (1.0)
  +0x14: health_mult_z (-1.0)
  +0x18: unknown
  +0x1c: is_active (1)
  +0x20: parent_segment*
  +0x24: child_list*
  +0x34: health_value
  +0x38: unknown
  +0x3c: controller*
```

## Vtables

| Address | Type | Description |
|---------|------|-------------|
| 0x005db06c | Primary | Core/primary segment (Type 0) |
| 0x005db148 | Standard | Standard segment with children (Type 1) |
| 0x005db114 | Leaf | Leaf segment, no children (Type 2) |
| 0x005db0e0 | End | End/terminal segment (Type 3) |
| 0x005db02c | Base | Base segment class |

## Related Systems

- **Monitor System**: CSPtrSet__Init (create), CSPtrSet__AddToHead (register) - tracks active game objects
- **Memory Allocation**: OID__AllocObject - allocator with debug tracking (file/line)
- **String Lookup**: FUN_004aa6b0, FUN_004aa820 - name/component string operations


## Additional Recovered Functions (Headless 2026-02-26)

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x004429a0 | CDestructableSegment__DispatchChildDestructionEvents | RENAMED | Child-destruction dispatch helper: immediate vs delayed event scheduling based on current segment state. |
| 0x00442a80 | CDestructableSegment__SetSubtreeActiveFlagRecursive | RENAMED | Recursively sets active flag (`+0x1C`) on a segment subtree. |
| 0x00442ac0 | CDestructableSegment__PropagateDamageToChildren | RENAMED | Child fanout helper invoking damage-style vfunc (`+0x0C`) with controller context. |
| 0x00443fc0 | CDestructableSegmentsController__Ctor | RENAMED | Constructor-like initialization for controller object (called from `CHiveBoss__Init`). |
| 0x00444000 | CDestructableSegmentsController__Dtor | RENAMED | Controller teardown helper freeing owned arrays and nested objects. |
| 0x004443f0 | CDestructableSegmentsController__TriggerCascadeIfThresholdExceeded | RENAMED | Health-threshold gate that triggers subtree activation + child damage cascade. |
| 0x00444450 | CDestructableSegmentsController__SetSegmentField0CByName | RENAMED | Name/tag-based segment lookup setter for field `+0x0C`. |
| 0x004444b0 | CDestructableSegmentsController__SetSegmentFields0C10ByName | RENAMED | Name/tag-based segment lookup setter for fields `+0x0C/+0x10` with health refresh. |
| 0x00444520 | CDestructableSegmentsController__FindSegmentByName | RENAMED | Returns tracked segment pointer by name/tag (used by `CHiveBoss__Init`). |
| 0x00444580 | CDestructableSegmentsController__SetAllSegmentsField0C | RENAMED | Bulk setter over all tracked segments for field `+0x0C`. |
| 0x004445b0 | CDestructableSegmentsController__SetSegmentActiveFlagByName | RENAMED | Name/tag-based segment lookup setter for active flag `+0x1C` with health refresh. |
| 0x004433f0 | CDestructableSegmentsController__AreCoreChildrenDestroyed | RENAMED | Core-child status gate used by cascade logic. |
| 0x00444030 | CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold | RENAMED | Indexed damage dispatch path with shared threshold/callback update. |
| 0x00444160 | CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold | RENAMED | Deduplicated random-damage burst pass with shared threshold update logic. |
| 0x004442d0 | CDestructableSegmentsController__GetSegmentField14ByIndex | RENAMED | Indexed getter for segment field `+0x14`. |
| 0x00444300 | CDestructableSegmentsController__GetSegmentField18ByIndex | RENAMED | Indexed getter for segment field `+0x18`. |
| 0x00444330 | CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive | RENAMED | Current subtree-health sum when active segments exist (else zero). |
| 0x00444370 | CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive | RENAMED | Root subtree-health query when active segments exist (else zero). |
| 0x004443b0 | CDestructableSegmentsController__GetCachedTotalHealthIfAnyActive | RENAMED | Cached total-health query when active segments exist (else zero). |
