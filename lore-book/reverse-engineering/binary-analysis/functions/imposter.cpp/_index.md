# imposter.cpp Functions

> Source File: imposter.cpp | Binary: BEA.exe
> Debug Path: 0x0062d3f0 (`[maintainer-local-source-export-root]\imposter.cpp`)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Imposters are billboard sprites used to represent distant 3D objects efficiently. This is a common Level of Detail (LOD) optimization technique in games - when objects are far from the camera, they are rendered as simple 2D sprites instead of full 3D models, saving significant rendering resources.

The imposter system maintains a global linked list of imposter objects at `DAT_0067a678`. Each imposter is identified by a name string and several parameters (texture ID, dimensions, etc.).

Wave415 re-audited the CImposter queue head from fresh retail metadata, xrefs, instructions, and decompile exports. It hardened `CImposter__FindOrCreate` and `CImposter__AddToList`, corrected stale `0x00488aa0` CIBuffer ownership to `CImposter__GetFrameHeightForOwnerSlot`, and created two adjacent static-init table function boundaries at `0x00488ac0` and `0x00488ae0`. The available Stuart source snapshot does not include matching source bodies, so these are static retail/debug-path findings rather than exact source-body proof.

Wave598 later hardened the adjacent CDXEngine/DXImposter imposter-head cluster around the CImposter allocator path: `0x00542740 CDXEngine__InitLandscapeTextureTables`, `0x00542a30 CDXImposter__InitEntry`, `0x00542ee0 CDXEngine__BuildZRotationMatrix`, `0x00543300 CDXEngine__RenderImposterBillboardSet`, and `0x005438c0 CDXImposter__RenderAll` now have saved signatures/comments/tags. This links `CImposter__FindOrCreate` to the DXImposter entry initializer and records render-side companion rows without claiming runtime behavior or exact layouts. Wave599 then hardened `0x00543d90 CDXImposter__Deserialize` and `0x00543f50 CDXImposter__Create`, tying the serialized IMPS chunk load path to CImposter list insertion and frame-data allocation.

Wave753 static read-back (`unwind-continuation-wave753`, `wave753-readback-verified`) also hardened `0x005d2df0 Unwind@005d2df0` as a compiler-generated SEH unwind allocation-cleanup callback. DATA scope-table xref `0x0061bbc4` points at the body; instruction evidence calls `OID__FreeObject_Callback` on `*(EBP+0x1c)` with imposter.cpp debug path `0x0062d3f0`, line token `0x39`, and allocation/type value `0x29`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-221626_post_wave753_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004888f0 | CImposter__FindOrCreate | Find existing or create new imposter | ~384 bytes |
| 0x00488a70 | CImposter__AddToList | Add imposter to global linked list | ~48 bytes |
| 0x00488aa0 | CImposter__GetFrameHeightForOwnerSlot | Return frame-table height selected through owner vtable slot | ~32 bytes |
| 0x00488ac0 | ImposterGlobals__ClearTailSlots | Static-init table helper clears imposter-adjacent tail globals | ~32 bytes |
| 0x00488ae0 | ImposterGlobals__InitDefaultFrameData | Static-init table helper initializes default imposter frame/global data | ~64 bytes |

## Function Details

### CImposter__FindOrCreate (0x004888f0)

**Signature:** `void * __cdecl CImposter__FindOrCreate(char * name, int key_24, int key_40, int key_30, int key_44, int key_48, int key_34)`

Main imposter management function. Searches the global imposter list for an existing imposter matching the given name and parameters. If found, returns the existing imposter; otherwise allocates and initializes a new one.

**Algorithm:**
1. Iterate through linked list at `DAT_0067a678`
2. Compare name using `stricmp` (0x00568390, was `FUN_00568390`)
3. If name matches, verify all 6 parameters match (at offsets +0x24, +0x30, +0x34, +0x40, +0x44, +0x48)
4. If exact match found, return existing imposter
5. If name matches but parameters differ, log warning "strange lack of imposter"
6. If no match found, allocate new 0x4C byte structure via memory manager
7. Initialize fields and add to linked list
8. Return new imposter pointer

