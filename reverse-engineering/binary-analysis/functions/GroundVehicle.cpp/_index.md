# GroundVehicle.cpp Functions

> Source File: GroundVehicle.cpp | Binary: BEA.exe
> Debug Path: 0x0062cb30

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Ground vehicle implementation. Current retail Ghidra read-back shows `CGroundVehicle` calling `CGroundUnit__Init`, resolving `WheelMotion`, allocating/initializing guide and motion-controller state, and owning vtable-slot firing-animation helpers. It inherits from `CGroundUnit`. This page records saved retail-binary evidence and does not prove runtime movement, wheel-motion, animation playback, or complete source parity.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0047cfd0 | CGroundVehicle__Init | Initialize ground-vehicle state, call `CGroundUnit__Init`, resolve `WheelMotion`, and allocate guide/component/controller state | ~400 bytes |
| 0x0047d3b0 | CMonitor__TryQueuePrefireAnimation | `CGroundVehicle` vtable slot `86`; update deploy/charge state, validate `prefire`, and dispatch animation vfunc `+0xf0` when present | ~110 bytes |
| 0x0047d420 | CUnitAI__QueueFiringOrPostfireAnimation | `CGroundVehicle` vtable slot `87`; choose `firing` versus `postfire`, validate the animation token, and dispatch vfunc `+0xf0` | ~120 bytes |
| 0x0047d590 | CGroundVehicleGuide__Constructor | Install `CGroundVehicleGuide` vtable and allocate guide-owned buffers | ~190 bytes |
| 0x0047d650 | CGroundVehicleGuide__ScalarDeletingDestructor | Scalar-deleting destructor wrapper for `CGroundVehicleGuide` vtable slot `1` | ~30 bytes |
| 0x0047d6d0 | CGroundVehicleGuide__Destructor | Restore guide/base cleanup state and release owned linked objects | ~80 bytes |
| 0x0047d750 | CGroundVehicleGuide__VFunc03_UpdateGuidanceState_0047d750 | Wave1077 CGroundVehicleGuide vtable slot-3 guidance/update-state boundary recovered from DATA-backed vtable evidence | ~1180 bytes |
| 0x00496a50 | CMCGroundVehicle__Constructor | Install `CMCGroundVehicle` vtable and initialize controller fields for a ground-vehicle owner | ~50 bytes |
| 0x00496a80 | CMCGroundVehicle__ScalarDeletingDestructor | Scalar-deleting destructor wrapper for `CMCGroundVehicle` vtable slot `1` | ~30 bytes |
| 0x00496aa0 | CMCGroundVehicle__Destructor | Restore controller/base cleanup state and clear target ownership | ~40 bytes |

## Exception Handlers

| Address | Name | Debug line / allocation type | Purpose |
|---------|------|------|---------|
| 0x005d2bd0 | Unwind@005d2bd0 | line `0x1b`, type `0x1c` | Wave752 allocation cleanup for `*(EBP+0x4)` through `OID__FreeObject_Callback`. |
| 0x005d2be6 | Unwind@005d2be6 | line `0x1b`, type `0x21` | Wave752 allocation cleanup for `*(EBP+0x4)` through `OID__FreeObject_Callback`. |
| 0x005d2bfc | Unwind@005d2bfc | line `0x17`, type `0x23` | Wave752 allocation cleanup for `*(EBP+0x4)` through `OID__FreeObject_Callback`. |
| 0x005d2c12 | Unwind@005d2c12 | line `0x16`, type `0x25` | Wave752 allocation cleanup for `*(EBP+0x4)` through `OID__FreeObject_Callback`. |
| 0x005d2c40 | Unwind@005d2c40 | scope-table cleanup | Wave752 monitor cleanup through `CMonitor__Shutdown_Thunk` on `*(EBP-0x10)`. |

Wave752 saved the GroundVehicle.cpp rows above with `unwind-continuation-wave752` and `wave752-readback-verified` tags. Anchor rows include `0x005d2bd0 Unwind@005d2bd0` and `0x005d2c40 Unwind@005d2c40`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-212829_post_wave752_unwind_continuation_verified`. These rows are static retail Ghidra evidence only; exact parent source-body identity, runtime ground-vehicle cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Key Observations

- **WheelMotion** - References "WheelMotion" string at 0x0062cb54
- **Inherits CGroundUnit** - Calls CGroundUnit__Init (0x0047c730) as parent
- **Multiple components** - Creates objects at +0x70, +0x208, +0x13c, +0x260
- **Four allocations** - Wave752 read-back distinguishes source debug-line pushes (`0x1b`, `0x1b`, `0x17`, `0x16`) from allocation/type values (`0x1c`, `0x21`, `0x23`, `0x25`) for the corresponding unwind handlers.
- **Guide component** - Wave 392 read-back maps the `+0x208` guide path to `CGroundVehicleGuide__Constructor` and the `0x005dbd90` RTTI/vtable. Wave1077 (`infantryguide-lifecycle-review-wave1077`) recovered `0x0047d750 CGroundVehicleGuide__VFunc03_UpdateGuidanceState_0047d750` for vtable slot `3` and confirmed slots `4` through `8` share `0x0047e2d0 SharedGuide__VFunc04_SetVectorMode1_0047e2d0`, `0x0047e310 SharedGuide__VFunc05_SetVectorMode2_0047e310`, `0x0047e340 SharedGuide__VFunc06_SetVectorMode3_0047e340`, `0x0047e370 SharedGuide__VFunc07_SetVectorModeFromOwnerState_0047e370`, and `0x0047e3d0 SharedGuide__VFunc08_ResetVectorsFromOwner_0047e3d0` with CInfantryGuide vtable `0x005dbfa8`. Queue closure is `6260/6260 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface is `1371/1560 = 87.88%`; top-500 remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-073929_post_wave1077_infantryguide_lifecycle_review_verified`.
- **Motion controller component** - Wave 392 read-back maps the `+0x13c` controller path to `CMCGroundVehicle__Constructor` and the `0x005dc35c` RTTI/vtable.
- **Firing animation slots** - Wave 393 read-back maps `CGroundVehicle` vtable slot `86` to the `prefire` queue helper and slot `87` to the `firing` / `postfire` queue helper.
- **Current boundary** - Runtime ground-vehicle driving, guide, wheel-motion, animation playback, component behavior, concrete layouts, locals/types, exact source identities, and rebuild parity remain unproven.

## Class Hierarchy

```
CUnit
  └── CGroundUnit
        └── CGroundVehicle
```

## Related Files

- GroundUnit.cpp - CGroundUnit parent class
- Unit.cpp - CUnit base class

---
*Discovered via Phase 1 xref analysis (Dec 2025); updated with Wave 392 guide/controller evidence and Wave 393 firing-animation vtable-slot evidence (2026-05-14).*
