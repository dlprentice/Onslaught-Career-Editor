# SphereTrigger.cpp Functions

> Source File: SphereTrigger.cpp | Binary: BEA.exe
> Debug Path: 0x0063270c (`[maintainer-local-source-export-root]\SphereTrigger.cpp`)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

CSphereTrigger implements volume-based triggers that fire when objects enter or collide with a spherical region. Used for triggering events, cutscenes, objectives, and scripted sequences during gameplay.

The trigger system works by:
1. Maintaining a list of objects currently within the sphere
2. Recording active/hit objects that enter the sphere
3. Firing the associated effect/event when triggered
4. Spawning a "Sphere_Trigger_Effect" particle when activated

## Wave1170 Actor-Derived Lifecycle Cleanup Review

Wave1170 (`wave1170-actor-derived-lifecycle-cleanup-current-risk-review`) re-read `CSphereTrigger__scalar_deleting_dtor` and `CSphereTrigger__dtor_base` inside `6 actor-derived lifecycle cleanup current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. Fresh Ghidra export evidence verified the scalar-deleting wrapper DATA vtable xref and the base destructor path that clears `CSPtrSet` at `+0x8c`, removes the `+0x7c` particle/global-list node, and delegates to `CComplexThing__dtor_base`. This was a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-062008_post_wave1170_actor_derived_lifecycle_cleanup_current_risk_review_verified`.

Runtime sphere-trigger cleanup behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1170; wave1170-actor-derived-lifecycle-cleanup-current-risk-review; 666/1179 = 56.49%; 6 actor-derived lifecycle cleanup current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 513; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 6 xref rows; 100 instruction rows; CRocket__scalar_deleting_dtor; CSphereTrigger__scalar_deleting_dtor; CEscapePod__scalar_deleting_dtor; CRocket__dtor_base; CSphereTrigger__dtor_base; CEscapePod__dtor_base; Wave459; Wave460; Wave1022; [maintainer-local-ghidra-backup-root]\BEA_20260606-062008_post_wave1170_actor_derived_lifecycle_cleanup_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Wave1022 Object-Lifecycle Destructor Review

Wave1022 (`object-lifecycle-dtor-review-wave1022`) re-read `0x004bff40 CSphereTrigger__dtor_base` as part of the adjacent destructor strip. The row still reads back as `void __fastcall CSphereTrigger__dtor_base(void * this)`; static evidence keeps it as the body called by `CSphereTrigger__scalar_deleting_dtor`, clearing the `+0x8c` `CSPtrSet`, removing the `+0x7c` particle/global-list node through `CParticleManager__RemoveFromGlobalList`, and delegating to `CComplexThing__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified`.

Probe token anchor: Wave1022; object-lifecycle-dtor-review-wave1022; 0x004bff40 CSphereTrigger__dtor_base; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified.

Runtime sphere-trigger cleanup behavior, exact tracked-set layout, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004e5540 | CSphereTrigger__OnTriggered | Fires trigger effect and spawns particle | ~313 bytes |
| 0x004e5700 | CSphereTrigger__Hit | Hit/contact override - records active objects in sphere | ~315 bytes |

## Wave505 Read-Back Status

Wave505 saved signatures/comments/tags for both known `CSphereTrigger` helpers on 2026-05-17. The pass keeps `0x004e5540` as `CSphereTrigger__OnTriggered` and corrects `0x004e5700` from stale `CSphereTrigger__Update` to `CSphereTrigger__Hit`, because the body calls `CComplexThing__Hit(this, other_thing, collision_report)` before recording the active object reader.

Verification artifacts live under `subagents/ghidra-static-reaudit/wave505-spawnpoint-trigger-004e43d0/`. The Wave505 apply script reported clean dry/apply/final-verify runs, post exports verified `6` metadata rows, `6` tag rows, `7` xref rows, `726` instruction rows, and `6` decompile exports across the whole spawn-point/sphere-trigger tranche, and both direct and npm probes passed. Backup `[maintainer-local-ghidra-backup-root]\BEA_20260517-154500_post_wave505_spawnpoint_spheretrigger_verified` verified `19` files, `158010247` bytes, and zero missing/extra/hash-diff files.