Wave598 addendum: the allocation path now has a saved call into `0x00542a30 CDXImposter__InitEntry`, which clears `+0x30/+0x38/+0x3c`, increments `0x008aa8bc`, and returns the input `0x4c` imposter object before the caller fills the remaining comparison fields.

**CImposter Structure (0x4C bytes):**
| Offset | Size | Field |
|--------|------|-------|
| 0x00 | 4 | Next pointer (linked list) |
| 0x04 | 32 | Name string (copied) |
| 0x24 | 4 | param2 value |
| 0x30 | 4 | param4 value |
| 0x34 | 4 | param7 value |
| 0x38 | 4 | Flags (zeroed on init) |
| 0x3C | 4 | Unknown |
| 0x40 | 4 | param3 value |
| 0x44 | 4 | param5 value |
| 0x48 | 4 | param6 value |

### CImposter__AddToList (0x00488a70)

**Signature:** `void __thiscall CImposter__AddToList(void * this)`

Adds an imposter to the global linked list. Uses thiscall convention (imposter pointer in ECX).

**Algorithm:**
1. If list is empty (`DAT_0067a678 == NULL`), set as head
2. Otherwise, traverse to end of list and append
3. Set imposter's next pointer to NULL

### CImposter__GetFrameHeightForOwnerSlot (0x00488aa0)

**Signature:** `float __thiscall CImposter__GetFrameHeightForOwnerSlot(void * this, void * owner)`

Wave415 corrects the stale `CIBuffer__GetEntryHeightByOwnerSlot` label. The observed caller is `CDXTrees__BuildTreeGeometry`; the helper uses `owner+0x08` vtable slot `+0x6c` to select a frame index and returns a frame-table float at `this+0x3c +0x10 + index*0x18`.

### ImposterGlobals__ClearTailSlots (0x00488ac0)

**Signature:** `void __cdecl ImposterGlobals__ClearTailSlots(void)`

Wave415 created this missing function boundary from static-init table data xref `0x006223b4`. The current body clears imposter-adjacent globals near `0x0067a6b8` through `0x0067a6c0`.

### ImposterGlobals__InitDefaultFrameData (0x00488ae0)

**Signature:** `void __cdecl ImposterGlobals__InitDefaultFrameData(void)`

Wave415 created this missing function boundary from static-init table data xref `0x006223b8`. The current body initializes imposter-adjacent default frame/global data near `0x0067a688` through `0x0067a6b4` with zero and `1.0` patterns.

## Global Data

| Address | Name | Purpose |
|---------|------|---------|
| 0x0067a678 | g_pImposterList | Head of imposter linked list |

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x0062d3f0 | "[maintainer-local-source-export-root]\imposter.cpp" | Debug path for assertions |
| 0x0062d410 | "strange lack of imposter" | Warning when name matches but params differ |

## Related Files

- **DXImposter.cpp** (0x006508cc) - DirectX-specific imposter rendering
- Console variables for imposter system:
  - `cg_renderimposters` (0x0062c8cc) - Toggle imposter rendering
  - `cg_imposterfadestart` (0x0063211c) - Distance at which imposters start to fade in
  - `cg_imposterfadeend` (0x006320dc) - Distance at which imposters stop fading in
  - `cg_forceobjectimposters` (0x00632164) - Force use of object imposters

## Wave598 CDXEngine/DXImposter Head (2026-05-19)

Wave598 records the current CImposter/DXImposter bridge at the saved-Ghidra evidence level:

| Address | Current saved Ghidra state | Imposter relevance |
| --- | --- | --- |
| `0x00542740` | `CDXEngine__InitLandscapeTextureTables` | Static-init helper returning the input table-owner pointer after initializing the observed `0x008aa4e8` owner path. |
| `0x00542a30` | `CDXImposter__InitEntry` | Called by `CImposter__FindOrCreate` for the newly allocated `0x4c` object before final field population. |
| `0x00542ee0` | `CDXEngine__BuildZRotationMatrix` | Engine-side helper used during imposter sample-ring setup; saved as a `__thiscall` row with explicit `this` after Ghidra read-back materialized ECX. |
| `0x00543300` | `CDXEngine__RenderImposterBillboardSet` | Engine-side billboard-set helper with `RET 0xc` proof for `view_context`, `alpha`, and `frame_index` stack arguments. |
| `0x005438c0` | `CDXImposter__RenderAll` | Global render pass called by `CDXEngine__Render`; gates on imposter globals, binds the atlas, renders via CVBufTexture paths, and restores sampler/state-cache values. |

