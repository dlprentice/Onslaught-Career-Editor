# MCBuggy.cpp Functions

> Source File: MCBuggy.cpp | Binary: BEA.exe
> Debug Path Address: 0x0062dc80 (`C:\dev\ONSLAUGHT2\MCBuggy.cpp`)
> RTTI: `.?AVCMCBuggy@@` at 0x0062dc70

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`CMCBuggy` is the buggy/wheeled-vehicle motion controller neighborhood. Current retail evidence is binary-led because `MCBuggy.cpp` is absent from the current Stuart source snapshot. The saved Ghidra metadata covers wheel-base and wheel-motion setup/update, shared matrix/vector helpers used by the update path, mesh-part token filters, target-value sampling, and a nested/shared destructable-segment motion-controller vtable after the primary `CMCBuggy` vtable.

This page records static saved-Ghidra evidence only. It does not prove runtime wheel behavior, concrete class layouts, exact local names/types, BEA launch behavior, game patching, or rebuild parity.

## Wave800 Gameplay Object Helper (2026-05-24)

Wave800 gameplay object helpers static read-back (`gameplay-object-helpers-wave800`, `wave800-readback-verified`) hardened `0x00445010 CMCBuggy__GetTargetValueOrFallback` as `float __thiscall CMCBuggy__GetTargetValueOrFallback(void * this, int target_id)`. `RET 0x4` proves one explicit stack argument after `ECX`, and the direct xref is `CDestructableSegmentsMotionController__ApplyRumbleTransform` at `0x00494cfa`. The body reads a target table at `this+4` using `target_id`, checks a candidate vfunc at `+0x14`, returns candidate field `+0x44` as an x87 float, or falls back to global float `0x005d856c`. If `target_id` is nonzero and no direct entry exists, it follows the owner/controller path at `this+0x10/+0x30`, dispatches vfunc `+0x24`, and probes the returned `+0x160` target table.

Verified backup: `G:\GhidraBackups\BEA_20260524-070217_post_wave800_gameplay_object_helpers_verified`. This is saved static retail Ghidra evidence only; exact field names, concrete target-record layout, runtime rumble/target behavior, BEA patching, and rebuild parity remain deferred.

## Wave755 MCBuggy Unwind Continuation (2026-05-23)

Wave755 static read-back (`unwind-continuation-wave755`, `wave755-readback-verified`) saved comments/tags/signatures for six MCBuggy.cpp-adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d3200 Unwind@005d3200` through `0x005d3280 Unwind@005d3280`. Evidence includes MCBuggy.cpp debug path `0x0062dc80`, DATA scope-table xrefs `0x0061bf44` through `0x0061bfc4`, two `OID__FreeObject_Callback` allocation-cleanup rows, one `CMCBuggy__ProfileEnd` profiler epilogue row, and two `CMotionController__dtor_base` rows. Verified backup: `G:\GhidraBackups\BEA_20260523-105815_post_wave755_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

| Address | Scope-table xref | Static read-back evidence |
| --- | --- | --- |
| `0x005d3200` | `0x0061bf44` | `OID__FreeObject_Callback(*(EBP+0x4))`, MCBuggy.cpp line token `0x1b`, allocation/type value `0x4e`. |
| `0x005d3216` | `0x0061bf4c` | `OID__FreeObject_Callback(*(EBP+0x4))`, allocation/type value `0x52`. |
| `0x005d3240` | `0x0061bf74` | `CMCBuggy__ProfileEnd(EBP-0x120)`. |
| `0x005d3260` | `0x0061bf9c` | `CMotionController__dtor_base(*(EBP-0x20))`. |
| `0x005d3280` | `0x0061bfc4` | `CMotionController__dtor_base(*(EBP-0x10))`. |

## Wave430 Saved Ghidra Correction

Wave430 re-read metadata, decompile, xrefs, instructions, strings, and vtable slots for the `CMCBuggy` / wheel-motion neighborhood. It corrected stale owner labels, fixed stack cleanup signatures, and hardened comments/tags for fifteen targets:

