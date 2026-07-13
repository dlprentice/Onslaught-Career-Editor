# WorldMeshList.cpp Function Analysis

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x0050b9c0` signature/comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

**Source file:** `[maintainer-local-source-export-root]\WorldMeshList.cpp`
**Header file:** `[maintainer-local-source-export-root]\WorldMeshList.h`
**Analysis date:** December 2025

> **Queue status (2026-05-26):** Ghidra export-contract closure **6246/6246** (Wave1073: every exported function commented with clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

The `CWorldMeshList` class manages a linked list of mesh names used in the game world. It provides functionality for:
- Adding meshes by name (with recursive child mesh processing)
- Clearing all registered meshes
- Marking meshes as "used" for tracking purposes

This system appears to be used during world loading to track which meshes need to be instantiated or have already been processed.

## Global Data

| Address | Name | Purpose |
|---------|------|---------|
| `0x00855358` | `g_WorldMeshList` | Head of the mesh list (linked list) |
| `0x00855360` | `g_WorldMeshListIterator` | Current iterator position for traversal |

## Functions (3 total)

| Address | Name | Signature | Purpose |
|---------|------|-----------|---------|
| `0x0050d9e0` | `CWorldMeshList__Add` | `void __cdecl CWorldMeshList__Add(char * mesh_name)` | Add mesh by name recursively |
| `0x0050d9a0` | `CWorldMeshList__Clear` | `void __cdecl CWorldMeshList__Clear(void)` | Clear all entries and free memory |
| `0x0050dc20` | `CWorldMeshList__MarkUsed` | `void __cdecl CWorldMeshList__MarkUsed(char * mesh_name)` | Mark a mesh entry as used |

Wave1073 static re-audit (cworld-load-tail-review-wave1073) re-read all three saved WorldMeshList rows with no mutation: `0x0050d9a0 CWorldMeshList__Clear`, `0x0050d9e0 CWorldMeshList__Add`, and `0x0050dc20 CWorldMeshList__MarkUsed`. Fresh xrefs keep `0x0050d9e0 CWorldMeshList__Add` tied to `CWorld__LoadWorld`, recursive child-mesh handling, `CSpawnerThng__Init`, and `CScriptObjectCode__CollectSpawnThings`; `0x0050dc20 CWorldMeshList__MarkUsed` remains tied to `CUnit__Init`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified`. This is static Ghidra evidence only; runtime mesh loading/usage behavior, exact list-node/layout identity, and rebuild parity remain separate proof. Probe token anchor: Wave1073; cworld-load-tail-review-wave1073; 0x0050a870 CWorld__ClearSetArrays; 0x0050ac70 CWorld__LoadScriptEvents; 0x0050b520 CWorld__LoadWorldFile; 0x0050d6a0 CWorld__PushWorldTextSlot; 0x0050d9e0 CWorldMeshList__Add; 0x0050dcb0 CWorld__SpawnInitialThings; 0x0050df80 CWorldPhysicsManager__CreateThingByType; 0x00537c40; 0x004dfa47; 812/1408 = 57.67%; 1357/1560 = 86.99%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified; read-only review.

## Wave556 Static Read-Back (2026-05-18)

Wave556 saved Ghidra signatures/comments/tags for all three known `CWorldMeshList` helpers:

- `CWorldMeshList__Clear` (`0x0050d9a0`) drains `DAT_00855358`, removes each node from its `CSPtrSet`, frees the copied mesh-name string, and frees the 8-byte node.
- `CWorldMeshList__Add` (`0x0050d9e0`) takes one `mesh_name` pointer from `CWorld__LoadWorld`, `CSpawnerThng__Init`, `CScriptObjectCode__CollectSpawnThings`, and recursive self-calls; it deduplicates existing entries, resolves thing definitions through `DAT_008553fc +0xb0`, allocates the node and copied string, and recurses over child names through `DAT_008553f4`.
- `CWorldMeshList__MarkUsed` (`0x0050dc20`) takes one `mesh_name` pointer from `CUnit__Init`, scans `DAT_00855358`, and sets the node used flag at `+0x04` when matched.

This remains static retail-binary evidence only. Exact definition/list container layouts, child-link semantics, runtime spawn ordering, mesh ownership lifetime, BEA launch, patching, and rebuild parity remain unproven.

## Function Details

### CWorldMeshList__Add (0x0050d9e0)

**Purpose:** Adds a mesh to the world mesh list by name, recursively processing child meshes.

**Algorithm:**
1. Check if mesh name already exists in the list (strcmp loop)
2. If found, return early (no duplicates)
3. If not found, search the thing list for matching mesh name at offset `+0xB0`
4. Allocate new node (8 bytes) and copy mesh name string
5. Add node to list via `CSPtrSet__AddToHead`
6. Recursively process child meshes from offset `+0x4C` (child list)

**Called by:**
- `CSpawnerThng__Init` (0x004e3010) - When spawner initializes
- `CWorld__LoadWorld` (0x0050b9c0) - During world loading
- Self (recursive) - For child mesh processing
- `FUN_005392a0` (0x005392a0) - Unknown context

**Key observations:**
- Uses exception handling (SEH) with unwind handler at `0x005d5d00`
- Memory allocation via `OID__AllocObject` (custom allocator with debug info)
- Mesh name stored at offset `+0x00`, flags at offset `+0x04`

### CWorldMeshList__Clear (0x0050d9a0)

**Purpose:** Destroys all entries in the world mesh list, freeing allocated memory.

**Algorithm:**
1. Reset iterator to list head
2. Loop through all entries:
   - Unlink entry from list via `CSPtrSet__Remove` (returns list node to pool)
   - Call `OID__FreeObject` on mesh name string (free string)
   - Call `OID__FreeObject` on entry object (free entry)
3. Exit when list is empty

**Notes:**
- Simple cleanup function with no parameters
- Uses same globals as other WorldMeshList functions

### CWorldMeshList__MarkUsed (0x0050dc20)

**Purpose:** Finds a mesh by name and sets its "used" flag to 1.

**Algorithm:**
1. Reset iterator to list head
2. Loop through entries comparing mesh names (strcmp)
3. When found, set `entry[1] = 1` (used flag at offset +4)
4. Return

**Notes:**
- The "used" flag at offset +4 is checked by other functions to determine if a mesh has been processed
- Used for tracking which meshes need instantiation vs which already exist

## Mesh List Node Structure

```c
struct WorldMeshNode {
    char*  meshName;    // +0x00: Allocated string with mesh name
    uint32 usedFlag;    // +0x04: 0 = not used, 1 = used/processed
    // Next pointer managed by CSPtrSet
};
```

## Related Functions (not from WorldMeshList.cpp)

| Address | Name | Notes |
|---------|------|-------|
| `0x0050dcb0` | Unknown | Uses same globals but calls WorldPhysicsMap functions |
| `0x0050df80` | WorldPhysicsMap factory | Creates physics managers by type |
| `0x00549220` | Memory free | General memory deallocation |
| `0x005490e0` | Memory alloc | Custom allocator with debug file/line info |

## Cross-References

**Debug strings found:**
- `0x0063d488`: `"[maintainer-local-source-export-root]\WorldMeshList.cpp"` (line 0x2E = 46)
- `0x0063d464`: `"[maintainer-local-source-export-root]\WorldMeshList.h"` (line 0x11 = 17)

The line numbers in allocation calls suggest:
- Line 46 in .cpp: Node allocation in `Add()`
- Line 17 in .h: String allocation (possibly inline or macro in header)
