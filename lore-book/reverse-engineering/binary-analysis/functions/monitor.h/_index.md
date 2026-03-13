# monitor.h / Monitor.h (Deletion Event System)

> Binary: `BEA.exe` (Steam build)
>
> Debug paths in `.rdata`:
> - `C:\dev\ONSLAUGHT2\monitor.h` @ `0x0062551c`
> - `C:\dev\ONSLAUGHT2\Monitor.h` @ `0x00622b80`

## Overview

This header-level system implements the **ActiveReader / Monitor** pattern used throughout the game to prevent dangling pointers.

At a high level:
- Objects that can be safely referenced inherit from a **monitor base** (`CMonitor` in Stuart's source naming).
- A `CActiveReader<T>` is a very small object (often just a 4-byte `mToRead` pointer).
- When an ActiveReader starts pointing at a monitor-derived object, it registers its **cell pointer** in the monitor's deletion list.
- When the monitored object dies, it iterates the deletion list and **nulls each cell** (`*cell = NULL`), matching `CGenericActiveReader::ToReadDied()`.

## Key Layout (Steam build)

Observed by RE (call sites + decompilation):
- `CMonitor + 0x04` is a lazily-allocated pointer to a `CSPtrSet` used as a deletion-event list.
- The deletion list stores **pointers to ActiveReader cells** (the address of `mToRead`), not a separate "listener object".

This matches Stuart's `activereader.h/.cpp` intent:
- `CGenericActiveReader::ToReadDied()` sets `mToRead = NULL`
- `CGenericActiveReader::SetReader()` removes from old monitor list and adds to new

## Functions (Steam build)

| Address | Name | Status | Notes |
|---------|------|--------|------|
| 0x00401040 | `CMonitor__AddDeletionEvent` | RENAMED | Allocates `CSPtrSet` at `monitor+0x04` (if needed) and adds `reader_cell` |
| 0x0042d9b0 | `CMonitor__DeleteDeletionEvent` | RENAMED | Removes `reader_cell` from `monitor+0x04` deletion list when present |
| 0x00401000 | `CGenericActiveReader__SetReader` | RENAMED | Unregister from old `mToRead+0x04`, assign, then register with new monitor |
| 0x00419a20 | `CMonitor__scalar_deleting_dtor` | RENAMED | Scalar deleting dtor wrapper: calls monitor shutdown then frees when delete-flag bit is set |
| 0x0044b1d0 | `CGenericActiveReader__dtor` | RENAMED | Unregister helper used before freeing an ActiveReader (removes from `mToRead+0x04`) |
| 0x00466120 | `CMonitor__ctor` | RENAMED | Monitor base constructor: sets vtable and initializes `monitor+0x04` to NULL |
| 0x0046dbc0 | `CMonitor__Shutdown_Thunk` | RENAMED | Thin compiler thunk that forwards to `0x004bac40` |
| 0x004bac40 | `CMonitor__Shutdown` | RENAMED | Monitor shutdown/destructor: iterates `monitor+0x04` and nulls each reader cell (`*cell = NULL`), then clears+frees the `CSPtrSet` |
| 0x004bacb0 | `CMonitor__Shutdown_Core` | RENAMED | Shared cleanup implementation (same null+clear+free behavior) used across many vtables |
| 0x0044e2c0 | `CMonitor__CheckSVFAnimationAndAdvanceState` | RENAMED | Checks current animation against `SVF` token and triggers monitor state-advance callback when matched |
| 0x0047d3b0 | `CMonitor__TryQueuePrefireAnimation` | RENAMED | Attempts to queue `prefire` animation token through animation-dispatch vfunc when state gate allows |
| 0x004ef120 | `CMonitor__SpawnParticleEffectFromIndexedListInHeightBand` | RENAMED | Walks indexed global list entry and emits particle effect only if sampled Z position is in configured height band |

### CMonitor__AddDeletionEvent (0x00401040)

**Purpose:** Register a reader cell with a monitor so the reader can be nulled on monitor deletion.

**Behavior (decompiled):**
1. If `*(monitor + 0x04) == NULL`:
   - allocates `0x10` bytes via `OID__AllocObject(0x10, 0x5e, "Monitor.h", 0x18)`
   - initializes it as an empty `CSPtrSet` (`CSPtrSet__Init`)
   - stores it into `monitor + 0x04`
2. Adds `reader_cell` to the set: `CSPtrSet__AddToHead(*(monitor+0x04), reader_cell)`

**Notes:**
- Many call sites inline equivalent logic instead of calling this helper directly.
- This function uses the `Monitor.h` debug path string (`0x00622b80`), while other call sites use `monitor.h` (`0x0062551c`).
- Some inlined sites initialize the newly allocated set via the thin wrapper `CSPtrSet__ctor` (`0x00505d00`): it calls `CSPtrSet__Init(this)` and returns `this`.

### CMonitor__DeleteDeletionEvent (0x0042d9b0)

**Purpose:** Remove a reader cell from a monitor's deletion list.

**Behavior (decompiled):**
1. If `*(monitor + 0x04) != NULL`:
   - call `CSPtrSet__Remove(*(monitor + 0x04), reader_cell)`
2. Return.

**Notes:**
- This is the explicit unregister companion to `CMonitor__AddDeletionEvent`.
- Called in cleanup paths (for example `CController__dtor`) and listener-removal flows.

### CGenericActiveReader__SetReader (0x00401000)

**Purpose:** The canonical "move this reader to a new target" helper.

Matches Stuart source (`references/Onslaught/activereader.cpp`):
- If `to_read == mToRead`: return
- If old `mToRead`: remove this reader cell from `old + 0x04`
- Assign `mToRead = to_read`
- If new `mToRead`: add this reader cell to `to_read + 0x04`

### CGenericActiveReader__dtor (0x0044b1d0)

**Purpose:** Unregister helper used before freeing/destroying an ActiveReader.

Behavior:
- If `mToRead != NULL` and `*(mToRead + 0x04) != NULL`, remove this reader cell from that set.

### CMonitor__ctor (0x00466120)

**Purpose:** Monitor base constructor.

Behavior:
- Assigns the monitor vtable.
- Initializes `this+0x04` (deletion-list pointer) to NULL.

### CMonitor__scalar_deleting_dtor (0x00419a20)

**Purpose:** Scalar deleting dtor wrapper for monitor-base semantics.

Behavior:
- Calls `CMonitor__Shutdown(this)` first.
- If `(free_flag & 1) != 0`, calls `OID__FreeObject(this)`.

### CMonitor__Shutdown_Thunk (0x0046dbc0)

**Purpose:** Compiler-generated thunk/wrapper.

Behavior:
- Forwards directly to `CMonitor__Shutdown(0x004bac40)`.

### CMonitor::Shutdown / Destructor (0x004bac40)

This is the missing lifecycle half of the system: when a monitor-derived object is shutting down, it walks the deletion list at `this+0x04` and nulls every registered ActiveReader cell.

Decompiled behavior summary:
1. If `this+0x04` (deletion list) is non-null:
   - Initialize iteration (`set->mIterator = set->mFirst`)
   - While iterating:
     - `cell = node->value` (value is a pointer to an ActiveReader cell)
     - `*cell = NULL` (prevents dangling pointer)
     - advance iterator to next node
   - `CSPtrSet__Clear(set)` and `OID__FreeObject(set)`
   - `this+0x04 = NULL`

This matches the internal source intent of `CGenericActiveReader::ToReadDied()` (set `mToRead = NULL`) applied to all registered cells.

### CMonitor__Shutdown_Core (0x004bacb0)

**Purpose:** Shared monitor cleanup implementation used by many class vtables.

Behavior:
- Performs the same deletion-list walk/null and set clear/free as `CMonitor__Shutdown`.
- Does **not** perform the vtable write seen at the start of `CMonitor__Shutdown(0x004bac40)`.

## Cross-References (Examples)

The deletion-list allocation debug path `monitor.h` (`0x0062551c`) is referenced from:
- `CController__Init` (controller monitor list usage)
- `CController__SetToControl` (registers a `CActiveReader<IController>` with `to_control+0x04`)
- `CDestructableSegmentsController__Init` (registers an embedded cell like `obj + 0x10`)
- `CPlayer__dtor` (unregisters embedded cells)
- `CSphereTrigger__Update` (uses monitor list allocation patterns)

## Open Questions

| Question | Why it matters |
|----------|----------------|
| Determine which classes actually embed `CMonitor` as a base (vs just using the `monitor+0x04` pattern) | Helps distinguish true monitor-derived objects from other structs that coincidentally have a `+0x04` pointer field |