| Address | Current saved state | Evidence |
| --- | --- | --- |
| `0x00493020` | `CMCBuggy__CMCBuggy` | `RET 0x4`; constructor calls the base motion-controller constructor, installs vtable `0x005dc250`, stores the owner/model pointer at `+0x08`, clears wheel buffers, and seeds `+0x3c` with `-1.0f`. |
| `0x00493080` | `CMCBuggy__scalar_deleting_destructor` | `RET 0x4`; calls the local destructor and conditionally frees `this` when delete flags bit `0` is set. |
| `0x004930a0` | `CMCBuggy__destructor` | Register-only body restores vtable `0x005dc250`, frees observed wheel/motion buffers, and calls the base motion-controller destructor. |
| `0x00493180` | `CMCBuggy__SetFieldC0` | `RET 0x4`; writes the single stack value to CMCBuggy offset `+0xc0`. |
| `0x00493190` | `CMCBuggy__Init` | `RET 0x4`; lazily counts `WheelBase` slots, allocates wheel buffers, resolves `WheelMotion`, seeds contact sentinels, and builds cached wheel motion pose data. |
| `0x004934f0` | `CMCBuggy__UpdateWheel` | `RET 0x50`; twenty stack arguments after `this`, with static evidence for position/basis data, owner vehicle, mesh-part owner, wheel index, and context value. The body profiles with `rdtsc`, lazily initializes, resolves wheel tokens, samples heightfield normals, recurses through child wheel parts, and updates cached transforms. |
| `0x00494310` | `CMCBuggy__ProfileEnd` | Register-only profiling epilogue that reads `rdtsc`, indexes profiler buckets, accumulates elapsed cycles, and increments call counts. |
| `0x00494350` | `Mat34__InvertBasisToOut` | Owner-corrected from `CMCBuggy__InvertMatrix`; `RET 0x4` confirms one output-matrix stack argument after the ECX/source matrix pointer, and xrefs include CDXEngine, CMCBuggy, and other mesh/math callers. |
| `0x004944b0` | `Vec3__DivideInPlaceByScalar` | Owner-corrected from `CMCBuggy__DivideVector`; `RET 0x4` confirms one scalar stack argument after the ECX/vector pointer, and xrefs include CMeshPart, CMeshRenderer, CMCMech, CPDSimpleSprite, and Mat34. |
| `0x00494b00` | `CMeshPart__NameAvoidsBodyAxleWheelTokens` | Caller cleanup plus `RET` confirm one cdecl mesh-part argument. String read-back proves the rejected tokens are `Body`, `Axle`, and `Wheel`; the older `NameMatchesWheelTokenSet` label was backwards. |
| `0x00494b50` | `CMeshPart__HasWheelMotionAnimation` | One cdecl mesh-part argument from `[ESP+4]`; pushes `WheelMotion` (`0x0062cb54`) into `FindAnimationIndex` and returns true when the index is not `-1`. |
| `0x00494c60` | `CDestructableSegmentsMotionController__Ctor` | `RET 0x4` proves the earlier two-stack-argument signature was too wide. Installs vtable `0x005dc27c`, stores the supplied segment/controller pointer at `+0x0c`, and caches `+0x10+8` at `+0x08` when present. |
| `0x00494ca0` | `CDestructableSegmentsMotionController__ScalarDeletingDestructor` | Owner-corrected from the CMCBuggy wheel-specific label; vtable `0x005dc27c` slot `1`, one delete-flags stack argument, and conditional free wrapper behavior. |
| `0x00494cc0` | `CDestructableSegmentsMotionController__Destructor` | Owner-corrected from the CMCBuggy wheel-specific label; restores vtable `0x005dc27c`, clears `+0x08/+0x0c`, and tail-calls the base motion-controller destructor. The duplicated destructor-like body at `0x00497130` remains a separate follow-up. |
| `0x00494ce0` | `CDestructableSegmentsMotionController__ApplyRumbleTransform` | `RET 0x10`; four stack arguments after `this`. Vtable `0x005dc27c` slot `4`; samples a target/fallback value, accumulates per-segment state, applies trig rotation terms, writes Mat34 rows into the supplied transform, and clears the pointed source flag. |

Validation for Wave430: focused probe tests passed `4/4`; `npm run test:ghidra-cmcbuggy-wave430` passed after final read-back; Python compile passed; queue probe passed with `6043` total functions, `4326` commentless functions, `1833` undefined signatures, and `1792` `param_N` signatures. The first Wave430 apply/read-back caught the same Ghidra `__thiscall` hidden-`this` parameter nuance on the shared Mat34/Vec3 helpers; the script/probe were corrected and rerun serially before final read-back.

## Vtable Read-Back

Primary table `0x005dc250`:

| Slot | Address | Function |
| ---: | --- | --- |
| `1` | `0x00493080` | `CMCBuggy__scalar_deleting_destructor` |
| `4` | `0x004944d0` | Pointer target currently has no function object in the checked slot export. |
| `5` | `0x00494940` | Pointer target currently has no function object in the checked slot export. |
| `11+` | `0x005dc27c` | Nested/shared destructable-segment motion-controller table begins after the primary slots. |

Nested/shared table `0x005dc27c`:

| Slot | Address | Function |
| ---: | --- | --- |
| `1` | `0x00494ca0` | `CDestructableSegmentsMotionController__ScalarDeletingDestructor` |
| `4` | `0x00494ce0` | `CDestructableSegmentsMotionController__ApplyRumbleTransform` |
| `6` | `0x00494fa0` | `SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag` |
| `8` | `0x00495020` | `CMCBuggy__VFunc_GetUnitAIEntryTableRoot` |

