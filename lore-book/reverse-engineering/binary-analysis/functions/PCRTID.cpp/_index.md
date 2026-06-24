# PCRTID.cpp - PC Runtime ID System

**Source File:** `C:\dev\ONSLAUGHT2\PCRTID.cpp`
**Debug String Address:** `0x0063e284`

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

PCRTID.cpp implements the PC Runtime ID factory system - a central factory pattern that creates different types of runtime objects used for rendering game entities. The "CRT" prefix stands for "C Runtime" objects, which are platform-specific rendering wrappers.

## Wave796 Final Signature Debt (2026-05-24)

Wave796 signature debt (`signature-debt-wave796`, `wave796-readback-verified`) saved the final CRT/library param-name hardening rows that the current owner docs place here: `0x00564486 CRT__FmodReduceCore` and ``0x00574a99 `vector_constructor_iterator'``. Saved signatures are `int __cdecl CRT__FmodReduceCore(int divisor_mantissa_low, uint divisor_mid_bits, int divisor_sign_exp_high)` and ``void __stdcall `vector_constructor_iterator'(void * base, uint element_size, int element_count, _func_void_ptr_void_ptr * constructor)``. The pass made no renames, no function-boundary changes, and no executable-byte changes; queue telemetry after the pass is 0 exact-undefined signatures, 0 param_N signatures, and strict clean-signature proxy `5544/6098 = 90.92%`. Verified backup: `G:\GhidraBackups\BEA_20260524-050846_post_wave796_final_param_signature_debt_verified`. Exact Visual Studio CRT source identity, custom FPU stack behavior, runtime C++ array construction behavior, BEA patching, and rebuild parity remain deferred.

## Functions Found

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| `0x00516580` | `PCRTID__CreateObject` | ~0x90 | Factory function - creates CRT objects by type ID |

## Type ID Mapping

The factory function uses a switch statement on a type ID parameter to create different object types:

| Type ID | Class | Size (bytes) | Vtable | Notes |
|---------|-------|--------------|--------|-------|
| 1 | `CRTMesh` | 0x50 (80) | `0x005deb1c` | Base mesh rendering object |
| 2 | `CRTTree` | 0x34 (52) | `0x005deb9c` | Tree rendering (smaller, specialized) |
| 4 | `CRTBuilding` | 0x5c (92) | `0x005de9c0` | Building rendering (inherits CRTMesh) |
| 5 | `CRTCutscene` | 0x28 (40) | `0x005dea38` | Cutscene rendering object; Wave489 verified constructor/vtable cluster |

**Note:** Type ID 3 is not implemented in this factory.

## Class Hierarchy

```
CRTMesh (base class, 0x50 bytes)
  |
  +-- CRTBuilding (derived, 0x5c bytes)
```

`CRTTree` and `CRTCutscene` appear to be independent classes (not derived from CRTMesh). Wave489 shows `CRTCutscene` uses adjacent `CRenderThing` base helpers, and Wave497 shows `CRTTree` uses the same render-helper family plus tree-resource getters. The exact retail inheritance/source identity remains bounded static evidence rather than rebuild-grade class recovery.

Wave1046 (`renderthing-crttree-review-wave1046`) re-read the shared render-object helper family created by the PCRTID runtime object classes with no mutation. Fresh evidence reconfirmed `0x004db880 CRenderThing__ForwardSlot26ToChildSlot68`, `0x004dbb80 CRenderThing__VFunc_07_ClearRenderOutputs`, `0x004dbbe0 CRenderThing__VFunc_08_ClearVec3`, `0x004dbd20 CRenderThing__dtor`, `0x004dbd50 CRenderThing__scalar_deleting_dtor`, `0x004dd960 CRTTree__VFuncSlot02_BuildRenderOutputs`, `0x004de050 CRTTree__VFuncSlot06_GetResourceScalar164`, and `0x004de060 SharedVFunc__ReturnResourceField150_004de060` across `0x005dea38`, `0x005deaac`, `0x005deb1c`, and `0x005deb9c`. Queue closure remains `6246/6246 = 100.00%`; expanded static surface progress is `993/1509 = 65.81%`. Verified backup: `G:\GhidraBackups\BEA_20260601-120449_post_wave1046_renderthing_crttree_review_verified`. Runtime render behavior, exact source virtual names, exact CRT object layouts, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Related Functions (by vtable)

### CRTMesh (Type ID 1)
| Address | Name | Purpose |
|---------|------|---------|
| `0x004dc370` | `CRTMesh__Init` | Initialize mesh |
| `0x004dc950` | `CRTMesh__Destructor` | Destructor |
| `0x004dcb00` | `CRTMesh__FreePoseData` | Free pose data |
| `0x004dcb70` | `CRTMesh__ScalarDeletingDestructor` | Scalar deleting destructor |
| `0x004dd0c0` | `CRTMesh__CleanupAllEffects` | Cleanup effects |
| `0x004dd6b0` | `CRTMesh__SetQualityLevel` | Set quality level |
| `0x004dd770` | `CRTMesh__GetQualityLevel` | Get quality level |

### CRTTree (Type ID 2)
| Address | Name | Purpose |
|---------|------|---------|
| `0x004dd7b0` | `CRTTree__Init` | Initialize tree render object, resolve tree/resource pointers, cache resource scalars |
| `0x004dd850` | `CRTTree__VFuncSlot03_UpdateVisibilityState` | Visibility/imposter state update path gated by `DAT_0083cd58` |
| `0x004dd960` | `CRTTree__VFuncSlot02_BuildRenderOutputs` | Build render output records and animated/render helper state |
| `0x004ddfd0` | `CRTTree__Destructor` | Destructor |
| `0x004de050` | `CRTTree__VFuncSlot06_GetResourceScalar164` | Compact getter for tree resource float at `+0x164` |
| `0x004de060` | `SharedVFunc__ReturnResourceField150_004de060` | Shared CRTMesh/CRTTree resource field getter for `+0x150` |
| `0x004de080` | `CRTTree__ScalarDeletingDestructor` | Scalar deleting destructor wrapper |

