# Tentacle.cpp Functions

> Source File: Tentacle.cpp | Binary: BEA.exe
> Debug Path: `0x00632ccc`
> Current evidence: Wave515 saved Ghidra read-back on 2026-05-17

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

CTentacle is a boss enemy class representing the giant mechanical tentacles that emerge from the ground/water. This file contains factory methods for creating tentacle-related components including the visual guide, AI controller, and integration with the Warspite battleship boss.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| `0x004f0760` | `CTentacle__CreateTentacleGuide` | Allocate a CTentacle guide / motion-controller component and store it at `this+0x70` | ~128 bytes |
| `0x004f07e0` | `CTentacle__CreateTentacleAI` | Allocate a CTentacleAI controller and store it at `this+0x208` | ~128 bytes |
| `0x004f0860` | `CTentacle__CreateWarspiteAI` | Allocate a Warspite-style AI component and store it at `this+0x13c` | ~128 bytes |
| `0x004f08f0` | `CTentacleAI__scalar_deleting_dtor` | Vtable slot-1 scalar deleting destructor wrapper | ~32 bytes |
| `0x004f0910` | `CTentacleAI__dtor_base` | Destructor-base cleanup body that tears down CUnitAI-style linked reader cells | ~160 bytes |

Wave768 static read-back (`unwind-continuation-wave768`, `wave768-readback-verified`) hardened the adjacent Tentacle.cpp unwind cleanup callbacks as `void __cdecl Unwind@...(void)`. Exact anchors include `0x005d5050 Unwind@005d5050`, `0x005d50b0 Unwind@005d50b0`, and `0x005d50e0 Unwind@005d50e0`. Evidence includes DATA scope-table xrefs `0x0061d8cc` through `0x0061d97c`, Tentacle.cpp debug path `0x00632ccc`, three `OID__FreeObject_Callback` rows, monitor shutdown, two active-reader destructors, and particle-list cleanup. Verified backup: `G:\GhidraBackups\BEA_20260523-171555_post_wave768_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

Wave1009 (`geometry-guide-heightfield-spine-review-wave1009`) recovered `0x004f0e40 CTentacle__VFunc_22_004f0e40` as a DATA-backed CTentacle static-shadow caller boundary. Queue closure is `6233/6233 = 100.00%`; verified backup: `G:\GhidraBackups\BEA_20260531-155648_post_wave1009_geometry_guide_heightfield_spine_review_verified`. Runtime tentacle activation/effect behavior, exact source virtual name, concrete layouts, BEA patching, and rebuild parity remain separate proof.

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d5050 | Unwind@005d5050 | 0x2f (47) | Cleanup for CTentacleGuide allocation |
| 0x005d5070 | Unwind@005d5070 | 0x35 (53) | Cleanup for CTentacleAI allocation |
| 0x005d5090 | Unwind@005d5090 | 0x3c (60) | Cleanup for CWarspiteAI allocation |

## Key Observations

- **Pool ID 0x1b (27)** - CTentacleGuide uses memory pool 27, object size 0xEC (236) bytes
- **Pool ID 0x17 (23)** - CTentacleAI and CWarspiteAI both use memory pool 23
- **Component storage offsets**:
  - CTentacleGuide stored at `this+0x70` (offset 112)
  - CTentacleAI stored at `this+0x208` (offset 520)
  - CWarspiteAI stored at `this+0x13c` (offset 316)
- **Factory table at 0x005e4170** - Function pointers referenced by vtable-like structure

## Class Relationships

```
CTentacle (main boss class)
  +0x70  -> CTentacleGuide  (visual/animation component, 236 bytes)
  +0x13c -> CWarspiteAI     (combat AI, 96 bytes)
  +0x208 -> CTentacleAI     (tentacle-specific AI, 32 bytes)
```

## RTTI Strings

| Address | String | Class |
|---------|--------|-------|
| 0x0063d968 | `.?AVCTentacle@@` | Main tentacle class |
| 0x00632cf8 | `.?AVCTentacleGuide@@` | Visual guide component |
| 0x00632d18 | `.?AVCTentacleAI@@` | AI controller |
| 0x00627968 | `.?AVCComponentTentacle@@` | Component base class |
| 0x0062dfe0 | `.?AVCMCTentacle@@` | Motion controller |

## VTables

| Address | Class | Notes |
|---------|-------|-------|
| 0x005df46c | CTentacleAI | Set in CreateTentacleAI |
| 0x005df498 | CWarspiteAI | Set in CreateWarspiteAI |
| 0x005dc450 | CTentacleGuide | Set via FUN_0049cad0 initializer |

## Debug Strings

- `"tentacle"` at 0x0062e02c
- `"Got %d bones in tentacle\n"` at 0x0062e048
- `"Tentacle Activation Effect"` at 0x00632d38

## Memory Allocation Pattern

All three functions follow the same pattern:
1. Call `OID__AllocObject(size, pool_id, debug_path, line_number)` to allocate
2. If allocation succeeds, initialize component via constructor
3. Set vtable pointer on the new object
4. Store component pointer at appropriate offset in parent CTentacle
5. If allocation fails, store NULL at the offset

## Wave515 Static Read-Back (2026-05-17)

Wave515 hardened the three CTentacle factory signatures and corrected the adjacent CTentacleAI destructor pair:

```cpp
void __fastcall CTentacle__CreateTentacleGuide(void * this);
void __fastcall CTentacle__CreateTentacleAI(void * this);
void __thiscall CTentacle__CreateWarspiteAI(void * this, void * init_context);
void * __thiscall CTentacleAI__scalar_deleting_dtor(void * this, byte delete_flags);
void __fastcall CTentacleAI__dtor_base(void * this);
```

The three factory entries are referenced from table data at `0x005e4170`, `0x005e4174`, and `0x005e4178`. The scalar deleting destructor is referenced from CTentacleAI vtable data at `0x005df49c` and calls the adjacent destructor-base body before optional free. The destructor-base body is structurally identical to the saved `CUnitAI__dtor_base` cleanup pattern, but this copy is emitted in the Tentacle.cpp cluster and is only reached from the CTentacleAI scalar deleting destructor in current xrefs.

Evidence lives in `release/readiness/ghidra_tentacle_ai_wave515_2026-05-17.md`. Runtime tentacle behavior, runtime AI behavior, exact source-body identity, concrete layouts, and rebuild parity remain unproven.

## Related Files

- Warspite.cpp - Naval AI (CWarspite__Init called from CreateWarspiteAI)
- MCTentacle.cpp - Motion controller (debug path at 0x0062e06c)
- Unit.cpp - Base unit class

---
*Discovered via Phase 1 xref analysis (Dec 2025); Wave515 read-back refreshed on 2026-05-17*