## Wave354 UnitAI Indexed Entry / Motion Controller Boundary Tranche

Fresh vtable-slot read-back corrected three previously missing function starts in the `CMCBuggy` / `CMCHiveBoss` motion-controller neighborhood:

| Address | Current saved state | Notes |
| --- | --- | --- |
| `0x00494fa0` | `SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag` | Shared by `CMCBuggy` slot `17` and `CMCHiveBoss` slot `6`; updates output bit `0` through `CUnitAI__CanUseIndexedSegmentEntry`. |
| `0x00494ff0` | `SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10` | Shared by `CMCBuggy` slot `18` and `CMCHiveBoss` slot `7`; dispatches `CUnitAI__CallIndexedEntryVFunc10` when the state-context gate permits it. |
| `0x00495020` | `CMCBuggy__VFunc_GetUnitAIEntryTableRoot` | `CMCBuggy` slot `19` getter that follows the controller-owned entry-table root pointer. |

The wave also hardened `CUnitAI__CallIndexedEntryVFunc10` and `CUnitAI__CanUseIndexedSegmentEntry` to one `entryIndex` stack argument each. Runtime wheel, motion-controller, UnitAI, concrete layout, local/type, and rebuild parity remain unproven.

## Key Static Findings

- Wheel marker strings: `WheelBase` at `0x0062dca0`, `WheelMotion` at `0x0062cb54`, `Wheel` at `0x0062dcac`, `Axle` at `0x0062dcb4`, and `Body` at `0x0062dcbc`.
- Debug path string: `C:\dev\ONSLAUGHT2\MCBuggy.cpp` at `0x0062dc80`.
- Wheel arrays and transform buffers are dynamically allocated from the observed wheel-base count.
- Contact sentinels use `-1.0f` (`0xbf800000`).
- Profiling uses `rdtsc`; the saved comment records bucket accumulation under globals near `DAT_0082ce84` and `DAT_0082d054`.
- Wave456 corrected the shared base motion-controller helpers reached by the constructor/destructor: `CMotionController__ctor_base` writes vtable `0x005dc778` and clears `+0x04/+0x08`, while `CMotionController__dtor_base` restores the same vtable and tails `CMonitor__Shutdown`.

## Observed CMCBuggy Offsets

| Offset | Observed role |
| --- | --- |
| `+0x00` | Primary vtable pointer. |
| `+0x08` | Associated owner/model pointer. |
| `+0x0c/+0x10/+0x24/+0x28/+0x2c/+0x30/+0x34/+0x38` | Freed by the destructor when non-null; wheel/motion buffer ownership is static-only evidence. |
| `+0x18` | Observed wheel count. |
| `+0x1c/+0x20` | Wheel motion animation/frame metadata. |
| `+0x3c` | Seeded to `-1.0f` by the constructor. |
| `+0x40..+0xbc` | Transform/vector-like cached wheel/update data in the decompile. |
| `+0xc0` | Written by `CMCBuggy__SetFieldC0`; field purpose remains unproven. |
| `+0xc4` | Wheel motion cache/context pointer in current decompile. |

These are observed retail offsets, not complete structure definitions.

## Call Graph Notes

```
CMCBuggy__CMCBuggy
    -> CMotionController__ctor_base

CMCBuggy__destructor
    -> OID__FreeObject
    -> CMotionController__dtor_base

CMCBuggy__Init
    -> WheelBase / WheelMotion token lookups
    -> OID__AllocObject
    -> animation-frame sampling helpers

CMCBuggy__UpdateWheel
    -> CMCBuggy__Init
    -> heightfield/vector/matrix helpers
    -> CMeshPart__NameAvoidsBodyAxleWheelTokens
    -> CMeshPart__HasWheelMotionAnimation
    -> Mat34__InvertBasisToOut
    -> CMCBuggy__UpdateWheel

Mat34__InvertBasisToOut
    -> Vec3__DivideInPlaceByScalar

CDestructableSegmentsMotionController__ApplyRumbleTransform
    -> CMCBuggy__GetTargetValueOrFallback
    -> fcos/fsin rotation terms
    -> vector/matrix construction helpers
```

## Additional Utility Promotions

| Address | Name | Purpose |
| --- | --- | --- |
| `0x004956a0` | `Mat34__Add` | 3x4 matrix add helper (`dst = lhs + rhs`) used across mech/mesh update paths. |
| `0x00495e00` | `Mat34__Subtract` | 3x4 matrix subtract helper (`dst = lhs - rhs`) used across mech/mesh update paths. |

These two helpers were previously weak `CMCBuggy__Unk_*` symbols and were promoted by behavior-level decompile evidence plus multi-caller xref usage outside buggy-only paths.