Read-back evidence: corrected dry/apply/final dry reported `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=2 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `8` metadata rows, `8` tag rows, `9` xref rows, `888` instruction rows, and `8` decompile rows. Queue telemetry after Wave598 is `6093` total, `3072` commented, `3021` commentless, `1333` exact-undefined signatures, `1080` `param_N`, comment-backed proxy `3072/6093 = 50.42%`, and strict clean-signature proxy `3027/6093 = 49.68%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-164920_post_wave598_cdxengine_imposter_head_verified`. The next queue head is `0x00543d90 CDXImposter__Deserialize`.

This is static saved-Ghidra evidence only. Runtime imposter rendering, runtime tree billboard behavior, exact CImposter/CDXImposter/CDXEngine/matrix/vector/CVBufTexture/texture-atlas/global layouts, exact source identity, BEA patching, and rebuild parity remain unproven.

## Wave599 CDXImposter Deserialize/Create (2026-05-19)

Wave599 records the serialized IMPS chunk creation bridge at the saved-Ghidra evidence level:

| Address | Current saved Ghidra state | Imposter relevance |
| --- | --- | --- |
| `0x00543d90` | `CDXImposter__Deserialize(void * chunk_reader)` | Resource accumulator IMPS dispatch pushes the active chunk reader, then this helper reads atlas dimensions, texture atlas data, serialized imposter count, and CVBufTexture setup before marking the imposter system initialized. |
| `0x00543f50` | `CDXImposter__Create(void * chunk_reader)` | Called by `CDXImposter__Deserialize`; allocates a `0x4c` imposter, reads the serialized object payload, resolves the mesh/resource id, allocates frame data sized `+0x44 * +0x40 * 0x18`, calls `CImposter__AddToList`, and returns the object. |

Read-back evidence: dry/apply/final dry reported `updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=2 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `2` metadata rows, `2` tag rows, `2` xref rows, `514` instruction rows, and `2` decompile rows. Queue telemetry after Wave599 is `6093` total, `3074` commented, `3019` commentless, `1331` exact-undefined signatures, `1080` `param_N`, comment-backed proxy `3074/6093 = 50.45%`, and strict clean-signature proxy `3029/6093 = 49.71%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-171359_post_wave599_cdximposter_deserialize_create_verified`. The next queue head is `0x00544040 CDXEngine__ClearHudTextureSlots`.

This is static saved-Ghidra evidence only. Runtime imposter loading, runtime tree billboard behavior, exact CImposter/CDXImposter/CDXEngine/CVBufTexture/texture-atlas/frame-data/global layouts, exact source identity, BEA patching, and rebuild parity remain unproven.

## Key Observations

1. **Linked List Structure**: Imposters are managed as a simple singly-linked list with the head at a global address
2. **Name-Based Lookup**: Imposters are identified primarily by name string, with additional parameters for exact matching
3. **Lazy Creation**: Uses find-or-create pattern - only allocates new imposters when no existing match is found
4. **Parameter Mismatch Warning**: The "strange lack of imposter" message indicates the code expects parameters to be consistent for a given name
5. **Small Footprint**: The core imposter list helpers are compact; Wave415 also records adjacent frame/global helper evidence. Rendering logic remains mostly in DXImposter.cpp and related render paths.
6. **Claim Boundary**: This page records saved static Ghidra metadata and public-safe retail binary evidence. It does not prove runtime imposter rendering behavior, runtime tree rendering behavior, concrete layouts, exact source-body identity, local-variable/type recovery, or rebuild parity.

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
