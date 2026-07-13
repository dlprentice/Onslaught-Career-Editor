# oids.cpp - Object ID Factory System

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x004df520` → `CActor__dtor_base_Thunk` (was `CActor__dtor_base`). Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1210 measured anchor: unique-address accounting governs active current-risk progress. Wave1210 (`wave1210-waypoint-wingman-lifecycle-current-risk-review`) accounts for `6 Waypoint/Wingman lifecycle current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This comment/tag normalization corrected stale CThing__ctor_like_004f3640 wording to `CThing__dtor_base`, aligned wrapper comments with `CWaypoint__dtor_base` and `CWingmanStart__dtor_base`, and removed an accidental loader `destructor` tag with `tags_removed=1`; final dry updated=0 skipped=6. There was no rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consult used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; active current-risk progress is `1102/1179 = 93.47%`; remaining active focused work: 77; legacy additive counter is deprecated (`1133/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1127; live regenerated current focused candidates: 1127; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `6 xref rows`, `630 instruction rows`, and `6 decompile rows`. Anchors: `CWaypoint__scalar_deleting_dtor`, `CWingmanStart__scalar_deleting_dtor`, `CWaypoint__dtor_base`, `CWingmanStart__dtor_base`, `CWaypoint__Load`, `CWaypointPath__scalar_deleting_dtor`, `CDXMemoryManager__Free(&DAT_009c3df0, this)`, and `CSPtrSet__Remove`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-053028_post_wave1210_waypoint_wingman_lifecycle_current_risk_review_verified`. Active measurement files: `static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, and `reverse-engineering/binary-analysis/wave1108-current-risk-rank.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime waypoint behavior, runtime wingman-start behavior, exact CWaypoint/CWingmanStart/CWaypointPath layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

**Source File:** `[maintainer-local-source-export-root]\oids.cpp`
**Debug String Address:** `0x00630c20`
**Analysis Date:** December 2025

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

The `oids.cpp` file implements the **Object ID (OID) Factory System** - a central factory pattern for creating game objects based on numeric OID values. This is the core object instantiation system used throughout the game engine.

Wave909 engine/platform support static review (`engine-platform-support-static-review-wave909`) records the OID factory side of a static-coherent engine/platform/math/memory support core. OID anchors include `OID__CreateObject` and `OID__FreeObject_Callback`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-120420_post_wave909_engine_platform_support_static_review_verified`. Runtime object-factory behavior and exact layouts remain separate proof.

Wave761 static read-back (`unwind-continuation-wave761`, `wave761-readback-verified`) saved `0x005d3f53 Unwind@005d3f53` as a `void __cdecl Unwind@005d3f53(void)` compiler-generated SEH unwind allocation-cleanup callback tied to the oids.cpp debug path at `0x00630c20`. DATA scope-table xref `0x0061cabc` points at the body; instruction/decompile evidence calls `OID__FreeObject_Callback(*(EBP+0x4))` with line token `0x05` and allocation/type value `0x48`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-140318_post_wave761_unwind_continuation_verified`. Exact parent source-body identity, runtime cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

Wave800 gameplay object helpers (`gameplay-object-helpers-wave800`, `wave800-readback-verified`) retained `0x00449d40 OID__FreeObject_Callback` under the existing OID cleanup callback name and added saved static read-back comments/tags. The row has 657 current xrefs, mostly compiler unwind cleanup callbacks. Instruction evidence loads the stack pointer argument, loads memory-manager/context `0x009c3df0` into `ECX`, pushes the pointer, calls `CDXMemoryManager__Free` at `0x00549220`, and returns. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-070217_post_wave800_gameplay_object_helpers_verified`. Exact allocator provenance, runtime exception cleanup behavior, BEA patching, and rebuild parity remain deferred.

Wave1142 mixed score22 current-risk residual review (`wave1142-mixed-score22-current-risk-review`) accounted for `10 current-risk rows` and re-read the adjacent OID lifecycle rows `0x004bfd80 CSpawnerThng__scalar_deleting_dtor` and `0x004bfed0 CSpawnerThng__dtor_base`, then normalized active docs away from stale `CSpawnerThing` spelling to the saved Ghidra `CSpawnerThng` prefix. Current focused accounting is `261/1179 = 22.14%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 918; static closure is `6411/6411 = 100.00%`; static debt remains `0 / 0 / 0`. fresh Ghidra export, xref-site windows, static-shadow no-function boundary candidates, read-only review, no mutation. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-153716_post_wave1142_mixed_score22_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-145724_post_wave1141_cdxcompass_hud_current_risk_review_verified`. Runtime spawner cleanup behavior, exact layouts, source identity, and rebuild parity remain separate proof.

Wave1210 Waypoint/Wingman lifecycle current-risk review (`wave1210-waypoint-wingman-lifecycle-current-risk-review`) re-read OID-adjacent destructor rows `0x004bfd60 CWaypoint__scalar_deleting_dtor`, `0x004bfdc0 CWingmanStart__scalar_deleting_dtor`, `0x004bfe70 CWaypoint__dtor_base`, and `0x004bffa0 CWingmanStart__dtor_base`. The scalar-deleting wrappers call their matching destructor bodies and optionally free through `CDXMemoryManager__Free(&DAT_009c3df0, this)`. `CWaypoint__dtor_base` removes a populated `this+0x3c` owner/list link through `CSPtrSet__Remove` and delegates to `CThing__dtor_base`, correcting stale CThing__ctor_like_004f3640 wording; `CWingmanStart__dtor_base` removes the analogous `this+0x7c` link and delegates to `CComplexThing__dtor_base`. Fresh exports verified `6 xref rows`, `630 instruction rows`, and `6 decompile rows`; `tags_removed=1`; final dry updated=0 skipped=6. There was no rename, no signature change, no function-boundary change, and no executable-byte change occurred. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-053028_post_wave1210_waypoint_wingman_lifecycle_current_risk_review_verified`. Runtime waypoint behavior, runtime wingman-start behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Functions Found

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| `0x004bf090` | `OID__CreateObject` | ~2048 bytes | Main factory - creates objects by OID |
| `0x00449d40` | `OID__FreeObject_Callback` | ~16 bytes | Wave800 cleanup/free callback that forwards to `CDXMemoryManager__Free` |
| `0x004bfa60` | `OID__InitTargetData` | ~32 bytes | Initialize target tracking data |
| `0x004bfab0` | `OID__RenderWithState1BOverride` | ~560 bytes | Render wrapper that first lets `CUnit__RenderWithDistanceFade` handle the draw when `this+0x48` is present, otherwise temporarily disables render state `0x1b` around base `CThing__Render` |
| `0x004bfce0` | `CTree__scalar_deleting_dtor` | ~32 bytes | CTree slot-1 scalar-deleting destructor wrapper |
| `0x004bfd00` | `CActorBase__shared_scalar_deleting_dtor_004bfd00` | ~32 bytes | Shared actor-base slot-1 scalar-deleting destructor wrapper |
| `0x004bfd20` | `OID__InitBaseObject` | ~32 bytes | Initialize base object vtable |
| `0x004bfd40` | `CRocket__scalar_deleting_dtor` | ~32 bytes | CRocket slot-1 scalar-deleting destructor wrapper |
| `0x004bfd60` | `CWaypoint__scalar_deleting_dtor` | ~32 bytes | CWaypoint slot-1 scalar-deleting destructor wrapper |
| `0x004bfd80` | `CSpawnerThng__scalar_deleting_dtor` | ~32 bytes | SpawnerThng slot-1 scalar-deleting destructor wrapper |
| `0x004bfda0` | `CSphereTrigger__scalar_deleting_dtor` | ~32 bytes | CSphereTrigger slot-1 scalar-deleting destructor wrapper |
| `0x004bfdc0` | `CWingmanStart__scalar_deleting_dtor` | ~32 bytes | CWingmanStart slot-1 scalar-deleting destructor wrapper |
| `0x004bfde0` | `CEscapePod__scalar_deleting_dtor` | ~32 bytes | CEscapePod slot-1 scalar-deleting destructor wrapper |
| `0x004bfe00` | `CUnit__dtor_base_Thunk_004bfe00` | ~16 bytes | Jump thunk to CUnit destructor-base |
| `0x004bfe10` | `CRocket__dtor_base` | ~96 bytes | CRocket destructor-base body |
| `0x004bfe70` | `CWaypoint__dtor_base` | ~96 bytes | CWaypoint destructor-base body |
| `0x004bfed0` | `CSpawnerThng__dtor_base` | ~96 bytes | SpawnerThng destructor-base body |
| `0x004bff30` | `CComplexThing__dtor_base_Thunk_004bff30` | ~16 bytes | Jump thunk to CComplexThing destructor-base |
| `0x004bff40` | `CSphereTrigger__dtor_base` | ~96 bytes | CSphereTrigger destructor-base body |
| `0x004bffa0` | `CWingmanStart__dtor_base` | ~96 bytes | CWingmanStart destructor-base body |
| `0x004c0000` | `CEscapePod__dtor_base` | ~96 bytes | CEscapePod destructor-base body |
| `0x004f84e0` | `CUnit__dtor_base` | large body | CUnit destructor-base cleanup body |
| `0x0050ee90` | `CUnit__scalar_deleting_dtor` | ~32 bytes | CUnit scalar-deleting destructor wrapper referenced by DATA vtables |
| `0x004bf9e0` | `OID__InitInfluenceMapObject` | ~48 bytes | Initialize influence map object |
| `0x0044a850` | `OID__GetAttachmentOrOriginTransform` | ~224 bytes | Resolve attachment origin or base position |
| `0x0044a930` | `OID__GetAttachmentOrBaseOrientationMatrix` | ~128 bytes | Resolve attachment orientation matrix or base orientation |

**Total Functions:** 25 OID-owned functions documented/renamed, plus a Wave607 owner-correction note for the retired allocator row at `0x005490e0`.

## OID__CreateObject (0x004bf090)

This is the main object factory function. It takes an OID as a parameter and returns a newly allocated and initialized object of the corresponding type.

### Signature
```cpp
void * OID__CreateObject(int object_id);
```

### OID Mapping

The function uses a large switch statement to map OID values to object types:

| OID | Hex | Object Size | Object Type (Inferred) |
|-----|-----|-------------|------------------------|
| 3 | 0x03 | 0x63C (1596) | Complex game entity with squad support |
| 7 | 0x07 | 0x4C (76) | Simple map entity |
| 10 | 0x0A | 0x284 (644) | Medium entity |
| 11 | 0x0B | 0xE4 (228) | Base object type |
| 15 | 0x0F | 0x44C (1100) | Large entity |
| 16 | 0x10 | 0x10C (268) | Entity with callback system |
| 17 | 0x11 | 0xE4 (228) | Base object type |
| 18 | 0x12 | 0x40 (64) | Small map entity |
| 19 | 0x13 | 0x46C (1132) | Influence map entity |
| 21 | 0x15 | 0x210 (528) | Medium entity |
| 25 | 0x19 | 0x26C (620) | Medium entity |
| 26 | 0x1A | 0xD74 (3444) | Very large entity |
| 27 | 0x1B | 0x7C (124) | Small entity |
| 29 | 0x1D | 0xE0 (224) | Medium entity |
| 31 | 0x1F | 0x84 (132) | Small entity |
| 36 | 0x24 | 0x9C (156) | Entity with squad support |
| 37 | 0x25 | 0x80 (128) | Small entity |
| 38 | 0x26 | 0x440 (1088) | Influence map entity |
| 41 | 0x29 | 0x44C (1100) | Influence map entity |
| 43 | 0x2B | 0xE8 (232) | Entity with target tracking |

### Initialization Hierarchy

Objects are initialized through a class hierarchy:

```
FUN_004f3e10 (Base Thing Init)
    |
    +-- FUN_004f33e0 (Simple Thing Init)
    |       |
    |       +-- CMapWhoEntry__Invalidate
    |
    +-- FUN_004f7e90 (Complex Entity Init)
    |       |
    |       +-- CSPtrSet__Init (6x)
    |       +-- FUN_004f8140
    |       +-- CEulerAngles__ctor_from_FMatrix
    |
    +-- OID__InitBaseObject (Base Object Init)
    |       |
    |       +-- Sets vtable PTR_FUN_005d844c
    |
    +-- OID__InitInfluenceMapObject
    |       |
    |       +-- CInfluenceMap__Init
    |
    +-- OID__InitTargetData
            |
            +-- Sets target tracking fields
```

## Retired OID__AllocObject Label (Wave607)

Wave607 retired the older `OID__AllocObject` label at `0x005490e0`. Fresh saved Ghidra evidence shows the function is `CDXMemoryManager__Alloc`, not OID-owned:

- saved signature: `void * __thiscall CDXMemoryManager__Alloc(void * this, uint size, int mem_type, char * source_file, uint line)`
- `RET 0x10` proves four explicit stack arguments after ECX `this`.
- 1384 xrefs span OID/factory, mesh, script, sound, asset, frontend, and resource-loading paths, so the function is the global memory-manager allocation fan-out rather than an OID factory helper.
- The body dispatches through `this+0x10 + mem_type*4` and maps heap failures to localized fatal-error codes `0xcd`, `0xce`, `0xcf`, and `0xd0`.

OID construction still calls the global allocator through `OID__CreateObject`, but allocator ownership is now documented under [`MemoryManager.cpp`](../MemoryManager.cpp/_index.md). Exact OID object layouts, runtime factory behavior, and exact allocation categories remain open.

## Wave759 oids.cpp Unwind Continuation

Wave759 static read-back (`unwind-continuation-wave759`, `wave759-readback-verified`) saved comments/tags/signatures for oids.cpp-adjacent compiler-generated SEH unwind cleanup callbacks in the `0x005d3cb0 Unwind@005d3cb0` through `0x005d3d7e Unwind@005d3d7e` range. The tranche includes three oids.cpp allocation-cleanup rows using debug path `0x00630c20`, plus adjacent unit/object teardown rows through `CUnit__dtor_base`, `CSPtrSet__Clear`, `CGenericActiveReader__dtor`, and `CParticleManager__RemoveFromGlobalList_Thunk`.

Representative rows:

| Address | Evidence |
| --- | --- |
| 0x005d3cb0 | DATA xref `0x0061c974`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with line token `0x05` and allocation/type value `0x28`. |
| 0x005d3d68 | DATA xref `0x0061c9dc`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with line token `0x07` and allocation/type value `0x2b`. |
| 0x005d3d7e | DATA xref `0x0061c9e4`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with line token `0x05` and allocation/type value `0x2d`. |

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-130827_post_wave759_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Wave760 oids.cpp Unwind Continuation

Wave760 static read-back (`unwind-continuation-wave760`, `wave760-readback-verified`) saved comments/tags/signatures for the next oids.cpp-adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d3d94 Unwind@005d3d94` through `0x005d3f35 Unwind@005d3f35`. The tranche includes sixteen oids.cpp allocation-cleanup rows using debug path `0x00630c20`, line token `0x05`, and allocation/type values `0x2e`, `0x32`, `0x33`, `0x34`, `0x35`, `0x36`, `0x38`, `0x3b`, `0x3c`, `0x3d`, `0x3f`, `0x40`, `0x44`, `0x45`, `0x46`, and `0x47`.

Representative rows:

| Address | Evidence |
| --- | --- |
| 0x005d3d94 | DATA xref `0x0061c9ec`; `OID__FreeObject_Callback(*(EBP+0x4))` with allocation/type value `0x2e`. |
| 0x005d3daa | DATA xref `0x0061c9f4`; `OID__FreeObject_Callback(*(EBP+0x4))` with allocation/type value `0x32`. |
| 0x005d3dc0 | DATA xref `0x0061c9fc`; `OID__FreeObject_Callback(*(EBP+0x4))` with allocation/type value `0x33`. |
| 0x005d3e33 | DATA xref `0x0061ca34`; `OID__FreeObject_Callback(*(EBP+0x4))` with allocation/type value `0x38`. |
| 0x005d3ecd | DATA xref `0x0061ca74`; `OID__FreeObject_Callback(*(EBP+0x4))` with allocation/type value `0x44`. |
| 0x005d3f35 | DATA xref `0x0061caac`; `OID__FreeObject_Callback(*(EBP+0x4))` with allocation/type value `0x47`. |

The same Wave760 scope-table tranche also includes adjacent `0x005d3dd6 Unwind@005d3dd6` actor destructor-base cleanup, `0x005d3e20 Unwind@005d3e20` and `0x005d3f22 Unwind@005d3f22` complex-thing destructor-base cleanup, active-reader cleanup, and `0x005d3eeb Unwind@005d3eeb` particle-list unlink cleanup. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-133538_post_wave760_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## OID__InitTargetData (0x004bfa60)

Initializes target tracking data for entities that can be targeted.

### Signature
```cpp
void OID__InitTargetData(void * target_data);
```

### Memory Layout
```cpp
struct TargetData {
    int field_0;    // = 0
    int field_4;    // = 0xFFFFFFFF (-1)
    int field_8;    // = 0
    float field_C;  // = -1.0f (0xBF800000)
};
```

## OID__InitBaseObject (0x004bfd20)

Initializes the base object type with appropriate vtable pointers.

### Signature
```cpp
void * OID__InitBaseObject(void * object);
```

### Vtables Set
- Primary vtable: `PTR_FUN_005d844c`
- Secondary vtable (offset +8): `PTR_FUN_005d83d4`

## Wave459 Object Factory / Lifecycle Corrections

Wave459 saved static Ghidra evidence for the OID object factory and adjacent lifecycle wrappers on 2026-05-16.

| Address | Saved signature | Static behavior |
| --- | --- | --- |
| `0x004bf090` | `void * __cdecl OID__CreateObject(int object_id)` | Main retail OID object factory. It allocates known object sizes, calls family initializers, and returns null for unsupported/default cases. |
| `0x004bfa60` | `void __fastcall OID__InitTargetData(void * target_data)` | Clears target tracking fields to `0`, `0xffffffff`, `0`, and float bits `0xbf800000`. |
| `0x004bfab0` | `void __thiscall OID__RenderWithState1BOverride(void * this, uint render_flags)` | Vtable-slot render wrapper with one stack `render_flags` argument; disables render state `0x1b`, calls `CThing` render behavior, then restores the state. |
| `0x004bfd20` | `void * __fastcall OID__InitBaseObject(void * object)` | Initializes base object vtables at the ECX object pointer and returns the object pointer. |
| `0x004bfce0` | `void * __thiscall CTree__scalar_deleting_dtor(void * this, byte flags)` | CTree slot-1 scalar-deleting destructor wrapper. |
| `0x004bfd00` | `void * __thiscall CActorBase__shared_scalar_deleting_dtor_004bfd00(void * this, byte flags)` | Shared slot-1 scalar-deleting destructor wrapper used by three actor-base-like vtable references. |
| `0x004bfd40` | `void * __thiscall CRocket__scalar_deleting_dtor(void * this, byte flags)` | CRocket slot-1 scalar-deleting destructor wrapper. |
| `0x004bfd60` | `void * __thiscall CWaypoint__scalar_deleting_dtor(void * this, byte flags)` | CWaypoint slot-1 scalar-deleting destructor wrapper. |
| `0x004bfd80` | `void * __thiscall CSpawnerThng__scalar_deleting_dtor(void * this, byte flags)` | SpawnerThng slot-1 scalar-deleting destructor wrapper. |
| `0x004bfda0` | `void * __thiscall CSphereTrigger__scalar_deleting_dtor(void * this, byte flags)` | CSphereTrigger slot-1 scalar-deleting destructor wrapper. |
| `0x004bfdc0` | `void * __thiscall CWingmanStart__scalar_deleting_dtor(void * this, byte flags)` | CWingmanStart slot-1 scalar-deleting destructor wrapper. |
| `0x004bfde0` | `void * __thiscall CEscapePod__scalar_deleting_dtor(void * this, byte flags)` | CEscapePod slot-1 scalar-deleting destructor wrapper. |

This is saved static retail Ghidra evidence only. Runtime object construction, render-state behavior, cleanup behavior, exact object layouts, exact source identities, and rebuild parity remain unproven.

## Wave460 Object Cleanup / Destructor Corrections

Wave460 saved static Ghidra evidence for adjacent object destructor-base bodies and cleanup thunks on 2026-05-16.

| Address | Saved signature | Static behavior |
| --- | --- | --- |
| `0x004bfe00` | `void __fastcall CUnit__dtor_base_Thunk_004bfe00(void * this)` | Jump thunk to `CUnit__dtor_base` at `0x004f84e0`, reached by scalar-deleting and unwind cleanup paths. |
| `0x004bfe10` | `void __fastcall CRocket__dtor_base(void * this)` | CRocket destructor-base body; destroys the observed `+0xec` callback array and delegates to `CActor__dtor_base`. |
| `0x004bfe70` | `void __fastcall CWaypoint__dtor_base(void * this)` | Removes observed owner/list links through `CSPtrSet__Remove`, then delegates to `CThing__dtor_base`. |
| `0x004bfed0` | `void __fastcall CSpawnerThng__dtor_base(void * this)` | Removes observed owner/list links through `CSPtrSet__Remove`, then delegates to `CComplexThing__dtor_base`. |
| `0x004bff30` | `void __fastcall CComplexThing__dtor_base_Thunk_004bff30(void * this)` | Jump thunk to the canonical `CComplexThing__dtor_base` body at `0x004f3f00`. |
| `0x004bff40` | `void __fastcall CSphereTrigger__dtor_base(void * this)` | Clears the observed `+0x8c` pointer set, removes the `+0x7c` global-list node, then delegates to `CComplexThing__dtor_base`. |
| `0x004bffa0` | `void __fastcall CWingmanStart__dtor_base(void * this)` | Removes observed owner/list links through `CSPtrSet__Remove`, then delegates to `CComplexThing__dtor_base`. |
| `0x004c0000` | `void __fastcall CEscapePod__dtor_base(void * this)` | Removes the observed `+0xe0` global-list node, then delegates to `CActor__dtor_base`. |
| `0x004f84e0` | `void __fastcall CUnit__dtor_base(void * this)` | CUnit destructor-base body; resets vtable pointers, tears down observed linked unit/particle state, clears several pointer-set style lists, removes owner links, then delegates to `CActor__dtor_base`. |
| `0x0050ee90` | `void * __thiscall CUnit__scalar_deleting_dtor(void * this, byte flags)` | Slot-1 scalar-deleting destructor wrapper; calls `CUnit__dtor_base_Thunk_004bfe00`, optionally frees `this` when `flags & 1`, returns `this`, and ends with `RET 0x4`. |

This is saved static retail Ghidra evidence only. The nearby queued `0x004f84c0` CUnit slot-1 wrapper remains untouched, and runtime cleanup behavior, exact object layouts, exact source identities, and rebuild parity remain unproven.

## OID__InitInfluenceMapObject (0x004bf9e0)

Initializes objects that participate in the AI influence map system.

### Initialization
- Calls `CInfluenceMap__Init`
- Sets vtable to `PTR_LAB_005dc1c0`
- Clears field at offset `0x3BC` (0xEF * 4)

## Related Classes (from RTTI)

Based on RTTI strings found in the binary, these classes are likely created via the OID system:

- `CSquad`, `CNormalSquad`, `CRelaxedSquad` - Squad management
- `CInfluenceMap`, `CInfluenceNode` - AI influence system
- `CUnit`, `CBattleEngine`, `CMCMech` - Game units
- `CBuilding`, `CBuildingNamedMesh` - Structures
- `CCamera` variants - Camera types
- `CGuide`, `CAirGuide`, `CBoatGuide` - Pathfinding
- Various AI classes (`CUnitAI`, `CBoatAI`, `CBomberAI`, etc.)

## Attachment Transform Helpers (Wave 365)

`0x0044a850` and `0x0044a930` were signature/comment/tag hardened on 2026-05-13 after fresh metadata, decompile, xref, instruction, and tag read-back.

| Address | Saved signature | Static behavior |
| --- | --- | --- |
| `0x0044a850` | `void __thiscall OID__GetAttachmentOrOriginTransform(void * this, void * out_origin)` | Reads the attachment id at `this+0x0c`, falls back to base object position at `+0x1c`, or queries the owner vfunc at `+0x160` to populate `out_origin`. |
| `0x0044a930` | `void __thiscall OID__GetAttachmentOrBaseOrientationMatrix(void * this, void * out_matrix)` | Reads the attachment id at `this+0x0c`, falls back to base orientation matrix at `+0x3c`, or queries the owner vfunc at `+0x160` to populate `out_matrix`. |

These are saved static retail Ghidra facts only. Exact OID structure layout, attachment selector semantics, runtime targeting behavior, and rebuild parity remain unproven.

## Wave 366 Caller-Biased Correction

The older `OID__ReadHazardGridIfAboveTerrainDelta` label at `0x0044c780` is superseded by Wave 366 saved Ghidra evidence. Fresh read-back shows the checked callee is `CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta`, called through global FearGrid pointers with a 16-byte by-value world vector. The body samples static-shadow height, gates on the vector Z delta, and reads the FearGrid clearance plane at `this+0x4008`.

This correction only changes ownership of the checked callee body. OID/ballistic callers may still use this helper, but runtime OID/projectile behavior and adjacent caller identities remain open.

## Exception Handlers

The file contains 20 exception unwind handlers (`Unwind@005d3cb0` through `Unwind@005d3f53`) at addresses in the `0x005d3xxx` range. These are compiler-generated C++ exception handling code for proper object destruction on exception.

## Technical Notes

1. **Memory Management**: Uses custom `CDXMemoryManager__Alloc` with multiple memory pools
2. **Pool ID 5**: General game objects (most common)
3. **Pool ID 7**: Map-related objects (simpler entities)
4. **Vtable Pattern**: All objects have dual vtables at offsets 0 and 8
5. **thiscall Convention**: Most initialization functions use `__thiscall` (ECX = this pointer)

## Cross-References

The debug path string at `0x00630c20` is referenced from:
- 20 locations in `OID__CreateObject` (allocation calls with line numbers)
- 20 exception unwind handlers

## See Also

- `CSPtrSet__Init` - SPtrSet init helper (zeros head/tail/count)
- `CInfluenceMap__Init` - Influence map system
- `CDXMemoryManager__Alloc` - Global memory allocation fan-out