Not proven by Wave505: exact `CSphereTrigger`, monitor/list, particle-effect, or collision-report layouts; runtime trigger behavior; BEA launch behavior; game patching; or rebuild parity.

## Wave766 Unwind Continuation

Wave766 static read-back (`unwind-continuation-wave766`, `wave766-readback-verified`) saved comments/tags/signatures for SphereTrigger.cpp-adjacent compiler-generated unwind cleanup callbacks from `0x005d4c50 Unwind@005d4c50` through `0x005d4d06 Unwind@005d4d06`. Evidence includes DATA scope-table xrefs `0x0061d4d4` through `0x0061d5b4`, SphereTrigger.cpp debug path `0x0063270c`, active-reader destructor callbacks, monitor shutdown callbacks, particle-list cleanup, CLine stack-local cleanup, and the `0x005d4cf0 Unwind@005d4cf0` allocation-free row. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-161835_post_wave766_unwind_continuation_verified`.

| Address | Evidence |
| --- | --- |
| 0x005d4c50 | `CGenericActiveReader__dtor(*(EBP-0x10))`; DATA xref `0x0061d4d4`. |
| 0x005d4c70 | `CMonitor__Shutdown(*(EBP-0x10))`; DATA xref `0x0061d4fc`. |
| 0x005d4c78 | `CGenericActiveReader__dtor((*(EBP-0x10))+0x08)`; DATA xref `0x0061d504`. |
| 0x005d4cb0 | `CParticleManager__RemoveFromGlobalList_Thunk(EBP-0x14)`; DATA xref `0x0061d55c`. |
| 0x005d4cd0 | `CLine__SetBaseVtable_00426360(EBP-0x2c)`; DATA xref `0x0061d584`. |
| 0x005d4cf0 | `OID__FreeObject_Callback(*(EBP+0x8))` with line token `0x53` and allocation/type value `0x5b`; DATA xref `0x0061d5ac`. |
| 0x005d4d06 | `CGenericActiveReader__dtor(*(EBP+0x8))`; DATA xref `0x0061d5b4`. |

This is saved static retail Ghidra evidence only. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Function Details

### CSphereTrigger__OnTriggered (0x004e5540)

**Purpose:** Called when an object enters the trigger sphere. Spawns the visual "Sphere_Trigger_Effect" particle and updates the triggered object's position data.

**Key Operations:**
- Calls virtual function at vtable+0x68 to validate trigger
- Spawns "Sphere_Trigger_Effect" particle via `CParticleManager__CreateEffect`
- Updates triggered object's position vectors (current, previous, target)
- Handles position interpolation for smooth transitions

**Saved Signature:**
```cpp
void __fastcall CSphereTrigger__OnTriggered(void * this);
```

**String References:**
- `"Sphere_Trigger_Effect"` at 0x006326f4

**Called Functions:**
- `FUN_004cb0b0` - Setup/preparation
- `FUN_004cd7a0` - Effect name lookup
- `CParticleManager__CreateEffect` at 0x004cb3d0

---

### CSphereTrigger__Hit (0x004e5700)

**Purpose:** Hit/contact override. Records active objects that contact the trigger sphere and keeps monitored reader cells so stale object references can be cleared safely.

**Key Operations:**
- Calls parent/base hit handling via `CComplexThing__Hit(this, other_thing, collision_report)`
- Checks flag at `other_thing+0x34` (bit `0x10`) to see if the contacting object is active
- Compares cached timestamp at this+0x88 against global time
- Iterates through object list using iterator pattern
- Uses monitor.h / ActiveReader deletion tracking for safe references (allocates `CSPtrSet` at `monitor+0x04` when needed; see `reverse-engineering/binary-analysis/functions/monitor.h/_index.md`)
- Manages SPtrSet linked list for object tracking

**Saved Signature:**
```cpp
void __thiscall CSphereTrigger__Hit(void * this, void * other_thing, void * collision_report);
```

**String References:**
- Debug path `"[maintainer-local-source-export-root]\SphereTrigger.cpp"` at 0x0063270c (line 0x53 = 83)
- `"[maintainer-local-source-export-root]\monitor.h"` at 0x0062551c (line 0x18 = 24)

**Called Functions:**
- `CComplexThing__Hit` - Base/source-parity hit handler
- `CSPtrSet__First` / `CSPtrSet__Next` - Iterator begin/next
- `CGenericActiveReader__dtor` (0x0044b1d0) - Unregister active reader from monitored object's deletion list (used before free)
- `OID__FreeObject` - Memory deallocation (frees temp objects)
- `CSPtrSet__Clear` - Clear trigger list (SPtrSet::Clear; returns nodes to pool)
- `OID__AllocObject` - Memory allocation (new operator)
- `CSPtrSet__Init` - Initialize empty set (head/tail/count = 0)
- `CSPtrSet__AddToHead` - Add entry to head of list
- `CSPtrSet__AddToTail` - Add entry to tail of list

## Related Classes

### SPtrSet (Smart Pointer Set)

The trigger uses SPtrSet for managing the list of objects within the sphere:

| Address | Function | Purpose |
|---------|----------|---------|
| 0x004e5840 | CSPtrSet__Init | Constructor-like init (mFirst/mLast/mSize = 0; mIterator untouched) |
| 0x004e5a80 | CSPtrSet__AddToHead | Add to head of list |
| 0x004e5b20 | CSPtrSet__AddToTail | Add to tail of list |
| 0x004e5c60 | CSPtrSet__Clear | Clear set and return nodes to pool |

**Note:** These functions are `SPtrSet.cpp` utilities (debug-path xref at 0x00632730), not SphereTrigger.cpp.

## Class Layout (Partial)

```cpp
class CSphereTrigger : public CTrigger {
    // Inherited from CTrigger...