### CRTBuilding (Type ID 4)
| Address | Name | Purpose |
|---------|------|---------|
| `0x004db850` | `CRTBuilding__Destructor` | Destructor (calls CRTMesh__Destructor) |

### CRTCutscene (Type ID 5)
| Address | Name | Purpose |
|---------|------|---------|
| `0x004dbb60` | `CRTCutscene__CRTCutscene` | Constructor |
| `0x004dbc30` | `CRTCutscene__scalar_deleting_dtor` | Scalar deleting destructor wrapper |
| `0x004dbc50` | `CRTCutscene__dtor` | Destructor implementation |
| `0x004dbd80` | `CRTCutscene__Init` | Initialize cutscene |
| `0x004dbe50` | `CRTCutscene__Activate` | Resolve saved element names to mesh pointers |
| `0x004dbe90` | `CRTCutscene__Reset` | Reset cutscene |
| `0x004dbec0` | `CRTCutscene__RenderCurrent` | Active/current-index gated render path |
| `0x004dbf70` | `CRTCutscene__SetCurrentIndex` | Set current index |
| `0x004dbf80` | `CRTCutscene__GetCurrentMesh` | Active/current-index mesh getter |
| `0x004dbfb0` | `CRTCutscene__GetDefaultScalar` | Default scalar getter |
| `0x004dbfc0` | `CRTCutscene__GetCurrentMeshEntryValue` | Current mesh entry-value lookup |
| `0x004dbff0` | `CRTCutscene__BuildCurrentFrameOutputs` | Current-frame output builder |

## RTTI Type Names

Found at these addresses (MSVC mangled names):
- `0x00631db8`: `.?AVCRTMesh@@`
- `0x00631dd0`: `.?AVCRTBuilding@@`
- `0x00631e18`: `.?AVCRTCutscene@@`
- `0x006321b0`: `.?AVCRTTree@@`

## Factory Function Details

### PCRTID__CreateObject (0x00516580)

```c
void* PCRTID__CreateObject(int typeId)
{
    switch(typeId) {
    case 1:  // CRTMesh
        obj = MemAlloc(0x50, 0x3b, "PCRTID.cpp", 0x11);
        if (obj) {
            obj->next = NULL;
            obj->vtable = &CRTMesh_vtable;
        }
        return obj;

    case 2:  // CRTTree
        obj = MemAlloc(0x34, 0x3b, "PCRTID.cpp", 0x12);
        if (obj) {
            obj->next = NULL;
            obj->vtable = &CRTTree_vtable;
        }
        return obj;

    case 4:  // CRTBuilding
        obj = MemAlloc(0x5c, 0x3b, "PCRTID.cpp", 0x14);
        if (obj) {
            obj->next = NULL;
            obj->vtable = &CRTBuilding_vtable;
        }
        return obj;

    case 5:  // CRTCutscene
        obj = MemAlloc(0x28, 0x3b, "PCRTID.cpp", 0x15);
        if (obj) {
            return CRTCutscene__CRTCutscene();
        }
        return NULL;
    }
    return NULL;
}
```

**Memory Allocation Tags:**
- Pool ID: `0x3b` (59) - Likely a specific memory pool for runtime objects
- Line numbers in source: 0x11 (17), 0x12 (18), 0x14 (20), 0x15 (21)

## Callers (17 call sites)

The factory is called from various game systems:
- `CBattleEngine__Init` (0x00404dd0) - 2 calls
- `CMissile__Init` (0x004baae0)
- `CUnit__Init` (0x004f86d0)
- Various other initialization functions

## Technical Notes

1. **Common Object Layout**: All CRT objects appear to share a common header:
   - Offset 0x00: vtable pointer
   - Offset 0x10: next pointer (linked list, set to NULL on creation)

2. **Exception Handling**: The factory uses SEH (Structured Exception Handling) to protect allocations.

3. **CRTBuilding Inheritance**: `CRTBuilding__Destructor` explicitly calls `CRTMesh__Destructor`, confirming inheritance.

4. **CRTTree Vtable Recovery**: Wave497 verifies CRTTree vtable `0x005deb9c` slots 0, 1, 2, 3, 4, 6, 14, 17, 20, and 26 as function-backed saved static evidence. Slot 28 still points at non-code address `0x00616840` and remains deferred.

5. **CRTCutscene Special Case**: Type ID 5 is unique - it calls the actual constructor `CRTCutscene__CRTCutscene()` after allocation, while other types just set the vtable. Wave489 verifies that constructor installs vtable `0x005dea38` and that the vtable's RTCutscene/CRenderThing/shared helper slots now have saved function objects and comments.

## Discovery Date

December 2025 - Ghidra MCP analysis; Wave497 CRTTree update added 2026-05-17.

## Wave1151 Current-Risk Tag Normalization

Wave1151 tag-only normalization covers CRT runtime helper rows `0x0055e3ea CRT__FpuIntrinsicDispatch2Thunk`, `0x00564a0b CRT__SpawnSearchPathWithFallbackExtensions`, and `0x00569cb8 CRT__FloatDispatchAmsgExitCode2Thunk` as score21 current-risk rows. It preserves their compiler-runtime/path/float-dispatch evidence and adds Wave1151/current-risk tags only. Verified backup: `G:\GhidraBackups\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