    // +0x1C: Vector3 position (16 bytes)
    // +0x7C: Particle effect data
    // +0x80: Associated object pointer
    // +0x88: float lastUpdateTime (cached timestamp)
    // +0x8C: SPtrSet objectsInSphere (linked list of objects)
};
```

## Key Observations

1. **Trigger Validation:** Uses virtual function at vtable+0x68 to check if trigger should fire
2. **Time-Based Caching:** Stores timestamp at offset 0x88 to avoid redundant updates in same frame
3. **Memory Management:** Uses `OID__AllocObject`/`OID__FreeObject` with debug file/line strings for allocations (including `monitor.h`)
4. **Particle Effect:** Always spawns "Sphere_Trigger_Effect" when triggered - visual feedback
5. **Position Tracking:** Updates triggered object's position in multiple buffers (current, previous, interpolated)
6. **Exception Handling:** Update function has SEH exception handler for robustness

## Global Data References

| Address | Type | Purpose |
|---------|------|---------|
| 0x00672fd0 | float | Global game time / timestamp |
| 0x0083d120-0x0083d12c | float[4] | Default particle effect parameters |
| 0x009c3df0 | object | Global memory manager instance |
| 0x009c63e8 | object | Global particle manager instance |
| 0x0082b400 | object | Effect name lookup table |

## Usage Context

SphereTriggers are placed in levels by designers to:
- Trigger objective completion when player reaches location
- Start cutscenes or scripted events
- Spawn enemies when player enters an area
- Activate/deactivate game elements
- Trigger audio/visual effects

The trigger records active objects that contact the sphere and fires once per object entry through its trigger/effect path.

---
*Discovered via Phase 1 xref analysis (Dec 2025). Wave505 refreshed/corrected signatures and stale `CSphereTrigger__Update` naming on 2026-05-17.*
